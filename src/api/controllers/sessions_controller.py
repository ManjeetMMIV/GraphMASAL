from fastapi import HTTPException
from pydantic import BaseModel

from src.api.dependencies import bootstrap_student
from src.storage.qa_store import (
    create_session,
    get_sessions_summary,
    get_session_history,
    get_session_info,
    delete_session
)

class NewSessionRequest(BaseModel):
    student_id: str
    topic: str
    learning_pace: str = "normal"  # 'slow', 'normal', or 'fast'

def create_new_session(req: NewSessionRequest):
    """Create a new chat session and ensure the student exists in Neo4j."""
    bootstrap_student(req.student_id)
    session = create_session(
        student_id=req.student_id,
        topic=req.topic,
        learning_pace=req.learning_pace,
    )
    return session

def list_sessions(student_id: str):
    """Return all sessions for a student, newest-first."""
    sessions = get_sessions_summary(student_id)
    return {"sessions": sessions}

def get_session(session_id: str):
    """Return session info + full message history."""
    info = get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    history = get_session_history(session_id)
    return {"info": info, "history": history}

def delete_session_logic(session_id: str):
    """Delete a specific session and its history."""
    success = delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "ok", "message": "Session deleted"}
