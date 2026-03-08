import os
from dotenv import load_dotenv
from src.graph.db import Neo4jConnection
from src.graph.models import Student

class StudentManager:
    def __init__(self, conn: Neo4jConnection):
        self.conn = conn

    def create_student(self, student: Student):
        """Creates a Student node in Neo4j."""
        query = """
        MERGE (s:Student {id: $id})
        SET s.name = $name
        """
        parameters = {
            "id": student.id,
            "name": student.name
        }
        self.conn.query(query, parameters)
        print(f"Created/Updated Student Profile: {student.name}")

    def create_student_from_dict(self, student_id: str, name: str, mastery_levels: dict):
        """Convenience method to create a student directly from primitives."""
        self.create_student(Student(id=student_id, name=name, mastery_levels=mastery_levels))

    def update_mastery(self, student_id: str, concept_id: str, mastery_score: float):
        """
        Creates or updates a HAS_MASTERY_OF relationship between a student and a concept.
        The score should be a float between 0.0 and 1.0.
        """
        if not 0.0 <= mastery_score <= 1.0:
            raise ValueError("Mastery score must be between 0.0 and 1.0")

        query = """
        MATCH (s:Student {id: $student_id})
        MATCH (c:Concept {id: $concept_id})
        MERGE (s)-[r:HAS_MASTERY_OF]->(c)
        SET r.score = $score
        """
        parameters = {
            "student_id": student_id,
            "concept_id": concept_id,
            "score": float(mastery_score) # ensure it's a float
        }
        self.conn.query(query, parameters)
        print(f"Updated mastery: Student {student_id} -> Concept {concept_id} = {mastery_score}")

    def get_student_mastery(self, student_id: str) -> dict:
        """Retrieves all mastery scores for a given student."""
        query = """
        MATCH (s:Student {id: $student_id})-[r:HAS_MASTERY_OF]->(c:Concept)
        RETURN c.id as concept_id, r.score as score
        """
        parameters = {"student_id": student_id}
        results = self.conn.query(query, parameters)
        
        mastery = {}
        for record in results:
            mastery[record["concept_id"]] = record["score"]
        return mastery

if __name__ == "__main__":
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")

    if uri and user and pwd:
        conn = Neo4jConnection(uri, user, pwd)
        manager = StudentManager(conn)
        
        # 1. Create a dummy student
        test_student = Student(id="student_123", name="Alice", mastery_levels={})
        manager.create_student(test_student)
        
        # 2. Simulate some initial knowledge (e.g., Alice took a pre-test)
        # Alice knows Computer Architecture perfectly
        manager.update_mastery(test_student.id, "computer-architecture", 0.95)
        # Alice knows a bit about virtualization
        manager.update_mastery(test_student.id, "cpu-virtualization", 0.60)
        manager.update_mastery(test_student.id, "memory-virtualization", 0.40)
        # Alice is weak on processes
        manager.update_mastery(test_student.id, "processes", 0.20)
        # Initialize unknown concepts explicitly as 0 (optional, but good for tracking)
        manager.update_mastery(test_student.id, "file-systems", 0.0)
        
        # 3. Verify retrieval
        mastery = manager.get_student_mastery(test_student.id)
        print(f"\nAlice's Current Cognitive State:")
        for concept, score in mastery.items():
            print(f"- {concept}: {score:.2f}")
            
        conn.close()
