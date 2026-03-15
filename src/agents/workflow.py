import os
import sys
import time
import uuid
from pathlib import Path

# Allow running this file directly from src/agents while keeping absolute `src.*` imports.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(override=True)

# ── LangSmith tracing ────────────────────────────────────────────────────────
# LangChain/LangGraph automatically pick up LANGCHAIN_TRACING_V2 and
# LANGCHAIN_API_KEY from the environment, so no extra setup is needed beyond
# ensuring they are loaded before the graph is built.  We import langsmith
# here only to surface a clear warning when tracing is requested but the
# package or API key is missing.
_tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
if _tracing_enabled:
    try:
        import langsmith  # noqa: F401
        if not os.getenv("LANGCHAIN_API_KEY"):
            print(
                "[LangSmith] WARNING: LANGCHAIN_TRACING_V2=true but LANGCHAIN_API_KEY is not set. "
                "Traces will not be uploaded."
            )
        else:
            print(
                f"[LangSmith] Tracing enabled — project: "
                f"{os.getenv('LANGCHAIN_PROJECT', 'graphmasal')}"
            )
    except ImportError:
        print(
            "[LangSmith] WARNING: langsmith package not installed. "
            "Run `uv sync` to install it."
        )

from langgraph.graph import StateGraph, START, END

from src.agents.llm import describe_chat_model
from src.agents.state import AgentState
from src.agents.router import router_node
from src.agents.diagnoser import diagnoser_node
from src.agents.planner import planner_node
from src.agents.tutor import tutor_node
from src.storage.qa_store import init_db, log_qa_turn


def route_after_router(state: AgentState):
    return state.get("route", "retrieve")

def build_graph():
    # Initialize the graph builder using our strictly typed AgentState
    graph_builder = StateGraph(AgentState)
    
    # 1. Add all our agent nodes
    graph_builder.add_node("Router", router_node)
    graph_builder.add_node("Diagnoser", diagnoser_node)
    graph_builder.add_node("Planner", planner_node)
    graph_builder.add_node("Tutor", tutor_node)
    
    # 2. Define the workflow order
    # START -> Router -> (Diagnoser -> Planner -> Tutor) or Tutor -> END
    graph_builder.add_edge(START, "Router")
    graph_builder.add_conditional_edges(
        "Router",
        route_after_router,
        {
            "diagnose": "Diagnoser",
            "retrieve": "Tutor",
        },
    )
    graph_builder.add_edge("Diagnoser", "Planner")
    graph_builder.add_edge("Planner", "Tutor")
    graph_builder.add_edge("Tutor", END)
    
    # Compile it into a runnable LangChain instance
    agent_graph = graph_builder.compile()
    
    return agent_graph

if __name__ == "__main__":
    # --- Interactive Testing CLI ---
    app = build_graph()

    # Initialise the Q&A SQLite database
    init_db()
    
    print("\n" + "="*50)
    print("Welcome to GraphMASAL AI Tutor (Type 'quit' to exit)")
    print("="*50 + "\n")
    print(f"Using model: {describe_chat_model()}\n")
    
    # Give Alice full initial mastery so we can test the Diagnoser revoking it
    print("Pre-configuring Student 'Alice' (student_123)...")
    from src.graph.student import StudentManager
    from src.graph.db import Neo4jConnection
    import os
    from dotenv import load_dotenv
    load_dotenv()
    uri = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USERNAME", "")
    pwd = os.getenv("NEO4J_PASSWORD", "")
    
    if uri and user and pwd:
        conn = Neo4jConnection(uri, user, pwd)
        manager = StudentManager(conn)
        manager.create_student_from_dict("student_123", "Alice", {})
        manager.update_mastery("student_123", "paging", 1.0)
        manager.update_mastery("student_123", "memory-virtualization", 1.0)
        manager.update_mastery("student_123", "computer-architecture", 1.0)
        conn.close()
    
    print("Ready! You can now chat with Alice's AI Tutor.\n")
    chat_history = []

    # Unique ID for this run of the CLI — groups all turns in one session
    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}\n")

    while True:
        user_input = input("[Alice]: ")
        sys.stdout.flush()
        if user_input.strip().lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        initial_state = {
            "student_id": "student_123",
            "user_input": user_input,
            "chat_history": chat_history,
            "route": "retrieve",
            "route_reason": "",
            "misconception_detected": False,
            "affected_concepts": [],
            "learning_paths": [],
            "retrieved_context": "",
            "long_term_memory": "",
            "final_response": ""
        }
        
        print("\n[System]: Thinking...\n")
        sys.stdout.flush()
        
        try:
            t0 = time.monotonic()
            # When LangSmith tracing is enabled, each invoke gets a run_id we
            # can retrieve via the LangSmith API callback.  We pass a
            # run_id config so the trace is labelled with the session.
            run_cfg: dict = {}
            langsmith_run_id = ""
            if _tracing_enabled:
                run_cfg = {
                    "run_name": f"graphmasal-turn-{session_id[:8]}",
                    "tags": ["graphmasal", "tutor"],
                    "metadata": {
                        "student_id": "student_123",
                        "session_id": session_id,
                    },
                }

            # invoke() is more reliable than stream() for interactive CLI
            result = app.invoke(initial_state, config=run_cfg if run_cfg else None)
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            chat_history = result.get("chat_history", chat_history)
            
            tutor_msg = result.get("final_response", "")

            # ── Persist Q&A turn to SQLite ───────────────────────────────────
            row_id = log_qa_turn(
                session_id=session_id,
                student_id="student_123",
                user_input=user_input,
                final_response=tutor_msg,
                route=result.get("route", ""),
                route_reason=result.get("route_reason", ""),
                misconception_detected=bool(result.get("misconception_detected", False)),
                affected_concepts=result.get("affected_concepts", []),
                learning_paths=result.get("learning_paths", []),
                retrieved_context=result.get("retrieved_context", ""),
                response_time_ms=elapsed_ms,
                model_used=describe_chat_model(),
                langsmith_run_id=langsmith_run_id,
            )
            print(f"[Storage]: Turn saved (row {row_id}, {elapsed_ms} ms)")

            if tutor_msg:
                print(f"\n[AI Tutor]: {tutor_msg}\n")
            else:
                print("\n[AI Tutor]: (No response generated. Try again.)\n")
        except Exception as e:
            print(f"\n[Error]: {e}\n")
