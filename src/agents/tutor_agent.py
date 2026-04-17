from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.agents.llm import get_chat_model
from src.agents.state import AgentState
from src.agents.tools import hybrid_retrieval_tool, store_memory_tool


def _build_messages_with_history(system_prompt: str, chat_history: list, current_input: str) -> list:
    """Build a LangChain messages list: system + prior turns + current user message."""
    messages = [SystemMessage(content=system_prompt)]
    for turn in chat_history:
        role = turn.get("role", "")
        content = turn.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=current_input))
    return messages


def tutor_node(state: AgentState):
    """
    The Tutor Agent.
    Proactively teaches the student, structured as a real lesson.
    """
    print("\n--- [Tutor Agent] Executing ---")

    llm = get_chat_model(temperature=0.7)
    memory_context = state.get("long_term_memory", "")
    retrieval_context = state.get("retrieved_context", "")
    student_id = state["student_id"]
    user_input = state["user_input"]
    chat_history = state.get("chat_history", [])

    # Determine if this is a "start/continue" signal or an actual question
    START_SIGNALS = {"lets start", "let's start", "yes", "ok", "okay", "sure",
                     "go ahead", "start", "begin", "continue", "next", "proceed",
                     "ready", "i'm ready", "yep", "yeah", "alright", "got it"}
    is_continuation = user_input.strip().lower() in START_SIGNALS

    # ------------------------------------------------------------------ #
    # Build retrieval query
    # ------------------------------------------------------------------ #
    active_plan = state.get("active_plan", [])
    next_concept_name = None

    if state.get("misconception_detected", False):
        affected = state.get("affected_concepts", [])
        query = ", ".join(affected) or user_input

    elif active_plan and (is_continuation or not chat_history):
        # Follow the selected plan — teach the first concept
        next_concept_id = active_plan[0]
        try:
            import os as _os
            from src.graph.db import Neo4jConnection as _Neo4jConn
            import logging as _logging
            _conn = _Neo4jConn(
                _os.getenv("NEO4J_URI", ""),
                _os.getenv("NEO4J_USERNAME", ""),
                _os.getenv("NEO4J_PASSWORD", ""),
            )
            rows = _conn.query(
                "MATCH (c:Concept {id: $id}) RETURN c.name AS name, c.description AS desc LIMIT 1",
                {"id": next_concept_id}
            )
            _conn.close()
            if rows:
                next_concept_name = rows[0]["name"]
                next_concept_desc = rows[0].get("desc", "")
                query = f"{next_concept_name}. {next_concept_desc}"
            else:
                query = next_concept_id
        except Exception as _e:
            import logging as _logging
            _logging.warning(f"Tutor: could not look up plan concept: {_e}")
            query = next_concept_id

    elif is_continuation and chat_history:
        # Pick up where we left off using the last AI response as context
        last_ai = next(
            (t["content"] for t in reversed(chat_history) if t.get("role") == "assistant"),
            user_input,
        )
        query = last_ai[:200]

    else:
        query = user_input

    print(f"Tutor invoking hybrid retrieval with query: '{query[:80]}...'")
    retrieval_context = hybrid_retrieval_tool.invoke({
        "query": query,
        "student_id": student_id,
    })

    # ------------------------------------------------------------------ #
    # Build the system prompt
    # ------------------------------------------------------------------ #
    if state.get("misconception_detected", False):
        affected = state.get("affected_concepts", [])
        paths = "\n".join(state.get("learning_paths", []))
        system_prompt = f"""You are an expert, structured AI tutor. The student is: {student_id}.

Long-term memory: {memory_context}

The student has a misconception about: {affected}.
Their mastery score has been reset.
Knowledge context: {retrieval_context}
Recommended learning path: {paths}

TEACHING RULES — follow these strictly:
1. Gently acknowledge the student's confusion without being harsh.
2. Immediately begin teaching the FIRST concept in the learning path using this format:
   - **Concept:** [name]
   - **What it is:** one clear sentence definition
   - **Why it matters:** one sentence on relevance
   - **Real example:** a concrete, easy-to-understand example
   - **Quick check:** ask the student ONE specific question to verify understanding
3. Do NOT say "feel free to ask" or "let me know if you have questions" — instead always end with your check question.
4. Keep the response focused and educational, not conversational filler."""

    else:
        learning_paths = state.get("learning_paths", [])
        plan_section = ""
        if learning_paths:
            plan_section = f"""
ACTIVE LEARNING PLAN — teach these concepts IN ORDER, one per response:
{chr(10).join(f'  {i+1}. {c}' for i, c in enumerate(learning_paths))}

Your CURRENT concept to teach is: **{learning_paths[0]}**
After teaching it and checking understanding, move to the next concept in the list.
"""
        system_prompt = f"""You are an expert, proactive AI tutor. The student is: {student_id}.

Long-term memory: {memory_context}
Knowledge retrieved from the Knowledge Graph: {retrieval_context}
{plan_section}
TEACHING RULES — follow these strictly at ALL TIMES:
1. You are a TEACHER, not a chatbot. When the student signals they are ready (says "yes", "ok", "lets start", "next", etc.), DO NOT ask them what topic to start with. IMMEDIATELY begin teaching the next logical piece of content.
2. If an ACTIVE LEARNING PLAN is shown above, always teach the stated CURRENT concept first. Do not skip or reorder.
3. If the student is answering your previous 'Quick Check' question, EVALUATE their answer. If they are CORRECT, you MUST use the `update_mastery_tool` to set their mastery score to 1.0 for that concept, then congratulate them and move on to the next concept. If incorrect, correct them gently without updating mastery.
4. For every response where you introduce a new concept, TEACH something concrete using this structure:
   ### [Topic/Concept Name]
   **What it is:** [Clear one-sentence definition]
   **How it works:** [2–4 sentence explanation using simple language and analogies]
   **Example:** [A concrete, relatable real-world or technical example]
   **---**
   *Quick Check:* [Ask ONE specific question to verify the student understood]
5. After the student answers your check question, evaluate their answer, correct any errors, then move on to the NEXT sub-topic.
6. NEVER say "feel free to ask questions", "let me know if you need help", or any other passive phrases. You are always driving the lesson forward.
7. If the student asks a specific question, answer it directly and concisely with an example, then ask a follow-up check question."""

    # ------------------------------------------------------------------ #
    # Invoke LLM with full conversation history and tools
    # ------------------------------------------------------------------ #
    from src.agents.tools import update_mastery_tool
    llm_with_tools = llm.bind_tools([update_mastery_tool])
    messages = _build_messages_with_history(system_prompt, chat_history, user_input)

    print("Tutor is generating teaching response...")
    response = llm_with_tools.invoke(messages)
    
    # Process tool calls if the tutor decided to update mastery
    final_content = response.content
    if response.tool_calls:
        print(f"Tutor invoked {len(response.tool_calls)} tools for mastery update.")
        for tool_call in response.tool_calls:
            print(f" -> Calling {tool_call['name']} with args: {tool_call['args']}")
            update_mastery_tool.invoke(tool_call['args'])
        
        # If the LLM only returned a tool call and no text, we need to prompt it again 
        # to generate the congratulatory message and the next concept.
        if not final_content:
            messages.append(response) # Add the AIMessage with tool_calls
            # Add a mock ToolMessage so the LLM knows it succeeded
            from langchain_core.messages import ToolMessage
            for tc in response.tool_calls:
                messages.append(ToolMessage(content="Mastery updated successfully to 1.0.", tool_call_id=tc["id"]))
            print("Tutor generating follow-up response after tool call...")
            followup = llm_with_tools.invoke(messages)
            final_content = followup.content

    # ------------------------------------------------------------------ #
    # Update state
    # ------------------------------------------------------------------ #
    updated_chat_history = list(chat_history)
    updated_chat_history.append({"role": "user", "content": user_input})
    updated_chat_history.append({"role": "assistant", "content": final_content})

    memory_topics = state.get("affected_concepts", []) or [state.get("route", "retrieve")]
    store_memory_tool.invoke({
        "student_id": student_id,
        "memory_type": state.get("route", "retrieve"),
        "content": (
            f"User said: {user_input} | "
            f"Route: {state.get('route', 'retrieve')} | "
            f"Tutor taught: {final_content[:300]}"
        ),
        "topics": ", ".join(memory_topics),
        "importance": 0.8 if state.get("misconception_detected", False) else 0.5,
    })

    return {
        "final_response": final_content,
        "retrieved_context": retrieval_context,
        "chat_history": updated_chat_history,
    }
