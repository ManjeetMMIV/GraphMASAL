import os
from typing import Optional
from src.graph.db import Neo4jConnection
from src.graph.student import StudentManager

def get_neo4j_connection() -> Optional[Neo4jConnection]:
    uri = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USERNAME", "")
    pwd = os.getenv("NEO4J_PASSWORD", "")
    if not (uri and user and pwd):
        return None
    return Neo4jConnection(uri, user, pwd)

def bootstrap_student(student_id: str) -> None:
    conn = get_neo4j_connection()
    if not conn:
        return
    try:
        manager = StudentManager(conn)
        manager.create_student_from_dict(student_id, student_id, {})
    finally:
        conn.close()
