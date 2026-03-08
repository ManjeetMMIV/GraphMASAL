import os
from dotenv import load_dotenv
from src.graph.db import Neo4jConnection
from sentence_transformers import SentenceTransformer

class ConceptEmbedder:
    def __init__(self, conn: Neo4jConnection, model_name: str = 'all-MiniLM-L6-v2'):
        self.conn = conn
        print(f"Loading HuggingFace model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully.")

    def embed_all_concepts(self):
        # Retrieve all concepts to generate embeddings
        query = "MATCH (c:Concept) RETURN c.id AS id, c.description AS description, c.name AS name"
        results = self.conn.query(query)
        
        if not results:
            print("No concepts found in the database.")
            return

        print(f"Generating embeddings for {len(results)} concepts...")
        for record in results:
            concept_id = record["id"]
            description = record["description"]
            
            # Create embedding from description
            # Convert to list of floats for Neo4j
            embedding = self.model.encode(description).tolist()
            
            # Update the concept node with the embedding
            update_query = """
            MATCH (c:Concept {id: $id})
            SET c.embedding = $embedding
            """
            self.conn.query(update_query, parameters={"id": concept_id, "embedding": embedding})
            print(f"Updated embedding for Concept: {record['name']}")
        
        print("Finished generating concept embeddings.")

if __name__ == "__main__":
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")

    if uri and user and pwd:
        conn = Neo4jConnection(uri, user, pwd)
        embedder = ConceptEmbedder(conn)
        embedder.embed_all_concepts()
        conn.close()
    else:
        print("Neo4j configuration is missing.")
