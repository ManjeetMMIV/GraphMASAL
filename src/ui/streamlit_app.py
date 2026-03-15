import json
import os
import sqlite3
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import graphviz

import streamlit as st
from dotenv import load_dotenv

# Ensure absolute imports from src.* work when running this file directly.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.agents.llm import describe_chat_model
from src.agents.workflow import build_graph
from src.graph.db import Neo4jConnection
from src.graph.student import StudentManager
from src.ingestion.pdf_pipeline import PdfEmbeddingPipeline
from src.pathing.roadmap import compute_student_roadmap
from src.storage.qa_store import init_db, log_qa_turn


AGENT_ORDER = ["Router", "Diagnoser", "Planner", "Tutor"]


def _get_neo4j_connection() -> Neo4jConnection | None:
    uri = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USERNAME", "")
    pwd = os.getenv("NEO4J_PASSWORD", "")
    if not (uri and user and pwd):
        return None
    return Neo4jConnection(uri, user, pwd)


def _qa_db_path() -> Path:
    custom = os.getenv("GRAPHMASAL_QA_DB")
    if custom:
        return Path(custom)
    return REPO_ROOT / "data" / "qa_sessions.db"


def _reset_student_memory(conn: Neo4jConnection, student_id: str) -> int:
    records = conn.query(
        """
        MATCH (:Student {id: $student_id})-[:REMEMBERS]->(m:Memory)
        WITH collect(m) AS memories
        FOREACH (x IN memories | DETACH DELETE x)
        RETURN size(memories) AS deleted_count
        """,
        {"student_id": student_id},
    )
    return int(records[0]["deleted_count"]) if records else 0


def _reset_student_mastery(conn: Neo4jConnection, student_id: str) -> int:
    records = conn.query(
        """
        MATCH (:Student {id: $student_id})-[r:HAS_MASTERY_OF]->(:Concept)
        WITH collect(r) AS rels
        FOREACH (x IN rels | DELETE x)
        RETURN size(rels) AS deleted_count
        """,
        {"student_id": student_id},
    )
    return int(records[0]["deleted_count"]) if records else 0


def _reset_pdf_embeddings(conn: Neo4jConnection) -> dict[str, int]:
    chunk_rows = conn.query(
        """
        MATCH (c:PDFChunk)
        WITH collect(c) AS chunks
        FOREACH (x IN chunks | DETACH DELETE x)
        RETURN size(chunks) AS deleted_count
        """
    )
    doc_rows = conn.query(
        """
        MATCH (d:PDFDocument)
        WITH collect(d) AS docs
        FOREACH (x IN docs | DETACH DELETE x)
        RETURN size(docs) AS deleted_count
        """
    )
    return {
        "chunks": int(chunk_rows[0]["deleted_count"]) if chunk_rows else 0,
        "documents": int(doc_rows[0]["deleted_count"]) if doc_rows else 0,
    }


def _reset_qa_logs(student_id: str | None = None) -> int:
    db_path = _qa_db_path()
    if not db_path.exists():
        return 0

    conn = sqlite3.connect(str(db_path))
    try:
        if student_id:
            cur = conn.execute("DELETE FROM qa_sessions WHERE student_id = ?", (student_id,))
        else:
            cur = conn.execute("DELETE FROM qa_sessions")
        conn.commit()
        return cur.rowcount if cur.rowcount is not None else 0
    finally:
        conn.close()


def _roadmap_graphviz(roadmap: dict[str, Any]) -> graphviz.Digraph:
    dot = graphviz.Digraph()
    dot.attr(rankdir="LR", bgcolor="white")
    dot.attr("node", shape="box", style="rounded,filled", fontname="Arial")

    graph = roadmap["graph"]
    mastery = roadmap["mastery"]
    sources = set(roadmap["sources"])
    sinks = set(roadmap["sinks"])
    path_nodes = {node_id for path in roadmap["paths"] for node_id in path["node_ids"]}

    for node_id in path_nodes:
        node_name = graph.nodes[node_id].get("name", node_id)
        score = mastery.get(node_id, 0.0)
        fill = "#f3f4f6"
        if node_id in sources:
            fill = "#d1fae5"
        elif node_id in sinks:
            fill = "#fee2e2"
        elif score > 0.0:
            fill = "#fef3c7"

        dot.node(node_id, f"{node_name}\nmastery={score:.2f}", fillcolor=fill)

    for path in roadmap["paths"]:
        for left, right in zip(path["node_ids"], path["node_ids"][1:]):
            dot.edge(left, right, color="#2563eb", penwidth="2")

    return dot


