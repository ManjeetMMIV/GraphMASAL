"""
QA Session Store — persists every query/answer turn to a SQLite database
alongside structured analysis fields from the LangGraph agent state.
"""

import json
import os
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Default DB path — can be overridden via GRAPHMASAL_QA_DB env var
_DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "qa_sessions.db"


def _db_path() -> Path:
    custom = os.getenv("GRAPHMASAL_QA_DB")
    path = Path(custom) if custom else _DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the qa_sessions table and indexes if they don't already exist."""
    conn = _get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS qa_sessions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id       TEXT    NOT NULL,
                student_id       TEXT    NOT NULL,
                timestamp        TEXT    NOT NULL,
                user_input       TEXT    NOT NULL,
                final_response   TEXT    NOT NULL,
                route            TEXT,
                route_reason     TEXT,
                misconception    INTEGER NOT NULL DEFAULT 0,
                affected_concepts TEXT,
                learning_paths   TEXT,
                retrieved_context TEXT,
                response_time_ms INTEGER,
                model_used       TEXT,
                langsmith_run_id TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_qs_student   ON qa_sessions(student_id);
            CREATE INDEX IF NOT EXISTS idx_qs_session   ON qa_sessions(session_id);
            CREATE INDEX IF NOT EXISTS idx_qs_timestamp ON qa_sessions(timestamp);
        """)
        conn.commit()
    finally:
        conn.close()


def log_qa_turn(
    *,
    session_id: str,
    student_id: str,
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
) -> int:
    """
    Insert one Q&A turn record.  Returns the new row id.
    """
    conn = _get_conn()
    try:
        cur = conn.execute(
            """
            INSERT INTO qa_sessions (
                session_id, student_id, timestamp,
                user_input, final_response,
                route, route_reason, misconception,
                affected_concepts, learning_paths, retrieved_context,
                response_time_ms, model_used, langsmith_run_id
            ) VALUES (?,?,?, ?,?, ?,?,?, ?,?,?, ?,?,?)
            """,
            (
                session_id,
                student_id,
                datetime.now(timezone.utc).isoformat(),
                user_input,
                final_response,
                route,
                route_reason,
                int(misconception_detected),
                json.dumps(affected_concepts or []),
                json.dumps(learning_paths or []),
                retrieved_context,
                response_time_ms,
                model_used,
                langsmith_run_id,
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Analytics helpers
# ---------------------------------------------------------------------------

def get_session_stats(session_id: str) -> dict:
    """Return aggregate stats for a single chat session."""
    conn = _get_conn()
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*)                                              AS turns,
                SUM(misconception)                                    AS misconception_turns,
                AVG(response_time_ms)                                 AS avg_response_ms,
                MIN(timestamp)                                        AS started_at,
                MAX(timestamp)                                        AS last_at
            FROM qa_sessions
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()


def get_student_summary(student_id: str) -> dict:
    """Return aggregate stats for a student across all sessions."""
    conn = _get_conn()
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*)                     AS total_turns,
                COUNT(DISTINCT session_id)   AS total_sessions,
                SUM(misconception)           AS total_misconceptions,
                AVG(response_time_ms)        AS avg_response_ms,
                MIN(timestamp)               AS first_interaction,
                MAX(timestamp)               AS last_interaction
            FROM qa_sessions
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()


def get_route_distribution(student_id: str | None = None) -> list[dict]:
    """
    Count how many turns went through each route.
    Optionally filter by student_id.
    """
    conn = _get_conn()
    try:
        if student_id:
            rows = conn.execute(
                "SELECT route, COUNT(*) AS count FROM qa_sessions WHERE student_id = ? GROUP BY route",
                (student_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT route, COUNT(*) AS count FROM qa_sessions GROUP BY route"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_recent_turns(student_id: str, limit: int = 10) -> list[dict]:
    """Return the most recent Q&A turns for a student."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT
                session_id, timestamp, user_input, final_response,
                route, misconception, affected_concepts, response_time_ms
            FROM qa_sessions
            WHERE student_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (student_id, limit),
        ).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            d["affected_concepts"] = json.loads(d["affected_concepts"] or "[]")
            results.append(d)
        return results
    finally:
        conn.close()


def get_misconception_analysis(student_id: str) -> list[dict]:
    """
    Return all turns where a misconception was detected,
    decoded with full concept and path detail.
    """
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT timestamp, user_input, affected_concepts, learning_paths, route_reason
            FROM qa_sessions
            WHERE student_id = ? AND misconception = 1
            ORDER BY timestamp DESC
            """,
            (student_id,),
        ).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            d["affected_concepts"] = json.loads(d["affected_concepts"] or "[]")
            d["learning_paths"] = json.loads(d["learning_paths"] or "[]")
            results.append(d)
        return results
    finally:
        conn.close()
