"""
QA Session Store — persists every query/answer turn to a MongoDB database
alongside structured analysis fields from the LangGraph agent state.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pymongo import MongoClient, ASCENDING, DESCENDING


def _get_db():
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(uri)
    return client.graphmasal


def _sessions_coll():
    return _get_db().sessions


def _turns_coll():
    return _get_db().qa_sessions


def get_db():
    """Public accessor for the database (used by server.py for plan selection)."""
    return _get_db()


def init_db() -> None:
    """Create indexes for the MongoDB collections."""
    try:
        sessions = _sessions_coll()
        sessions.create_index("student_id")
        sessions.create_index("session_id", unique=True)
        sessions.create_index([("student_id", ASCENDING), ("created_at", DESCENDING)])

        turns = _turns_coll()
        turns.create_index("student_id")
        turns.create_index("session_id")
        turns.create_index("timestamp")
    except Exception as e:
        print(f"Failed to initialize MongoDB: {e}")


# --------------------------------------------------------------------------- #
# Session Management
# --------------------------------------------------------------------------- #

def create_session(*, student_id: str, topic: str) -> Dict[str, Any]:
    """Create a new chat session document. Returns the session dict."""
    sessions = _sessions_coll()
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "session_id": session_id,
        "student_id": student_id,
        "topic": topic,
        "created_at": now,
        "updated_at": now,
    }
    sessions.insert_one(doc)
    doc.pop("_id", None)
    return doc


def get_sessions_summary(student_id: str) -> List[Dict[str, Any]]:
    """Return a list of all sessions for a student, sorted newest-first."""
    sessions = _sessions_coll()
    turns = _turns_coll()

    session_docs = list(
        sessions.find(
            {"student_id": student_id},
            {"_id": 0, "session_id": 1, "topic": 1, "created_at": 1, "updated_at": 1},
        ).sort("created_at", DESCENDING)
    )

    # Attach turn count to each session
    for s in session_docs:
        s["turn_count"] = turns.count_documents({"session_id": s["session_id"]})

    return session_docs


def get_session_history(session_id: str) -> List[Dict[str, Any]]:
    """Return the full message history for a specific session as [{role, content}]."""
    turns = _turns_coll()
    docs = turns.find({"session_id": session_id}).sort("timestamp", ASCENDING)

    history = []
    for d in docs:
        history.append({"role": "user", "content": d.get("user_input", "")})
        history.append({"role": "assistant", "content": d.get("final_response", "")})

    return history


def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
    """Return the metadata for a single session (topic, student, timestamps)."""
    sessions = _sessions_coll()
    doc = sessions.find_one({"session_id": session_id}, {"_id": 0})
    return doc


# --------------------------------------------------------------------------- #
# Turn Persistence
# --------------------------------------------------------------------------- #

def log_qa_turn(
    *,
    session_id: str,
    student_id: str,
    topic: str = "",
    user_input: str,
    final_response: str,
    route: str = "",
    route_reason: str = "",
    misconception_detected: bool = False,
    affected_concepts: list[str] | None = None,
    learning_paths: list[str] | None = None,
    retrieved_context: str = "",
    response_time_ms: Optional[int] = None,
    model_used: str = "",
    langsmith_run_id: str = "",
) -> str:
    """Insert one Q&A turn into MongoDB. Returns the inserted ID string."""
    turns = _turns_coll()
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "session_id": session_id,
        "student_id": student_id,
        "topic": topic,
        "timestamp": now,
        "user_input": user_input,
        "final_response": final_response,
        "route": route,
        "route_reason": route_reason,
        "misconception": int(misconception_detected),
        "affected_concepts": affected_concepts or [],
        "learning_paths": learning_paths or [],
        "retrieved_context": retrieved_context,
        "response_time_ms": response_time_ms,
        "model_used": model_used,
        "langsmith_run_id": langsmith_run_id,
    }

    result = turns.insert_one(doc)

    # Also bump the session's updated_at timestamp
    _sessions_coll().update_one(
        {"session_id": session_id},
        {"$set": {"updated_at": now}},
    )

    return str(result.inserted_id)


# --------------------------------------------------------------------------- #
# Cleanup
# --------------------------------------------------------------------------- #

def delete_student_history(student_id: str) -> int:
    """Deletes all sessions and turns for a specific student."""
    turns = _turns_coll()
    sessions = _sessions_coll()
    turns_deleted = turns.delete_many({"student_id": student_id}).deleted_count
    sessions.delete_many({"student_id": student_id})
    return turns_deleted
