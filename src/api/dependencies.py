import os
from typing import Optional
from fastapi import Header, HTTPException
from src.graph.db import Neo4jConnection
from src.graph.student import StudentManager


def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    """
    FastAPI dependency that validates the Bearer token from the Authorization header.
    Returns {"user_id": ..., "role": ...} or raises 401.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ").strip()
    from src.storage.qa_store import verify_auth_token
    payload = verify_auth_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def require_role(role: str):
    """Returns a FastAPI dependency that also enforces a specific role."""
    def _dep(user: dict = Header(default=None)):  # overridden below
        pass

    from fastapi import Depends

    def _check(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return _check


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
