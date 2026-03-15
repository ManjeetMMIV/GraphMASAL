import os
from dotenv import load_dotenv
from langchain_core.tools import tool

from src.graph.db import Neo4jConnection
from src.graph.student import StudentManager
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.search import SemanticSearch
from src.pathing.graph_adapter import GraphAdapter
from src.pathing.roadmap import compute_student_roadmap, format_roadmap_lines
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
        graph_context = r.get("graph_context", {})
        prerequisites = ", ".join(graph_context.get("prerequisites", [])) or "None"
        unlocks = ", ".join(graph_context.get("unlocks", [])) or "None"
        summary += (
            f"- {r['concept']} (Similarity: {r['similarity']:.2f}, Student Mastery: {r['mastery']:.2f}, "
            f"Rerank: {r.get('rerank_score', 0.0):.2f}, Prerequisites: {prerequisites}, Unlocks: {unlocks})\n"
        )
    return summary


@tool
def hybrid_retrieval_tool(query: str, student_id: str) -> str:
    """
    Runs hybrid retrieval by combining vector search with graph neighborhood expansion and reranking.
    """
    conn = get_connection()
    searcher = HybridRetriever(conn)
    results = searcher.retrieve(query, student_id, top_k=3)
    conn.close()

    if not results:
        return "No relevant concepts found."

    lines = ["Hybrid retrieval results:"]
    for result in results:
        neighborhood = result.get("graph_neighborhood", {})
        prerequisites = ", ".join(neighborhood.get("prerequisites", [])) or "None"
        downstream = ", ".join(neighborhood.get("downstream", [])) or "None"
        lines.append(
            f"- {result['concept']} (Hybrid: {result.get('hybrid_score', 0.0):.2f}, "
            f"Similarity: {result['similarity']:.2f}, Mastery: {result['mastery']:.2f}, "
            f"Prerequisites: {prerequisites}, Related Next Concepts: {downstream})"
        )
    return "\n".join(lines)


@tool
def recall_memory_tool(query: str, student_id: str) -> str:
    """
    Recalls relevant long-term memory for the student so the tutor can maintain context across sessions.
    """
    conn = get_connection()
    manager = StudentManager(conn)
    memories = manager.recall_memories(student_id, query, limit=3)
    conn.close()

    if not memories:
        return "No relevant long-term memory found."

    lines = ["Relevant long-term memory:"]
    for memory in memories:
        topics = ", ".join(memory.get("topics", [])) or "None"
        lines.append(
            f"- [{memory['memory_type']}] {memory['content']} (Topics: {topics}, Score: {memory['score']:.2f})"
        )
    return "\n".join(lines)


@tool
def store_memory_tool(student_id: str, memory_type: str, content: str, topics: str = "", importance: float = 0.5) -> str:
    """
    Stores a durable memory entry for the student so future turns can reuse context.
    """
    conn = get_connection()
    manager = StudentManager(conn)
    parsed_topics = [topic.strip() for topic in topics.split(",") if topic.strip()]
    manager.store_memory(student_id, memory_type, content, parsed_topics, importance)
    conn.close()
    return "Memory stored successfully."


@tool
def generate_paths_tool(student_id: str) -> str:
    """
    Calculates the mathematically optimal learning paths for a student based on what they already know (Sources)
    and what they need to learn (Sinks), considering concept difficulty and fanout.
    """
    conn = get_connection()
    try:
        roadmap = compute_student_roadmap(conn, student_id)
        if not roadmap["paths"]:
            return "No valid learning paths could be generated."

        result = "Calculated Optimal Paths:\n"
        for line in format_roadmap_lines(roadmap):
            result += f"{line}\n"

        return result
    finally:
        conn.close()
