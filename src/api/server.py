import asyncio
import json
import os
import uuid
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure absolute imports work
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.agents.workflow import build_graph
from src.graph.db import Neo4jConnection
from src.graph.student import StudentManager
from src.ingestion.pdf_pipeline import PdfEmbeddingPipeline
from src.pathing.roadmap import compute_student_roadmap
from src.storage.qa_store import (
    init_db,
    create_session,
    get_sessions_summary,
    get_session_history,
    get_session_info,
    delete_student_history,
    log_qa_turn,
)

load_dotenv(override=True)
init_db()

app = FastAPI(title="GraphMASAL API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
graph_app = build_graph()


def _get_neo4j_connection() -> Optional[Neo4jConnection]:
    uri = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USERNAME", "")
    pwd = os.getenv("NEO4J_PASSWORD", "")
    if not (uri and user and pwd):
        return None
    return Neo4jConnection(uri, user, pwd)


def _bootstrap_student(student_id: str) -> None:
    conn = _get_neo4j_connection()
    if not conn:
        return
    try:
        manager = StudentManager(conn)
        manager.create_student_from_dict(student_id, student_id, {})
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Pydantic Models
# --------------------------------------------------------------------------- #

class NewSessionRequest(BaseModel):
    student_id: str
    topic: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    student_id: str
    topic: str = ""
    message: str
    chat_history: List[ChatMessage]

class ResetRequest(BaseModel):
    student_id: str

class SelectPlanRequest(BaseModel):
    student_id: str
    session_id: str
    plan_id: str
    concept_sequence: List[str]  # ordered list of concept IDs


# --------------------------------------------------------------------------- #
# Session Endpoints
# --------------------------------------------------------------------------- #

@app.post("/api/sessions/new")
async def new_session(req: NewSessionRequest):
    """Create a new chat session and ensure the student exists in Neo4j."""
    _bootstrap_student(req.student_id)
    session = create_session(student_id=req.student_id, topic=req.topic)
    return session


@app.get("/api/sessions")
async def list_sessions(student_id: str):
    """Return all sessions for a student, newest-first."""
    sessions = get_sessions_summary(student_id)
    return {"sessions": sessions}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Return session info + full message history."""
    info = get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    history = get_session_history(session_id)
    return {"info": info, "history": history}


# --------------------------------------------------------------------------- #
# Roadmap Endpoint
# --------------------------------------------------------------------------- #

@app.get("/api/roadmap")
async def get_roadmap(student_id: str, session_id: str = ""):
    """Return the active learning plan for the session."""
    if not session_id:
        return {"paths": []}
        
    try:
        from src.storage.qa_store import get_db as _qa_get_db
        session_doc = _qa_get_db()["sessions"].find_one({"session_id": session_id})
        if not session_doc:
            return {"paths": []}
            
        active_plan = session_doc.get("active_plan", [])
        if not active_plan:
            return {"paths": []}
            
        # To get the names of the concepts, we need Neo4j
        conn = _get_neo4j_connection()
        if not conn:
            return {"paths": [{"index": 1, "node_ids": active_plan, "names": active_plan}]}
            
        try:
            from src.pathing.graph_adapter import GraphAdapter
            adapter = GraphAdapter(conn)
            nx_graph = adapter.get_networkx_graph(student_id=student_id)
            names = [nx_graph.nodes[n].get("name", n) if n in nx_graph else n for n in active_plan]
            return {"paths": [{"index": 1, "node_ids": active_plan, "names": names}]}
        finally:
            conn.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------------- #
# Video Recommendations Endpoint
# --------------------------------------------------------------------------- #

@app.get("/api/videos")
async def get_video_recommendations(student_id: str, session_id: str = ""):
    """
    Return topic-wise YouTube search links for every concept in the student's
    active learning plan, enriched with mastery scores.
    """
    import urllib.parse

    if not session_id:
        return {"topics": []}

    try:
        from src.storage.qa_store import get_db as _qa_get_db
        session_doc = _qa_get_db()["sessions"].find_one({"session_id": session_id})
        if not session_doc:
            return {"topics": []}

        active_plan = session_doc.get("active_plan", [])
        if not active_plan:
            return {"topics": []}

        conn = _get_neo4j_connection()
        if not conn:
            return {"topics": []}

        try:
            # Fetch concept names, descriptions, and mastery scores in one query
            rows = conn.query(
                """
                UNWIND $ids AS cid
                MATCH (c:Concept {id: cid})
                OPTIONAL MATCH (s:Student {id: $sid})-[r:HAS_MASTERY_OF]->(c)
                RETURN c.id AS id, c.name AS name, c.description AS desc,
                       coalesce(r.score, 0.0) AS mastery
                """,
                {"ids": active_plan, "sid": student_id}
            )
        finally:
            conn.close()

        # Index rows by concept id to preserve Active Plan ordering
        row_map = {r["id"]: r for r in (rows or [])}

        topics = []
        for idx, cid in enumerate(active_plan):
            row = row_map.get(cid)
            if not row:
                continue

            name = row["name"]
            mastery = row.get("mastery", 0.0)
            enc = urllib.parse.quote_plus(name)

            # Build a rich set of search links per topic
            videos = [
                {
                    "label": f"📖 {name} — Introduction",
                    "url": f"https://www.youtube.com/results?search_query={enc}+introduction+explained"
                },
                {
                    "label": f"🎥 {name} — Full Tutorial",
                    "url": f"https://www.youtube.com/results?search_query={enc}+tutorial"
                },
                {
                    "label": f"🎬 {name} — Visual / Animation",
                    "url": f"https://www.youtube.com/results?search_query={enc}+visual+explanation+animation"
                },
                {
                    "label": f"🧪 {name} — Examples & Problems",
                    "url": f"https://www.youtube.com/results?search_query={enc}+examples+problems+solved"
                },
            ]

            # Status for UI colouring
            if mastery >= 0.8:
                status = "mastered"
            elif idx == next(
                (i for i, c in enumerate(active_plan)
                 if row_map.get(c, {}).get("mastery", 0.0) < 0.8), None
            ):
                status = "current"
            else:
                status = "upcoming"

            topics.append({
                "id": cid,
                "name": name,
                "desc": row.get("desc", ""),
                "mastery": mastery,
                "mastery_pct": round(mastery * 100),
                "status": status,
                "step": idx + 1,
                "videos": videos,
            })

        return {"topics": topics}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------------- #
# Knowledge Graph Endpoint (for vis.js visualization)
# --------------------------------------------------------------------------- #

@app.get("/api/knowledge_graph")
async def get_knowledge_graph(student_id: str, session_id: str = ""):
    """
    Return all concept nodes and IS_PREREQUISITE_FOR edges for this student,
    plus the active plan path and per-node mastery scores (for visualization).
    """
    conn = _get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        from src.pathing.graph_adapter import GraphAdapter
        adapter = GraphAdapter(conn)
        nx_graph = adapter.get_networkx_graph(student_id=student_id)

        # Fetch mastery scores for ALL concepts this student has a relationship with
        mastery_rows = conn.query(
            """
            MATCH (s:Student {id: $sid})-[r:HAS_MASTERY_OF]->(c:Concept)
            RETURN c.id AS id, coalesce(r.score, 0.0) AS score
            """,
            {"sid": student_id}
        )
        mastery_map = {row["id"]: row["score"] for row in (mastery_rows or [])}

        nodes = [
            {
                "id": n,
                "name": nx_graph.nodes[n].get("name", n),
                "desc": nx_graph.nodes[n].get("description", ""),
                "mastery": mastery_map.get(n, 0.0),
            }
            for n in nx_graph.nodes()
        ]
        edges = [
            {"source": u, "target": v}
            for u, v in nx_graph.edges()
        ]

        # Also grab the active learning plan from the session
        active_plan = []
        if session_id:
            try:
                from src.storage.qa_store import get_db as _qa_get_db
                session_doc = _qa_get_db()["sessions"].find_one({"session_id": session_id})
                if session_doc:
                    active_plan = session_doc.get("active_plan", [])
            except Exception:
                pass

        # Compute the current concept = first concept in active_plan with mastery < 0.8
        current_concept = None
        mastered_in_plan = []
        upcoming_in_plan = []
        for cid in active_plan:
            score = mastery_map.get(cid, 0.0)
            if score >= 0.8:
                mastered_in_plan.append(cid)
            elif current_concept is None:
                current_concept = cid
            else:
                upcoming_in_plan.append(cid)

        # Build the justification object explaining what changed and why
        justification = {
            "mastered_count": len(mastered_in_plan),
            "mastered_concepts": mastered_in_plan,
            "current_concept": current_concept,
            "upcoming_count": len(upcoming_in_plan),
            "reason": (
                f"{len(mastered_in_plan)} concept(s) already mastered and skipped. "
                f"Now focusing on: '{mastery_map and next((n['name'] for n in nodes if n['id'] == current_concept), current_concept) or 'N/A'}'."
                if current_concept else
                "All concepts in the learning plan have been mastered! 🎉"
            )
        }

        return {
            "nodes": nodes,
            "edges": edges,
            "active_plan": active_plan,
            "current_concept": current_concept,
            "justification": justification,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Documents Endpoint
# --------------------------------------------------------------------------- #

@app.get("/api/documents")
async def list_documents(student_id: str):
    """Return all uploaded PDF documents from Neo4j for this student."""
    conn = _get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        pipeline = PdfEmbeddingPipeline(conn, student_id=student_id)
        docs = pipeline.list_recent_documents(limit=50)
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Backfill: Extract Concepts from Existing PDFs
# --------------------------------------------------------------------------- #

class ExtractConceptsRequest(BaseModel):
    student_id: str

@app.post("/api/extract_concepts")
async def extract_concepts_from_existing_pdfs(req: ExtractConceptsRequest):
    """
    Re-extract concepts from every PDFDocument already stored in Neo4j for this student.
    Also re-links any uploaded PDFs that weren't linked to this student yet.
    """
    # Ensure Student node exists in Neo4j first
    _bootstrap_student(req.student_id)
    
    conn = _get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        # Fetch all documents and their chunk texts for this student
        records = conn.query(
            """
            MATCH (s:Student {id: $student_id})-[:HAS_UPLOADED]->(d:PDFDocument)-[:HAS_CHUNK]->(c:PDFChunk)
            RETURN d.id AS doc_id, d.file_name AS file_name,
                   collect(c.content) AS chunks
            """,
            {"student_id": req.student_id}
        )
        if not records:
            return {"status": "ok", "message": "No PDFDocument nodes found for this student.", "total_concepts": 0}

        pipeline = PdfEmbeddingPipeline(conn, student_id=req.student_id)
        pipeline.initialize_concept_schema()

        total_concepts = 0
        results = []
        for rec in records:
            doc_id = rec["doc_id"]
            file_name = rec["file_name"]
            chunks = rec["chunks"] or []
            count = pipeline._extract_and_store_concepts(doc_id, file_name, chunks)
            total_concepts += count
            results.append({"file": file_name, "concepts_extracted": count})

        return {"status": "ok", "total_concepts": total_concepts, "documents": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()



# --------------------------------------------------------------------------- #
# PDF Upload Endpoint
# --------------------------------------------------------------------------- #

from fastapi import Form

@app.post("/api/upload_pdf")
async def upload_pdf(student_id: str = Form(...), file: UploadFile = File(...)):
    conn = _get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        _bootstrap_student(student_id)
        bytes_data = await file.read()
        pipeline = PdfEmbeddingPipeline(conn, student_id=student_id)
        pipeline.initialize_concept_schema()
        result = pipeline.ingest_pdf_bytes(file.filename, bytes_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Plan Generation & Selection Endpoints
# --------------------------------------------------------------------------- #

@app.get("/api/concepts")
async def list_concepts(student_id: str):
    """Return Concept nodes from Neo4j extracted by this student for the UI."""
    conn = _get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        rows = conn.query(
            """
            MATCH (s:Student {id: $student_id})-[:HAS_EXTRACTED]->(c:Concept)
            RETURN c.id AS id, c.name AS name, c.description AS desc 
            ORDER BY c.name
            """,
            {"student_id": student_id}
        )
        concepts = [{"id": r["id"], "name": r["name"], "desc": r.get("desc", "")}
                    for r in (rows or [])]
        return {"concepts": concepts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


class ComputePathRequest(BaseModel):
    student_id: str
    source_ids: list  # concept IDs the student already knows
    sink_ids: list    # concept IDs the student wants to learn


@app.post("/api/compute_path")
async def compute_path(req: ComputePathRequest):
    """
    Run the MSMS graph algorithm with user-specified sources (known) and sinks (targets).
    Returns an ordered flat concept sequence covering all sinks.
    """
    conn = _get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        from src.pathing.graph_adapter import GraphAdapter
        from src.pathing.msms import MSMSOptimizer

        adapter = GraphAdapter(conn)
        nx_graph = adapter.get_networkx_graph(student_id=req.student_id)

        if nx_graph.number_of_nodes() == 0:
            return {"path": [], "path_names": [], "message": f"No concept graph found for student {req.student_id}. Please upload and extract concepts first."}

        all_nodes = list(nx_graph.nodes())

        # Validate that provided IDs actually exist in the graph
        valid_sources = [nid for nid in req.source_ids if nid in all_nodes]
        valid_sinks   = [nid for nid in req.sink_ids   if nid in all_nodes]

        # If no sources, use all nodes with no incoming edges as default
        if not valid_sources:
            valid_sources = [n for n in all_nodes if nx_graph.in_degree(n) == 0]

        # If no sinks, use all left nodes (no outgoing edges)
        if not valid_sinks:
            valid_sinks = [n for n in all_nodes if nx_graph.out_degree(n) == 0]

        # Remove sinks that are already sources (nothing to learn)
        valid_sinks = [s for s in valid_sinks if s not in valid_sources]

        if not valid_sinks:
            return {"path": [], "path_names": [], "message": "Nothing left to learn — all target concepts are already marked as known."}

        mastery = {nid: 1.0 for nid in valid_sources}  # sources count as mastered

        optimizer = MSMSOptimizer(nx_graph, valid_sources, valid_sinks, mastery)
        paths = optimizer.greedy_set_cover()

        # Flatten paths into a single ordered sequence (deduplicate, preserve order)
        flat_path: list[str] = []
        seen: set[str] = set()
        for path in paths:
            for node in path:
                if node not in seen and node not in valid_sources:
                    flat_path.append(node)
                    seen.add(node)

        path_names = [nx_graph.nodes[nid].get("name", nid) for nid in flat_path]

        return {
            "path": flat_path,
            "path_names": path_names,
            "total_concepts": len(flat_path),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post("/api/select_plan")
async def select_plan(req: SelectPlanRequest):
    """Store the student's selected plan in their session."""
    from src.storage.qa_store import get_db
    db = get_db()
    db["sessions"].update_one(
        {"session_id": req.session_id},
        {"$set": {
            "active_plan": req.concept_sequence,
            "plan_id": req.plan_id,
        }},
    )
    return {"status": "ok", "plan_id": req.plan_id, "concept_count": len(req.concept_sequence)}


# --------------------------------------------------------------------------- #
# Chat (SSE Streaming) Endpoint
# --------------------------------------------------------------------------- #

@app.post("/api/chat")
async def chat_stream(request: Request, body: ChatRequest):
    # Load the active plan from the session (if student selected one)
    active_plan: list = []
    if body.session_id:
        try:
            from src.storage.qa_store import get_db as _qa_get_db
            session_doc = _qa_get_db()["sessions"].find_one({"session_id": body.session_id})
            if session_doc:
                active_plan = session_doc.get("active_plan", [])
        except Exception:
            pass  # gracefully ignore if MongoDB is unavailable

    initial_state = {
        "student_id": body.student_id,
        "user_input": body.message,
        "chat_history": [{"role": m.role, "content": m.content} for m in body.chat_history],
        "route": "retrieve",
        "route_reason": "",
        "misconception_detected": False,
        "affected_concepts": [],
        "learning_paths": [],
        "retrieved_context": "",
        "long_term_memory": "",
        "final_response": "",
        "active_plan": active_plan,
        "topic": body.topic,
    }

    run_cfg = {
        "run_name": f"graphmasal-api-{body.session_id[:8]}",
        "metadata": {
            "session_id": body.session_id,
            "student_id": body.student_id,
        },
    }

    async def event_generator():
        final_response = ""
        route = ""
        route_reason = ""
        misconception_detected = False
        affected_concepts = []
        learning_paths = []
        retrieved_context = ""

        try:
            for event in graph_app.stream(initial_state, stream_mode="updates", config=run_cfg):
                if await request.is_disconnected():
                    break

                if not isinstance(event, dict):
                    continue

                for node_name, payload in event.items():
                    summary_payload = {}
                    if isinstance(payload, dict):
                        for k in ["route", "route_reason", "misconception_detected", "affected_concepts", "learning_paths", "final_response"]:
                            if k in payload:
                                summary_payload[k] = payload[k]

                        # Capture state for persistence
                        if "route" in payload:
                            route = payload["route"]
                        if "route_reason" in payload:
                            route_reason = payload["route_reason"]
                        if "misconception_detected" in payload:
                            misconception_detected = payload["misconception_detected"]
                        if "affected_concepts" in payload:
                            affected_concepts = payload["affected_concepts"]
                        if "learning_paths" in payload:
                            learning_paths = payload["learning_paths"]
                        if "retrieved_context" in payload:
                            retrieved_context = payload["retrieved_context"]
                        if "final_response" in payload and payload["final_response"]:
                            final_response = payload["final_response"]

                    yield {
                        "event": "node_update",
                        "data": json.dumps({"node": node_name, "state": summary_payload})
                    }

                    if "final_response" in payload and payload.get("final_response"):
                        yield {
                            "event": "message",
                            "data": json.dumps({"content": payload["final_response"]})
                        }

            # Persist the completed turn to MongoDB
            if final_response and body.session_id:
                try:
                    log_qa_turn(
                        session_id=body.session_id,
                        student_id=body.student_id,
                        topic=body.topic,
                        user_input=body.message,
                        final_response=final_response,
                        route=route,
                        route_reason=route_reason,
                        misconception_detected=misconception_detected,
                        affected_concepts=affected_concepts,
                        learning_paths=learning_paths,
                        retrieved_context=retrieved_context,
                    )
                except Exception as e:
                    pass  # Don't break streaming because of a DB error

            yield {"event": "done", "data": "{}"}

        except Exception as e:
            yield {"event": "error", "data": json.dumps({"detail": str(e)})}

    return EventSourceResponse(event_generator())


# --------------------------------------------------------------------------- #
# Reset Endpoint
# --------------------------------------------------------------------------- #

@app.delete("/api/documents")
async def delete_all_documents(student_id: str):
    """Delete all uploaded PDF documents, their chunks, and concept links for this student."""
    conn = _get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        # Delete chunks that belong to documents uploaded by this student
        conn.query(
            "MATCH (s:Student {id: $student_id})-[:HAS_UPLOADED]->(d:PDFDocument)-[:HAS_CHUNK]->(c:PDFChunk) DETACH DELETE c",
            {"student_id": student_id}
        )
        # Delete the documents uploaded by this student
        result = conn.query(
            "MATCH (s:Student {id: $student_id})-[:HAS_UPLOADED]->(d:PDFDocument) DETACH DELETE d RETURN count(d) as deleted",
            {"student_id": student_id}
        )
        
        # Remove the HAS_EXTRACTED links for this student (we don't delete the Concept nodes themselves as they may be shared)
        conn.query(
            "MATCH (s:Student {id: $student_id})-[r:HAS_EXTRACTED]->(:Concept) DELETE r",
            {"student_id": student_id}
        )
        
        deleted = result[0]["deleted"] if result else 0
        return {"status": "success", "documents_deleted": deleted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post("/api/reset")
async def reset_data(request: ResetRequest):
    conn = _get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        # Clear student memory + mastery from Neo4j
        conn.query("MATCH (:Student {id: $id})-[:REMEMBERS]->(m:Memory) DETACH DELETE m", {"id": request.student_id})
        conn.query("MATCH (:Student {id: $id})-[r:HAS_MASTERY_OF]->(c:Concept) DELETE r", {"id": request.student_id})
        # Clear all PDF documents and chunks from Neo4j
        conn.query("MATCH (c:PDFChunk) DETACH DELETE c")
        conn.query("MATCH (d:PDFDocument) DETACH DELETE d")
        # Clear MongoDB sessions + turns
        docs_deleted = delete_student_history(request.student_id)
        return {"status": "success", "message": f"All data cleared: memories, mastery, PDFs, and {docs_deleted} chat turns."}
    finally:
        conn.close()



# --------------------------------------------------------------------------- #
# Static Frontend
# --------------------------------------------------------------------------- #

public_dir = REPO_ROOT / "public"
public_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="public")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