def _bootstrap_demo_student(student_id: str) -> None:
    uri = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USERNAME", "")
    pwd = os.getenv("NEO4J_PASSWORD", "")
    if not (uri and user and pwd):
        return

    conn = Neo4jConnection(uri, user, pwd)
    try:
        manager = StudentManager(conn)
        manager.create_student_from_dict(student_id, "Alice", {})
        manager.update_mastery(student_id, "paging", 1.0)
        manager.update_mastery(student_id, "memory-virtualization", 1.0)
        manager.update_mastery(student_id, "computer-architecture", 1.0)
    finally:
        conn.close()


def _render_agent_cards(state_map: dict[str, str], containers: dict[str, Any]) -> None:
    color_by_state = {
        "pending": "#9ca3af",
        "running": "#f59e0b",
        "done": "#10b981",
        "skipped": "#6b7280",
    }
    icon_by_state = {
        "pending": "\u23f3",
        "running": "\u25b6\ufe0f",
        "done": "\u2705",
        "skipped": "\u23ed\ufe0f",
    }

    for agent in AGENT_ORDER:
        state = state_map.get(agent, "pending")
        containers[agent].markdown(
            (
                "<div style='border:1px solid #e5e7eb;border-radius:12px;padding:10px;'>"
                f"<div style='font-size:0.85rem;color:#6b7280;'>{agent}</div>"
                f"<div style='font-size:1rem;color:{color_by_state[state]};font-weight:600;'>"
                f"{icon_by_state[state]} {state.title()}</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def _stream_turn(app: Any, initial_state: dict[str, Any], run_cfg: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    merged_updates: dict[str, Any] = {}
    timeline: list[str] = []

    for event in app.stream(initial_state, stream_mode="updates", config=run_cfg):
        if not isinstance(event, dict):
            continue
        for node_name, payload in event.items():
            if not isinstance(payload, dict):
                timeline.append(f"{node_name}: completed")
                continue

            timeline.append(f"{node_name}: {json.dumps(payload, ensure_ascii=True)[:220]}")
            merged_updates.update(payload)

    return merged_updates, timeline


def main() -> None:
    load_dotenv(override=True)
    init_db()

    st.set_page_config(page_title="GraphMASAL Agent Console", page_icon=":brain:", layout="wide")
    st.title("GraphMASAL Agent Console")
    st.caption("Live multi-agent tutoring with workflow trace (Router -> Diagnoser -> Planner -> Tutor)")

    if "graph_app" not in st.session_state:
        st.session_state.graph_app = build_graph()
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "student_id" not in st.session_state:
        st.session_state.student_id = "student_123"
    if "student_bootstrapped" not in st.session_state:
        try:
            _bootstrap_demo_student(st.session_state.student_id)
            st.session_state.student_bootstrapped = True
        except Exception as exc:
            st.session_state.student_bootstrapped = False
            st.warning(f"Student bootstrap skipped: {exc}")

    with st.sidebar:
        st.subheader("Runtime")
        st.text_input("Student ID", key="student_id")
        st.code(f"Session: {st.session_state.session_id}")
        st.write(f"Model: {describe_chat_model()}")
        tracing_on = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        st.write(f"LangSmith tracing: {'ON' if tracing_on else 'OFF'}")
        if st.button("New Session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.chat_history = []
            st.rerun()

        st.divider()
        st.subheader("Learner Roadmap")
        show_roadmap = st.toggle(
            "Show optimal learning path",
            value=False,
            help="Visualize the student's current optimal learning roadmap from mastered concepts to unknown targets.",
        )
        roadmap_refresh = st.button("Refresh roadmap", use_container_width=True)

        if show_roadmap or roadmap_refresh:
            conn = _get_neo4j_connection()
            if conn is None:
                st.error("Neo4j credentials are missing in .env.")
            else:
                try:
                    roadmap = compute_student_roadmap(conn, st.session_state.student_id)
                    if roadmap["paths"]:
                        st.caption(
                            f"Known concepts: {len(roadmap['sources'])} | Learning targets: {len(roadmap['sinks'])}"
                        )
                        for path in roadmap["paths"]:
                            st.markdown(f"**Path {path['index']}**: {' -> '.join(path['names'])}")
                        st.graphviz_chart(_roadmap_graphviz(roadmap), use_container_width=True)
                    else:
                        st.caption("No optimal path could be generated for the current student state.")
                except Exception as exc:
                    st.error(f"Roadmap generation failed: {exc}")
                finally:
                    conn.close()

        st.divider()
        st.subheader("PDF Embedding Pipeline")
        uploaded_pdf = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            accept_multiple_files=False,
            help="Extract text, chunk it, embed it, and store document chunks in Neo4j.",
        )

        if uploaded_pdf is not None:
            st.caption(f"Selected: {uploaded_pdf.name}")
            if st.button("Embed PDF into Neo4j", use_container_width=True):
                conn = _get_neo4j_connection()
                if conn is None:
                    st.error("Neo4j credentials are missing in .env.")
                else:
                    with st.spinner("Parsing PDF and generating embeddings..."):
                        try:
                            pipeline = PdfEmbeddingPipeline(conn)
                            pipeline.initialize_schema()
                            result = pipeline.ingest_pdf_bytes(
                                uploaded_pdf.name,
                                uploaded_pdf.getvalue(),
                            )
                            st.success(
                                f"Embedded {result['file_name']} into {result['chunk_count']} chunks across {result['page_count']} pages."
                            )
                            st.json(result)
                        except Exception as exc:
                            st.error(f"PDF ingestion failed: {exc}")
                        finally:
                            conn.close()

        if st.button("Refresh uploaded PDF list", use_container_width=True):
            st.session_state["refresh_pdf_docs"] = str(uuid.uuid4())

        conn = _get_neo4j_connection()
        if conn is not None:
            try:
                pipeline = PdfEmbeddingPipeline(conn)
                recent_docs = pipeline.list_recent_documents(limit=5)
                with st.expander("Recent embedded PDFs", expanded=False):
                    if recent_docs:
                        for doc in recent_docs:
                            st.markdown(
                                f"**{doc['file_name']}**  \\n+Pages: {doc['page_count']} | Chunks: {doc['chunk_count']}  \\n+Updated: {doc['updated_at']}"
                            )
                    else:
                        st.caption("No embedded PDFs found yet.")
            finally:
                conn.close()

        st.divider()
        st.subheader("Reset / Test Utilities")
        enable_resets = st.checkbox(
            "Enable destructive reset actions",
            value=False,
            help="Protects against accidental data deletion.",
        )

        if enable_resets:
            if st.button("Reset Chat Session", use_container_width=True):
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.chat_history = []
                st.success("Session state cleared.")

            if st.button("Clear Student Memory + Mastery", use_container_width=True):
                conn = _get_neo4j_connection()
                if conn is None:
                    st.error("Neo4j credentials are missing in .env.")
                else:
                    try:
                        deleted_memories = _reset_student_memory(conn, st.session_state.student_id)
                        deleted_mastery = _reset_student_mastery(conn, st.session_state.student_id)
                        st.success(
                            f"Cleared {deleted_memories} memories and {deleted_mastery} mastery links for {st.session_state.student_id}."
                        )
                    except Exception as exc:
                        st.error(f"Reset failed: {exc}")
                    finally:
                        conn.close()

            if st.button("Clear PDF Embeddings", use_container_width=True):
                conn = _get_neo4j_connection()
                if conn is None:
                    st.error("Neo4j credentials are missing in .env.")
                else:
                    try:
                        result = _reset_pdf_embeddings(conn)
                        st.success(
                            f"Deleted {result['documents']} PDF documents and {result['chunks']} PDF chunks."
                        )
                    except Exception as exc:
                        st.error(f"PDF reset failed: {exc}")
                    finally:
                        conn.close()

            if st.button("Clear This Student Q&A Logs", use_container_width=True):
                try:
                    deleted_rows = _reset_qa_logs(st.session_state.student_id)
                    st.success(f"Deleted {deleted_rows} Q&A rows for {st.session_state.student_id}.")
                except Exception as exc:
                    st.error(f"Q&A reset failed: {exc}")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask the OS tutor anything...")
    if not prompt:
        return

    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status = st.status("Running agent workflow...", expanded=True)

        card_cols = st.columns(4)
        card_containers = {
            AGENT_ORDER[i]: card_cols[i].empty() for i in range(4)
        }
        agent_states = {name: "pending" for name in AGENT_ORDER}
        _render_agent_cards(agent_states, card_containers)

        timeline_box = st.empty()
        timeline_lines: list[str] = []

        initial_state = {
            "student_id": st.session_state.student_id,
            "user_input": prompt,
            "chat_history": st.session_state.chat_history,
            "route": "retrieve",
            "route_reason": "",
            "misconception_detected": False,
            "affected_concepts": [],
            "learning_paths": [],
            "retrieved_context": "",
            "long_term_memory": "",
            "final_response": "",
        }

        run_cfg: dict[str, Any] = {}
        if os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true":
            run_cfg = {
                "run_name": f"graphmasal-streamlit-{st.session_state.session_id[:8]}",
                "tags": ["graphmasal", "streamlit"],
                "metadata": {
                    "session_id": st.session_state.session_id,
                    "student_id": st.session_state.student_id,
                },
            }

        t0 = time.monotonic()
        final_state: dict[str, Any] = {}

        try:
            for event in st.session_state.graph_app.stream(
                initial_state,
                stream_mode="updates",
                config=run_cfg if run_cfg else None,
            ):
                if not isinstance(event, dict):
                    continue
                for node_name, payload in event.items():
                    if node_name in agent_states:
                        for agent in AGENT_ORDER:
                            if agent_states[agent] == "running":
                                agent_states[agent] = "done"
                        agent_states[node_name] = "running"
                        _render_agent_cards(agent_states, card_containers)

                    line = f"[{node_name}] {json.dumps(payload, ensure_ascii=True)[:260]}"
                    timeline_lines.append(line)
                    timeline_box.code("\n".join(timeline_lines[-18:]))

                    if isinstance(payload, dict):
                        final_state.update(payload)

            for agent in AGENT_ORDER:
                if agent_states[agent] == "running":
                    agent_states[agent] = "done"
            if final_state.get("route") == "retrieve":
                agent_states["Diagnoser"] = "skipped"
                agent_states["Planner"] = "skipped"
            _render_agent_cards(agent_states, card_containers)

            elapsed_ms = int((time.monotonic() - t0) * 1000)
            answer = final_state.get("final_response") or "No response was generated."

            st.markdown(answer)
            status.update(label=f"Completed in {elapsed_ms} ms", state="complete", expanded=False)

            with st.expander("Turn Summary", expanded=False):
                st.json(
                    {
                        "route": final_state.get("route", ""),
                        "route_reason": final_state.get("route_reason", ""),
                        "misconception_detected": final_state.get("misconception_detected", False),
                        "affected_concepts": final_state.get("affected_concepts", []),
                        "learning_paths": final_state.get("learning_paths", []),
                    }
                )

            st.session_state.chat_history.append({"role": "assistant", "content": answer})

            log_qa_turn(
                session_id=st.session_state.session_id,
                student_id=st.session_state.student_id,
                user_input=prompt,
                final_response=answer,
                route=final_state.get("route", ""),
                route_reason=final_state.get("route_reason", ""),
                misconception_detected=bool(final_state.get("misconception_detected", False)),
                affected_concepts=final_state.get("affected_concepts", []),
                learning_paths=final_state.get("learning_paths", []),
                retrieved_context=final_state.get("retrieved_context", ""),
                response_time_ms=elapsed_ms,
                model_used=describe_chat_model(),
                langsmith_run_id="",
            )

        except Exception as exc:
            status.update(label="Workflow failed", state="error", expanded=True)
            st.error(f"Agent workflow error: {exc}")


if __name__ == "__main__":
    main()
