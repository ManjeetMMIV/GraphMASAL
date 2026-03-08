import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Get Aura credentials from .env
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, pwd))
            print("Successfully connected to Neo4j instance.")
        except Exception as e:
            print(f"Failed to create the driver: {e}")

    def close(self):
        if self.driver is not None:
            self.driver.close()
            print("Neo4j connection closed.")

    def query(self, query, parameters=None, db=None):
        assert self.driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.driver.session(database=db) if db else self.driver.session() 
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

    def initialize_schema(self):
        """Creates indexes and constraints for the Knowledge Graph."""
        print("Initializing schema constraints...")
        
        # We need concepts to have unique names
        concept_constraint_query = "CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;"
        self.query(concept_constraint_query)

        # We need students to have unique IDs
        student_constraint_query = "CREATE CONSTRAINT student_id IF NOT EXISTS FOR (s:Student) REQUIRE s.id IS UNIQUE;"
        self.query(student_constraint_query)

        # Create Vector Index for Concepts
        vector_index_query = """
        CREATE VECTOR INDEX concept_embedding IF NOT EXISTS
        FOR (c:Concept) ON (c.embedding)
        OPTIONS {indexConfig: {
         `vector.dimensions`: 384,
         `vector.similarity_function`: 'cosine'
        }}
        """
        self.query(vector_index_query)

        print("Schema constraints and indexes initialized successfully.")

if __name__ == "__main__":
    if not NEO4J_URI or not NEO4J_USERNAME or not NEO4J_PASSWORD:
        print("Error: Missing Neo4j credentials in environment. Have you set up your .env file?")
    else:
        conn = Neo4jConnection(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        if conn.driver:
            conn.initialize_schema()
            conn.close()
