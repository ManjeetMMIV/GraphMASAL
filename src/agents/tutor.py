from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.state import AgentState
from src.agents.tools import semantic_search_tool

def tutor_node(state: AgentState):
    """
    The Tutor Agent.
    This acts as the master controller and conversational interface for the user.
    It synthesizes the output of the Diagnoser and Planner into friendly natural language.
    """
    print("\n--- [Tutor Agent] Executing ---")
    
    llm = ChatOllama(model="llama3.1", temperature=0.7)
    
    # Base Context
    system_prompt = f"You are a helpful, expert AI Operating Systems Tutor. The current student is: {state['student_id']}."
    
    # Conditional logic based on earlier nodes
    if state.get("misconception_detected", False):
        affected = state.get("affected_concepts", [])
        paths = "\n".join(state.get("learning_paths", []))
        
        system_prompt += f"""
        The Diagnostic agent noticed the student struggled with the following concepts: {affected}.
        Their mastery score has been reset.
        
        The Planner agent mathematically generated a new optimal learning path for them to catch up:
        {paths}
        
        Your job: Write a gentle, encouraging response to the student acknowledging their mistake. 
        Gently explain that to grasp {affected}, they first need to build up their prerequisite knowledge according to the provided optimal learning path.
        Ask if they are ready to learn the first concept in the path!
        """
    else:
        # Just answer the question using semantic search for context
        # We can simulate the tutor executing the search tool to ground its knowledge
        print(f"Tutor invoking semantic search to answer: '{state['user_input']}'")
        search_results = semantic_search_tool.invoke({"query": state['user_input'], "student_id": state['student_id']})
        
        system_prompt += f"""
        The student asked a question. Here is relevant context retrieved from the Knowledge Graph:
        {search_results}
        
        Your job: Answer the student's question clearly and concisely based on this context. 
        If the student mentions missing a topic, encourage them.
        """
        
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_input"])
    ]
    
    print("Tutor is generating conversational response...")
    response = llm.invoke(messages)
    
    return {
        "final_response": response.content
    }
