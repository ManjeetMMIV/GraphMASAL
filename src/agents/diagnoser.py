from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.llm import get_chat_model
from src.agents.state import AgentState
from src.agents.tools import update_mastery_tool, hybrid_retrieval_tool

def diagnoser_node(state: AgentState):
    """
    The Diagnoser Agent.
    Analyzes the user's input to determine if they are struggling with a concept.
    If so, it uses the semantic_search_tool to find the exact concept, 
    and then the update_mastery_tool to reduce their score.
    """
    print("\n--- [Diagnoser Agent] Executing ---")
    
    # We use a tool-calling LLM to automate the process
    # binding the search and update tools directly to it.
    llm = get_chat_model(temperature=0)
    llm_with_tools = llm.bind_tools([hybrid_retrieval_tool, update_mastery_tool])
    
    system_prompt = f"""
    You are the Diagnostic Engine of an AI Tutor.
    The current student's ID is: {state['student_id']}.
    Prior long-term memory for this student:
    {state.get('long_term_memory', 'No relevant long-term memory found.')}
    
    Your job is to analyze the student's input. 
    If the student demonstrates a severe misunderstanding of a concept, or explicitly states they failed on a topic (e.g., "Paging", "File Systems", "Locks"), you MUST invoke the `update_mastery_tool`.
    
    Pass the concept ID as a lowercased, hyphenated string (e.g., 'paging', 'file-systems', 'locks') and set the mastery score to 0.0.
    DO NOT just search for the concept. You MUST invoke `update_mastery_tool`.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_input"])
    ]
    
    response = llm_with_tools.invoke(messages)
    
    misconception_detected = False
    affected_concepts = []
    
    # Check if the LLM decided to call tools
    if response.tool_calls:
        print(f"Diagnoser invoked {len(response.tool_calls)} tools.")
        for tool_call in response.tool_calls:
            print(f" -> Calling {tool_call['name']} with args: {tool_call['args']}")
            
            # Extract concept ID regardless of which tool it decided to call, as a fallback
            concept_id = None
            if 'concept_id' in tool_call['args']:
                concept_id = tool_call['args']['concept_id']
            elif 'query' in tool_call['args']:
                # rough fallback if it just searched "Paging"
                concept_id = tool_call['args']['query'].lower().replace(" ", "-")
                if "paging" in concept_id: concept_id = "paging"
                elif "file" in concept_id: concept_id = "file-systems"
                
            if concept_id:
                misconception_detected = True
                affected_concepts.append(concept_id)
                
                # Force the execution of the update mastery tool
                print(f"Diagnoser forcing Neo4j mastery update to 0.0 for {concept_id}")
                update_mastery_tool.invoke({"student_id": state['student_id'], "concept_id": concept_id, "mastery_score": 0.0})

    else:
        print("Diagnoser: No misconceptions detected.")
        
    # Update the state
    return {
        "misconception_detected": misconception_detected,
        "affected_concepts": affected_concepts
    }
