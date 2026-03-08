from src.graph.db import Neo4jConnection
from src.graph.models import Concept
from src.ingestion.parser import OstepParser
import os
from dotenv import load_dotenv

class GraphBuilder:
    def __init__(self, conn: Neo4jConnection):
        self.conn = conn

    def create_concept(self, concept: Concept):
        """Creates a Concept node in Neo4j."""
        query = """
        MERGE (c:Concept {id: $id})
        SET c.name = $name,
            c.description = $description,
            c.domain = $domain
        """
        parameters = {
            "id": concept.id,
            "name": concept.name,
            "description": concept.description,
            "domain": concept.domain
        }
        self.conn.query(query, parameters)
        print(f"Created Concept: {concept.name}")

    def create_prerequisite(self, concept_id: str, prereq_id: str):
        """Creates an IS_PREREQUISITE_FOR relationship."""
        query = """
        MATCH (prereq:Concept {id: $prereq_id})
        MATCH (target:Concept {id: $concept_id})
        MERGE (prereq)-[:IS_PREREQUISITE_FOR]->(target)
        """
        parameters = {
            "prereq_id": prereq_id,
            "concept_id": concept_id
        }
        self.conn.query(query, parameters)
        print(f"Created Path: {prereq_id} -> {concept_id}")

    def build_graph(self, concepts_data: list[dict]):
        """Takes a list of concept dictionaries and builds the Neo4j graph."""
        
        # Pass 1: Create all nodes
        for data in concepts_data:
            # Validate using Pydantic
            concept = Concept(**data)
            self.create_concept(concept)
            
        # Pass 2: Create all relationships
        # We do this in a second pass to ensure all prerequisite nodes exist
        for data in concepts_data:
            concept = Concept(**data)
            for prereq_id in concept.prerequisites:
                self.create_prerequisite(concept.id, prereq_id)

if __name__ == "__main__":
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")

    if uri and user and pwd:
        conn = Neo4jConnection(uri, user, pwd)
        builder = GraphBuilder(conn)
        
        parser = OstepParser("data_md")
        concepts = parser.extract_concepts()
        
        print(f"Building graph with {len(concepts)} concepts...")
        builder.build_graph(concepts)
        
        conn.close()
        print("Graph building complete!")
    else:
        print("Neo4j configuration is missing.")
