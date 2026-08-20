import json
from fastapi import Request
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import List

# Lazy import - only load the heavy LangGraph workflow on first request
# so Render can bind to the port before hitting memory limits
_graph_app = None

def _get_graph():
    global _graph_app
    if _graph_app is None:
        from src.agents.workflow import build_graph
        _graph_app = build_graph()
    return _graph_app

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    student_id: str
    session_id: str = ""
    topic: str = ""
    message: str
    chat_history: List[ChatMessage] = []

async def chat_stream_logic(request: Request, body: ChatRequest):
    active_plan: list = []
    learning_pace: str = "normal"
    if body.session_id:
        try:
            from src.storage.qa_store import get_db as _qa_get_db
            session_doc = _qa_get_db()["sessions"].find_one({"session_id": body.session_id})
            if session_doc:
                active_plan = session_doc.get("active_plan", [])
                learning_pace = session_doc.get("learning_pace", "normal")
        except Exception:
            pass 

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
        "learning_pace": learning_pace,
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
            for event in _get_graph().stream(initial_state, stream_mode="updates", config=run_cfg):
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

            if final_response and body.session_id:
                try:
                    from src.storage.qa_store import log_qa_turn
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
                    pass 

            yield {"event": "done", "data": "{}"}

        except Exception as e:
            yield {"event": "error", "data": json.dumps({"detail": str(e)})}

    return EventSourceResponse(event_generator())
