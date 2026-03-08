from langgraph.graph import StateGraph, START, END

from src.agents.state import AgentState
from src.agents.diagnoser import diagnoser_node
from src.agents.planner import planner_node
from src.agents.tutor import tutor_node

def build_graph():
    # Initialize the graph builder using our strictly typed AgentState
    graph_builder = StateGraph(AgentState)
    
    # 1. Add all our agent nodes
    graph_builder.add_node("Diagnoser", diagnoser_node)
    graph_builder.add_node("Planner", planner_node)
    graph_builder.add_node("Tutor", tutor_node)
    
    # 2. Define the workflow order
    # START -> Diagnoser -> Planner -> Tutor -> END
    
    graph_builder.add_edge(START, "Diagnoser")
    graph_builder.add_edge("Diagnoser", "Planner")
    graph_builder.add_edge("Planner", "Tutor")
    graph_builder.add_edge("Tutor", END)
    
    # Compile it into a runnable LangChain instance
    agent_graph = graph_builder.compile()
    
    return agent_graph

if __name__ == "__main__":
    # --- Interactive Testing CLI ---
    import sys
    app = build_graph()
    
    print("\n" + "="*50)
    print("Welcome to GraphMASAL AI Tutor (Type 'quit' to exit)")
    print("="*50 + "\n")
    
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
        manager.update_mastery("student_123", "paging", 1.0)
        manager.update_mastery("student_123", "memory-virtualization", 1.0)
        manager.update_mastery("student_123", "computer-architecture", 1.0)
        conn.close()
    
    print("Ready! You can now chat with Alice's AI Tutor.\n")

    while True:
        user_input = input("[Alice]: ")
        sys.stdout.flush()
        if user_input.strip().lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        initial_state = {
            "student_id": "student_123",
            "user_input": user_input,
            "chat_history": [],
            "misconception_detected": False,
            "affected_concepts": [],
            "learning_paths": [],
            "final_response": ""
        }
        
        print("\n[System]: Thinking... (this may take 15-30s while Ollama processes)\n")
        sys.stdout.flush()
        
        try:
            # invoke() is more reliable than stream() for interactive CLI
            result = app.invoke(initial_state)
            
            tutor_msg = result.get("final_response", "")
            if tutor_msg:
                print(f"\n[AI Tutor]: {tutor_msg}\n")
            else:
                print("\n[AI Tutor]: (No response generated. Ollama may still be loading — try again.)\n")
        except Exception as e:
            print(f"\n[Error]: {e}\n")
