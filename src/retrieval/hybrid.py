from __future__ import annotations

from src.graph.db import Neo4jConnection
from src.retrieval.search import SemanticSearch


class HybridRetriever:
    def __init__(self, conn: Neo4jConnection, use_cross_encoder: bool = False):
        self.conn = conn
        self.semantic_search = SemanticSearch(conn, use_cross_encoder=use_cross_encoder)

    def _get_graph_neighborhood(self, concept_id: str, hops: int = 2) -> dict[str, list[str]]:
        hops = max(1, min(hops, 2))
        query = f"""
        MATCH (center:Concept {{id: $concept_id}})
        OPTIONAL MATCH (prereq:Concept)-[:IS_PREREQUISITE_FOR*1..{hops}]->(center)
        OPTIONAL MATCH (center)-[:IS_PREREQUISITE_FOR*1..{hops}]->(downstream:Concept)
        RETURN collect(DISTINCT prereq.name) AS prerequisites,
               collect(DISTINCT downstream.name) AS downstream
        """
        records = self.conn.query(query, {"concept_id": concept_id})
        if not records:
            return {"prerequisites": [], "downstream": []}

        record = records[0]
        return {
            "prerequisites": [item for item in record["prerequisites"] if item],
            "downstream": [item for item in record["downstream"] if item],
        }

    def retrieve(self, query_text: str, student_id: str, top_k: int = 3, seed_k: int = 5) -> list[dict]:
        vector_results = self.semantic_search.search_and_personalize(query_text, student_id, top_k=seed_k)
        hybrid_results = []

        for result in vector_results:
            neighborhood = self._get_graph_neighborhood(result["concept_id"])
            prereq_richness = min(len(neighborhood["prerequisites"]), 3) / 3.0
            downstream_richness = min(len(neighborhood["downstream"]), 3) / 3.0
            structural_richness = 0.5 * prereq_richness + 0.5 * downstream_richness

            base_score = result.get("rerank_score", result["similarity"])
            hybrid_score = 0.85 * base_score + 0.15 * (base_score * structural_richness)

            enriched = dict(result)
            enriched["hybrid_score"] = hybrid_score
            enriched["graph_neighborhood"] = neighborhood
            hybrid_results.append(enriched)

        hybrid_results.sort(key=lambda item: item["hybrid_score"], reverse=True)
        return hybrid_results[:top_k]