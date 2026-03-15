import os
import re
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

    def ensure_student(self, student_id: str, name: str | None = None):
        self.create_student(Student(id=student_id, name=name or student_id, mastery_levels={}))

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

    def store_memory(self, student_id: str, memory_type: str, content: str, topics: list[str] | None = None, importance: float = 0.5):
        self.ensure_student(student_id)
        query = """
        MATCH (s:Student {id: $student_id})
        CREATE (m:Memory {
            id: randomUUID(),
            memory_type: $memory_type,
            content: $content,
            topics: $topics,
            importance: $importance,
            created_at: datetime(),
            last_accessed: datetime()
        })
        MERGE (s)-[:REMEMBERS]->(m)
        """
        parameters = {
            "student_id": student_id,
            "memory_type": memory_type,
            "content": content,
            "topics": topics or [],
            "importance": float(max(0.0, min(1.0, importance))),
        }
        self.conn.query(query, parameters)

    def recall_memories(self, student_id: str, query_text: str, limit: int = 3) -> list[dict]:
        tokens = [token.lower() for token in re.findall(r"[A-Za-z0-9_-]+", query_text) if len(token) > 2][:8]
        query = """
        MATCH (:Student {id: $student_id})-[:REMEMBERS]->(m:Memory)
        WITH m,
             CASE WHEN toLower(m.content) CONTAINS toLower($query_text) THEN 1.0 ELSE 0.0 END AS content_hit,
             size([token IN $tokens WHERE toLower(m.content) CONTAINS token]) AS token_hits,
             size([topic IN coalesce(m.topics, []) WHERE any(token IN $tokens WHERE toLower(topic) CONTAINS token OR token CONTAINS toLower(topic))]) AS topic_hits
        WITH m,
             content_hit + (0.25 * token_hits) + (0.35 * topic_hits) + (0.4 * coalesce(m.importance, 0.0)) AS memory_score
        RETURN m.content AS content,
               m.memory_type AS memory_type,
               coalesce(m.topics, []) AS topics,
               memory_score
        ORDER BY memory_score DESC, m.created_at DESC
        LIMIT $limit
        """
        parameters = {
            "student_id": student_id,
            "query_text": query_text,
            "tokens": tokens,
            "limit": limit,
        }
        records = self.conn.query(query, parameters)
        return [
            {
                "content": record["content"],
                "memory_type": record["memory_type"],
                "topics": record["topics"],
                "score": record["memory_score"],
            }
            for record in records
        ]

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
