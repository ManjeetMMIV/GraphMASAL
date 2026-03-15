import os
import logging
from contextlib import redirect_stderr
from contextlib import redirect_stdout
from functools import lru_cache
from io import StringIO

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from src.graph.db import Neo4jConnection
from src.retrieval.reranker import StructureAwareReranker


def _verbose_retrieval() -> bool:
    return os.getenv("GRAPHMASAL_VERBOSE_RETRIEVAL", "0").strip().lower() in {"1", "true", "yes", "on"}


def _quiet_hf_load_noise() -> None:
    logging.getLogger("transformers").setLevel(logging.ERROR)
    logging.getLogger("sentence_transformers").setLevel(logging.ERROR)


@lru_cache(maxsize=2)
def _get_sentence_transformer(model_name: str) -> SentenceTransformer:
    verbose = _verbose_retrieval()
    if verbose:
        print(f"Loading HuggingFace model for search: {model_name}...")

    # Keep first-load model diagnostics quiet unless explicitly requested.
    if verbose:
        model = SentenceTransformer(model_name)
    else:
        _quiet_hf_load_noise()
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            model = SentenceTransformer(model_name)

    if verbose:
        print("Model loaded successfully.")
    return model

class SemanticSearch:
    def __init__(self, conn: Neo4jConnection, model_name: str = 'all-MiniLM-L6-v2', use_cross_encoder: bool = False):
        self.conn = conn
        self.model = _get_sentence_transformer(model_name)
        self.reranker = StructureAwareReranker(conn, use_cross_encoder=use_cross_encoder)
    
    def search_and_personalize(self, query_text: str, student_id: str, top_k: int = 3):
        if _verbose_retrieval():
            print(f"Embedding query: '{query_text}'")
        query_embedding = self.model.encode(query_text).tolist()
        
        # We query the vector index and simultaneously match the student's mastery IF it exists
        cypher_query = """
        CALL db.index.vector.queryNodes('concept_embedding', $top_k, $embedding)
        YIELD node AS concept, score AS similarity
        OPTIONAL MATCH (s:Student {id: $student_id})-[r:HAS_MASTERY_OF]->(concept)
        RETURN concept.id AS concept_id, 
               concept.name AS name, 
               concept.description AS description, 
               similarity, 
               COALESCE(r.score, 0.0) AS mastery_score
        """
        
        parameters = {
            "embedding": query_embedding,
            "top_k": top_k,
            "student_id": student_id
        }
        
        results = self.conn.query(cypher_query, parameters)
        
        candidates = []
        if results:
            for record in results:
                candidates.append({
                    "concept_id": record["concept_id"],
                    "concept": record["name"],
                    "name": record["name"],
                    "description": record["description"],
                    "similarity": record["similarity"],
                    "mastery": record["mastery_score"]
                })

        if not candidates:
            return []

        reranked = self.reranker.rerank(query_text, student_id, candidates)
        return reranked[:top_k]

if __name__ == "__main__":
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")

    if uri and user and pwd:
        conn = Neo4jConnection(uri, user, pwd)
        finder = SemanticSearch(conn)
        
        test_query = "How does the OS manage files?"
        student_id = "student_123" # Alice
        
        print("\n--- Search Results ---")
        results = finder.search_and_personalize(test_query, student_id)
        for r in results:
            print(f"Concept: {r['concept']} | Similarity: {r['similarity']:.4f} | Mastery: {r['mastery']:.2f}")
            
        conn.close()
    else:
        print("Neo4j configuration is missing.")
