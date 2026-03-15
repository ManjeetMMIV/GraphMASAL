from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.llm import get_chat_model
from src.agents.state import AgentState
from src.agents.tools import hybrid_retrieval_tool, store_memory_tool

def tutor_node(state: AgentState):
    """
    The Tutor Agent.
    This acts as the master controller and conversational interface for the user.
    It synthesizes the output of the Diagnoser and Planner into friendly natural language.
    """
    print("\n--- [Tutor Agent] Executing ---")
    
    llm = get_chat_model(temperature=0.7)
    memory_context = state.get("long_term_memory", "No relevant long-term memory found.")
    retrieval_context = state.get("retrieved_context", "")
    
    # Base Context
    system_prompt = f"You are a helpful, expert AI Operating Systems Tutor. The current student is: {state['student_id']}."
    system_prompt += f"\nRelevant long-term memory for continuity:\n{memory_context}\n"
    
    # Conditional logic based on earlier nodes
    if state.get("misconception_detected", False):
        affected = state.get("affected_concepts", [])
        paths = "\n".join(state.get("learning_paths", []))
        if not retrieval_context:
            retrieval_context = hybrid_retrieval_tool.invoke({
                "query": ", ".join(affected) or state["user_input"],
                "student_id": state["student_id"],
            })
        
        system_prompt += f"""
        The Diagnostic agent noticed the student struggled with the following concepts: {affected}.
        Their mastery score has been reset.
        Supporting hybrid retrieval context:
        {retrieval_context}
        
        The Planner agent mathematically generated a new optimal learning path for them to catch up:
        {paths}
        
        Your job: Write a gentle, encouraging response to the student acknowledging their mistake. 
        Gently explain that to grasp {affected}, they first need to build up their prerequisite knowledge according to the provided optimal learning path.
        Ask if they are ready to learn the first concept in the path!
        """
    else:
        print(f"Tutor invoking hybrid retrieval to answer: '{state['user_input']}'")
        retrieval_context = hybrid_retrieval_tool.invoke({"query": state['user_input'], "student_id": state['student_id']})
        
        system_prompt += f"""
        The student asked a question. Here is relevant context retrieved from the Knowledge Graph:
        {retrieval_context}
        
        Your job: Answer the student's question clearly and concisely based on this context. 
        If the student mentions missing a topic, encourage them.
        """
        
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_input"])
    ]
    
    print("Tutor is generating conversational response...")
    response = llm.invoke(messages)

    updated_chat_history = list(state.get("chat_history", []))
    updated_chat_history.append({"role": "user", "content": state["user_input"]})
    updated_chat_history.append({"role": "assistant", "content": response.content})

    memory_topics = state.get("affected_concepts", []) or [state.get("route", "retrieve")]
    memory_content = (
        f"User asked: {state['user_input']} | "
        f"Route: {state.get('route', 'retrieve')} | "
        f"Tutor response summary: {response.content[:280]}"
    )
    store_memory_tool.invoke(
        {
            "student_id": state["student_id"],
            "memory_type": state.get("route", "retrieve"),
            "content": memory_content,
            "topics": ", ".join(memory_topics),
            "importance": 0.8 if state.get("misconception_detected", False) else 0.5,
        }
    )
    
    return {
        "final_response": response.content,
        "retrieved_context": retrieval_context,
        "chat_history": updated_chat_history,
    }
