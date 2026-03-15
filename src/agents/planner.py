from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.state import AgentState
from src.agents.tools import generate_paths_tool

def planner_node(state: AgentState):
    """
    The Planner Agent.
    If the Diagnoser detected a misconception, the Planner's job is to invoke the Python MSMS logic
    to recalculate the optimal learning path for the student.
    """
    print("\n--- [Planner Agent] Executing ---")
    
    if not state.get("misconception_detected", False):
        print("Planner skipped: No misconceptions detected.")
        return {"learning_paths": []}
    
    # We call the mathematical msms generator tool directly since we know we need paths
    print(f"Misconception detected on {state.get('affected_concepts')}. Re-calculating MSMS learning paths...")
    
    path_result = generate_paths_tool.invoke({"student_id": state['student_id']})
    
    # The output is a formatted string of calculated optimal paths.
    # For LangGraph state, we can just save it as a List of strings temporarily, 
    # or pass the raw string for the Tutor to read. 
    # To keep it simple, we'll store the raw string wrapped in a list.
    paths_list = path_result.split("\n")
    
    print(f"Planner generated new paths.")
    
    return {
        "learning_paths": paths_list
    }
