import os
from dotenv import load_dotenv
from langchain_core.tools import tool

from src.graph.db import Neo4jConnection
from src.graph.student import StudentManager
from src.retrieval.search import SemanticSearch
from src.pathing.graph_adapter import GraphAdapter
from src.pathing.state import StateModeler
from src.pathing.msms import MSMSOptimizer

# ---------------------------------------------------------
# Global Initialization (for demo purposes)
# ---------------------------------------------------------
load_dotenv()
URI = os.getenv("NEO4J_URI", "")
USER = os.getenv("NEO4J_USERNAME", "")
PWD = os.getenv("NEO4J_PASSWORD", "")

def get_connection():
    return Neo4jConnection(URI, USER, PWD)

# ---------------------------------------------------------
# LangChain Tools
# ---------------------------------------------------------

@tool
def update_mastery_tool(student_id: str, concept_id: str, mastery_score: float) -> str:
    """
    Updates the Neo4j Graph with a new mastery score (0.0 to 1.0) for a specific concept.
    Call this when a student demonstrates understanding or misunderstanding of a concept.
    """
    conn = get_connection()
    manager = StudentManager(conn)
    manager.update_mastery(student_id, concept_id, mastery_score)
    conn.close()
    return f"Successfully updated mastery for {student_id} on {concept_id} to {mastery_score}"


@tool
def semantic_search_tool(query: str, student_id: str) -> str:
    """
    Searches the Neo4j knowledge graph using vector embeddings to find concepts relevant to a natural language query.
    Also retrieves the student's mastery of those concepts.
    """
    conn = get_connection()
    searcher = SemanticSearch(conn)
    results = searcher.search_and_personalize(query, student_id, top_k=3)
    conn.close()
    
    if not results:
        return "No relevant concepts found."
    
    summary = "Found the following related concepts:\n"
    for r in results:
        summary += f"- {r['concept']} (Similarity: {r['similarity']:.2f}, Student Mastery: {r['mastery']:.2f})\n"
    return summary


@tool
def generate_paths_tool(student_id: str) -> str:
    """
    Calculates the mathematically optimal learning paths for a student based on what they already know (Sources)
    and what they need to learn (Sinks), considering concept difficulty and fanout.
    """
    conn = get_connection()
    try:
        # Load Graph
        adapter = GraphAdapter(conn)
        nx_graph = adapter.get_networkx_graph()
        
        # Load State
        manager = StudentManager(conn)
        modeler = StateModeler(manager)
        mastery = manager.get_student_mastery(student_id)
        sources, sinks = modeler.get_sources_and_sinks(student_id, list(nx_graph.nodes()))
        
        # Calculate Paths
        optimizer = MSMSOptimizer(nx_graph, sources, sinks, mastery)
        paths = optimizer.greedy_set_cover()
        
        if not paths:
            return "No valid learning paths could be generated."
            
        result = "Calculated Optimal Paths:\n"
        for i, path in enumerate(paths, 1):
            names = [nx_graph.nodes[n]['name'] for n in path]
            result += f"{i}. {' -> '.join(names)}\n"
            
        return result
    finally:
        conn.close()
