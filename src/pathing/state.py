from typing import List, Tuple
from src.graph.student import StudentManager

class StateModeler:
    def __init__(self, student_manager: StudentManager, threshold_known: float = 0.8, threshold_unknown: float = 0.5):
        self.manager = student_manager
        self.threshold_known = threshold_known
        self.threshold_unknown = threshold_unknown

    def get_sources_and_sinks(self, student_id: str, all_concepts: List[str]) -> Tuple[List[str], List[str]]:
        """
        Calculates the sources (concepts the student knows) and 
        sinks (concepts the student needs to learn).
        """
        mastery = self.manager.get_student_mastery(student_id)
        
        sources = []
        sinks = []
        
        for concept_id in all_concepts:
            # If the concept isn't in mastery, treat it as unknown (0.0)
            score = mastery.get(concept_id, 0.0)
            
            if score >= self.threshold_known:
                sources.append(concept_id)
            elif score <= self.threshold_unknown:
                sinks.append(concept_id)
                
        return sources, sinks

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from src.graph.db import Neo4jConnection
    from src.pathing.graph_adapter import GraphAdapter
    
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")

    if uri and user and pwd:
        conn = Neo4jConnection(uri, user, pwd)
        adapter = GraphAdapter(conn)
        G = adapter.get_networkx_graph()
        
        manager = StudentManager(conn)
        modeler = StateModeler(manager)
        
        # Test Alice
        sources, sinks = modeler.get_sources_and_sinks("student_123", list(G.nodes()))
        
        print("\nStudent state analysis for Alice:")
        print(f"Sources (Known Concepts): {sources}")
        print(f"Sinks (Unknown Concepts): {sinks}")
        
        conn.close()
