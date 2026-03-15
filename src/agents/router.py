from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.llm import get_chat_model
from src.agents.state import AgentState
from src.agents.tools import recall_memory_tool


DIAGNOSIS_CUES = (
    "wrong",
    "mistake",
    "confused",
    "confusing",
    "failed",
    "don't understand",
    "dont understand",
    "stuck",
    "misunderstood",
    "help me learn",
    "what should i learn",
    "plan for",
)


def router_node(state: AgentState):
    """
    Decide whether the request should go through the diagnosis-and-planning path
    or directly to tutoring with retrieval.
    """
    print("\n--- [Router Agent] Executing ---")

    memory_context = recall_memory_tool.invoke({
        "query": state["user_input"],
        "student_id": state["student_id"],
    })

    user_text = state["user_input"].strip().lower()
    if any(cue in user_text for cue in DIAGNOSIS_CUES):
        print("Router selected diagnose path via heuristic cue.")
        return {
            "route": "diagnose",
            "route_reason": "User signaled confusion, struggle, or a request for remediation.",
            "long_term_memory": memory_context,
        }

    llm = get_chat_model(temperature=0)
    system_prompt = f"""
    You are a routing agent for an adaptive tutoring workflow.
    The current student's ID is {state['student_id']}.

    Available routes:
    - diagnose: use this when the student appears confused, reports failure, asks for remediation, or likely needs a learning plan.
    - retrieve: use this when the student is asking for an explanation, definition, example, or factual answer.

    Relevant long-term memory:
    {memory_context}

    Return exactly two lines:
    ROUTE: <diagnose|retrieve>
    REASON: <short reason>
    """

    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["user_input"]),
        ]
    ).content

    route = "retrieve"
    reason = "Defaulted to retrieval-oriented tutoring."
    for line in response.splitlines():
        normalized = line.strip()
        if normalized.upper().startswith("ROUTE:"):
            candidate = normalized.split(":", 1)[1].strip().lower()
            if candidate in {"diagnose", "retrieve"}:
                route = candidate
        elif normalized.upper().startswith("REASON:"):
            reason = normalized.split(":", 1)[1].strip() or reason

    print(f"Router selected {route} path.")
    return {
        "route": route,
        "route_reason": reason,
        "long_term_memory": memory_context,
    }