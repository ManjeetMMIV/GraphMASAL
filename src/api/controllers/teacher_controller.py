from fastapi import HTTPException
from pydantic import BaseModel
from src.api.dependencies import get_neo4j_connection

class AddStudentRequest(BaseModel):
    student_id: str

def list_teacher_students_logic(teacher_id: str):
    from src.storage.qa_store import get_teacher_students
    students = get_teacher_students(teacher_id)
    return {"students": students}

def add_student_to_teacher_logic(teacher_id: str, req: AddStudentRequest):
    from src.storage.qa_store import add_teacher_student
    add_teacher_student(teacher_id, req.student_id)
    return {"status": "ok", "student_id": req.student_id}

def remove_student_from_teacher_logic(teacher_id: str, student_id: str):
    from src.storage.qa_store import remove_teacher_student
    remove_teacher_student(teacher_id, student_id)
    return {"status": "ok", "student_id": student_id}

def get_student_progress_logic(student_id: str):
    try:
        from src.storage.qa_store import get_db as _qa_get_db
        db = _qa_get_db()
        
        sessions = list(db.sessions.find({"student_id": student_id}, {"_id": 0}).sort("updated_at", -1))
        recent_turns = list(db.qa_sessions.find({"student_id": student_id}, {"_id": 0}).sort("timestamp", -1).limit(10))
        doubt_turns = list(db.qa_sessions.find({"student_id": student_id, "misconception": 1}, {"_id": 0}).sort("timestamp", -1))
        
        conn = get_neo4j_connection()
        strong_topics = []
        weak_topics = []
        unstarted_topics = []
        concept_names = {}
        
        if conn:
            try:
                all_concepts_records = conn.query("MATCH (c:Concept) RETURN c.id AS id, c.name AS name")
                for r in (all_concepts_records or []):
                    concept_names[r["id"]] = r["name"]

                rows = conn.query(
                    """
                    MATCH (s:Student {id: $sid})
                    OPTIONAL MATCH (s)-[r:HAS_MASTERY_OF]->(c:Concept)
                    OPTIONAL MATCH (s)-[:HAS_EXTRACTED]->(c2:Concept)
                    WITH s, collect(DISTINCT c) + collect(DISTINCT c2) AS all_concepts
                    UNWIND all_concepts AS concept
                    WITH DISTINCT concept, s
                    OPTIONAL MATCH (s)-[r:HAS_MASTERY_OF]->(concept)
                    RETURN concept.id AS id, concept.name AS name, concept.description AS desc,
                           coalesce(r.score, 0.0) AS mastery
                    ORDER BY concept.name
                    """,
                    {"sid": student_id}
                )
                
                for row in (rows or []):
                    concept_data = {
                        "id": row["id"],
                        "name": row["name"],
                        "desc": row.get("desc", ""),
                        "mastery": row["mastery"],
                        "mastery_pct": round(row["mastery"] * 100)
                    }
                    if row["mastery"] >= 0.8:
                        strong_topics.append(concept_data)
                    elif row["mastery"] > 0.0:
                        weak_topics.append(concept_data)
                    else:
                        unstarted_topics.append(concept_data)
            finally:
                conn.close()

        for s in sessions:
            s["active_plan_names"] = [concept_names.get(cid, cid) for cid in s.get("active_plan", [])]
            
        return {
            "student_id": student_id,
            "sessions": sessions,
            "recent_activity": recent_turns,
            "doubts": doubt_turns,
            "mastery_profile": {
                "strong_topics": strong_topics,
                "weak_topics": weak_topics,
                "unstarted_topics": unstarted_topics
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
