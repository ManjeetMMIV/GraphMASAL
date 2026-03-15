from __future__ import annotations

import os
import logging
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Any


class StructureAwareReranker:
    def __init__(self, conn, use_cross_encoder: bool = False, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.conn = conn
        self.use_cross_encoder = use_cross_encoder
        self.model_name = model_name
        self._cross_encoder = None

    def _load_cross_encoder(self):
        if not self.use_cross_encoder:
            return None

        if self._cross_encoder is None:
            from sentence_transformers import CrossEncoder

            verbose = os.getenv("GRAPHMASAL_VERBOSE_RETRIEVAL", "0").strip().lower() in {"1", "true", "yes", "on"}
            if not verbose:
                logging.getLogger("transformers").setLevel(logging.ERROR)
                logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
                with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                    self._cross_encoder = CrossEncoder(self.model_name)
                return self._cross_encoder

            self._cross_encoder = CrossEncoder(self.model_name)
        return self._cross_encoder

    def _get_graph_context(self, concept_id: str, student_id: str) -> dict[str, Any]:
        query = """
        MATCH (concept:Concept {id: $concept_id})
        OPTIONAL MATCH (prereq:Concept)-[:IS_PREREQUISITE_FOR]->(concept)
        OPTIONAL MATCH (concept)-[:IS_PREREQUISITE_FOR]->(next_concept:Concept)
        OPTIONAL MATCH (student:Student {id: $student_id})-[mastery:HAS_MASTERY_OF]->(prereq)
        RETURN collect(DISTINCT prereq.name) AS prerequisites,
               collect(DISTINCT next_concept.name) AS unlocks,
               count(DISTINCT prereq) AS prerequisite_count,
               count(DISTINCT next_concept) AS unlock_count,
               avg(COALESCE(mastery.score, 0.0)) AS prerequisite_mastery
        """

        records = self.conn.query(query, {"concept_id": concept_id, "student_id": student_id})
        if not records:
            return {
                "prerequisites": [],
                "unlocks": [],
                "prerequisite_count": 0,
                "unlock_count": 0,
                "prerequisite_mastery": 0.0,
            }

        record = records[0]
        return {
            "prerequisites": [item for item in record["prerequisites"] if item],
            "unlocks": [item for item in record["unlocks"] if item],
            "prerequisite_count": int(record["prerequisite_count"] or 0),
            "unlock_count": int(record["unlock_count"] or 0),
            "prerequisite_mastery": float(record["prerequisite_mastery"] or 0.0),
        }

    def _cross_encoder_score(self, query_text: str, candidate: dict[str, Any], context: dict[str, Any]) -> float:
        model = self._load_cross_encoder()
        if model is None:
            return 0.0

        context_text = (
            f"Concept: {candidate['name']}. "
            f"Description: {candidate['description']}. "
            f"Prerequisites: {', '.join(context['prerequisites']) or 'None'}. "
            f"Unlocks: {', '.join(context['unlocks']) or 'None'}."
        )
        score = model.predict([(query_text, context_text)])[0]
        return 1.0 / (1.0 + pow(2.718281828, -float(score)))

    def rerank(self, query_text: str, student_id: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        reranked: list[dict[str, Any]] = []

        max_similarity = max((candidate["similarity"] for candidate in candidates), default=1.0) or 1.0

        for candidate in candidates:
            context = self._get_graph_context(candidate["concept_id"], student_id)
            normalized_similarity = candidate["similarity"] / max_similarity
            mastery_gap = 1.0 - candidate["mastery"]
            frontier_alignment = (0.6 * context["prerequisite_mastery"]) + (0.4 * mastery_gap)
            structural_value = min(context["unlock_count"], 5) / 5.0
            cross_encoder_score = self._cross_encoder_score(query_text, candidate, context)

            final_score = (
                0.45 * normalized_similarity
                + 0.25 * frontier_alignment
                + 0.10 * structural_value
                + 0.20 * cross_encoder_score
            )

            enriched_candidate = dict(candidate)
            enriched_candidate.update(
                {
                    "graph_context": context,
                    "rerank_score": final_score,
                    "cross_encoder_score": cross_encoder_score,
                }
            )
            reranked.append(enriched_candidate)

        reranked.sort(key=lambda item: item["rerank_score"], reverse=True)
        return reranked