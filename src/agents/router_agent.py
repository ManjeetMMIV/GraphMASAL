import json as _json

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.agents.llm import get_chat_model
from src.agents.state import AgentState
from src.agents.tools import recall_memory_tool


# ── Keyword heuristics (expanded) ──────────────────────────────────────────
DIAGNOSIS_CUES = (
    "wrong",
    "mistake",
    "confused",
    "confusing",
    "failed",
    "don't understand",
    "dont understand",
    "do not understand",
    "stuck",
    "misunderstood",
    "help me learn",
    "what should i learn",
    "plan for",
    "struggling",
    "struggle",
    "can't figure out",
    "having trouble",
    "keep getting",
    "keep failing",
    "messed up",
    "lost on",
    "no idea how",
    "bombed",
    "need help with",
    "going wrong",
    "not working for me",
    "got it wrong",
    "my answer was wrong",
    "i thought it was",
    "isn't it supposed to",
    "why did i get",
    "what am i doing wrong",
    "i failed",
    "i bombed",
    "remediation",
    "remediate",
    "fix my understanding",
    "learn from scratch",
)

RETRIEVE_CUES = (
    "what is",
    "what are",
    "explain",
    "define",
    "describe",
    "how does",
    "how do",
    "tell me about",
    "give me an example",
    "show me",
    "difference between",
    "compare",
    "list the",
    "what does",
    "why is",
    "why do",
    "when is",
    "advantages of",
    "disadvantages of",
)

