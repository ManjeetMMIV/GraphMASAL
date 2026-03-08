import os
from dotenv import load_dotenv
from src.graph.db import Neo4jConnection
from sentence_transformers import SentenceTransformer

class SemanticSearch:
    def __init__(self, conn: Neo4jConnection, model_name: str = 'all-MiniLM-L6-v2'):
        self.conn = conn
        print("Loading HuggingFace model for search...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully.")
    
    def search_and_personalize(self, query_text: str, student_id: str, top_k: int = 3):
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
        
        final_results = []
        for record in results:
            final_results.append({
                "concept": record["name"],
                "similarity": record["similarity"],
                "mastery": record["mastery_score"]
            })
            
        return final_results

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