# ── Few-shot examples for the LLM router ───────────────────────────────────
_FEW_SHOT_EXAMPLES = """
Example 1:
Student says: "What is virtual memory?"
Your answer: {"route": "retrieve", "reason": "Student asks a direct factual question about a concept definition."}

Example 2:
Student says: "I keep getting segmentation faults when I try to implement paging. I don't know what I'm doing wrong."
Your answer: {"route": "diagnose", "reason": "Student signals repeated failure and confusion about paging, indicating a misconception."}

Example 3:
Student says: "Can you explain the difference between threads and processes?"
Your answer: {"route": "retrieve", "reason": "Student requests a comparative explanation — factual retrieval."}

Example 4:
Student says: "I thought mutex and semaphore were the same thing but my exam answer was marked wrong."
Your answer: {"route": "diagnose", "reason": "Student reveals a confirmed misconception (mutex vs semaphore) that led to a wrong answer."}

Example 5:
Student says: "How are page tables implemented in x86 architecture?"
Your answer: {"route": "retrieve", "reason": "Student asks a specific technical question — factual retrieval."}

Example 6:
Student says: "I'm totally lost on file systems, can you create a learning plan for me?"
Your answer: {"route": "diagnose", "reason": "Student explicitly requests remediation and a learning plan, indicating they are stuck."}

Example 7:
Student says: "What should I study to prepare for deadlocks?"
Your answer: {"route": "diagnose", "reason": "Student asks for a learning plan / study preparation, which needs diagnostic path planning."}

Example 8:
Student says: "Give me some examples of REST API status codes."
Your answer: {"route": "retrieve", "reason": "Student asks for examples of a concept — straightforward factual retrieval."}

Example 9:
Student says: "Explain why my specific code snippet `int *p; *p = 5;` causes a crash."
Your answer: {"route": "diagnose", "reason": "Student asks to diagnose an error in their specific code/implementation."}

Example 10:
Student says: "Can you explain how a multi-level feedback queue works? I'm having a hard time grasping the concept."
Your answer: {"route": "retrieve", "reason": "Student is asking for an explanation of a general concept despite expressing difficulty."}

Example 11:
Student says: "I understand TLBs, but in my simulation the hit rate is 10%. Is my matrix loop causing thrashing?"
Your answer: {"route": "diagnose", "reason": "Student reports an unexpected result in their simulation and asks to diagnose the cause."}

Example 12:
Student says: "I am so lost. Please just tell me what DMA (Direct Memory Access) stands for and what it does."
Your answer: {"route": "retrieve", "reason": "Student is asking for a direct definition and summary of what a concept does."}
"""


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

    # ── Heuristics: Only shortcut trivial/pure textbook definitions ──
    # For all nuanced, multi-clause, or personal queries, let the LLM classify.
    is_pure_definition = user_text.startswith(("what is ", "what are ", "define ")) and len(user_text.split()) <= 7 and not any(k in user_text for k in ("my", "i ", "me", "code", "fail", "crash", "bug", "wrong", "error"))
    if is_pure_definition:
        print("Router selected retrieve path via simple definition shortcut.")
        return {
            "route": "retrieve",
            "route_reason": "User asked a direct, short factual definition.",
            "long_term_memory": memory_context,
        }

    # ── Tier 2: LLM classification with rich few-shot CoT examples ─────────────────
    llm = get_chat_model(temperature=0)
    system_prompt = f"""You are a routing classifier for an adaptive tutoring system.
The current student's ID is {state['student_id']}.

Your task: classify the student's message into exactly ONE route.

## Routes
- **diagnose**:
  * The student reports an error, bug, crash, or unexpected behavior in their own code, simulation, or lab.
  * The student reveals a confirmed misconception ("I thought X was Y", "my exam answer was marked wrong").
  * The student asks for remediation, a learning plan, or what they should study to fix their understanding.
  * The student asks "what did I do wrong" or "what did I miss in my design".

- **retrieve**:
  * The student asks for a factual definition, explanation, overview, or comparison of a standard concept ("What is X", "How does Y work", "Compare A and B").
  * The student asks for examples or documentation of a topic.
  * Even if the student says "I'm having a hard time" or "I am so lost", if their actual request is "explain X" or "tell me what X does", route to **retrieve**.

## Decision Rules
1. Troubleshooting own code/simulation/lab/exam mistake -> **diagnose**.
2. Asking for a study plan / roadmap / remediation -> **diagnose**.
3. Concept definition, explanation, or standard comparison -> **retrieve**.
4. When in doubt, prioritize whether the user needs debugging/diagnosis of their work (diagnose) vs learning a concept (retrieve).

## Relevant long-term memory
{memory_context}

## Few-Shot Examples
{_FEW_SHOT_EXAMPLES}

## Output Format
Return ONLY a JSON object (no markdown fencing):
{{"route": "diagnose" or "retrieve", "reason": "short reason", "confidence": 0.0 to 1.0}}
"""

    # Build messages with full conversation history so routing is context-aware
    messages = [SystemMessage(content=system_prompt)]
    for turn in state.get("chat_history", []):
        if turn.get("role") == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn.get("role") == "assistant":
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=state["user_input"]))

    response = llm.invoke(messages).content

    # ── Parse structured JSON output ──────────────────────────────────────
    route = "retrieve"
    reason = "Defaulted to retrieval-oriented tutoring."
    confidence = 0.5

    try:
        # Strip markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
        if cleaned.endswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[:-1])
        cleaned = cleaned.strip()

        parsed = _json.loads(cleaned)
        candidate = parsed.get("route", "").strip().lower()
        if candidate in {"diagnose", "retrieve"}:
            route = candidate
        reason = parsed.get("reason", reason)
        confidence = float(parsed.get("confidence", 0.5))
    except (_json.JSONDecodeError, ValueError, AttributeError):
        # Fall back to line-based parsing for robustness
        for line in response.splitlines():
            normalized = line.strip()
            if normalized.upper().startswith("ROUTE:"):
                candidate = normalized.split(":", 1)[1].strip().lower()
                if candidate in {"diagnose", "retrieve"}:
                    route = candidate
            elif normalized.upper().startswith("REASON:"):
                reason = normalized.split(":", 1)[1].strip() or reason

    # ── Tier 3: Confidence gating ─────────────────────────────────────────
    # If LLM confidence is low and diagnosis cues are present, defer to diagnose (safety first)
    has_diagnose_cue = any(cue in user_text for cue in DIAGNOSIS_CUES)
    if confidence < 0.6 and has_diagnose_cue:
        route = "diagnose"
        reason = f"Low-confidence LLM ({confidence:.2f}) overridden by diagnose cue."

    print(f"Router selected {route} path (confidence={confidence:.2f}).")
    return {
        "route": route,
        "route_reason": reason,
        "long_term_memory": memory_context,
    }