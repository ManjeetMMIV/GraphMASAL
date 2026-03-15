"""
Phase 5.2: Programmatic Validation - PathSim Metric
Evaluates AI-generated paths against expert paths using a weighted combination of:
1. Node overlap
2. Edge overlap
3. Sequence similarity via normalized Levenshtein distance
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.getcwd())

from src.graph.db import Neo4jConnection
from src.graph.student import StudentManager
from src.pathing.graph_adapter import GraphAdapter
from src.pathing.state import StateModeler
from src.pathing.msms import MSMSOptimizer
from src.evaluation.pathsim import compute_pathsim

# -------------------------------------------------------
# Expert-defined "ground truth" paths for each scenario.
# These represent what a human OS professor would prescribe.
# -------------------------------------------------------
EXPERT_PATHS = {
    "scenario_scheduling": {
        "description": "Student knows Computer Architecture, wants to learn Process Scheduling",
        "known": {"computer-architecture": 0.95},
        "target_sink": "scheduling",
        "expert_path": ["computer-architecture", "cpu-virtualization", "processes", "scheduling"]
    },
    "scenario_file_systems": {
        "description": "Student knows Computer Architecture, wants to learn File Systems",
        "known": {"computer-architecture": 0.95},
        "target_sink": "file-systems",
        "expert_path": ["computer-architecture", "persistence", "file-systems"]
    },
    "scenario_locks": {
        "description": "Student knows Processes and Memory Virtualization, wants to learn Locks",
        "known": {"computer-architecture": 0.95, "processes": 0.90, "memory-virtualization": 0.90},
        "target_sink": "locks",
        "expert_path": ["processes", "concurrency", "threads", "locks"]
    }
}

def run_pathsim_evaluation():
    uri = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USERNAME", "")
    pwd = os.getenv("NEO4J_PASSWORD", "")
    conn = Neo4jConnection(uri, user, pwd)

    manager = StudentManager(conn)
    adapter = GraphAdapter(conn)
    G = adapter.get_networkx_graph()

    results = []
    print("\n=== PathSim Evaluation ===\n")

    for scenario_name, scenario in EXPERT_PATHS.items():
        print(f"Scenario: {scenario['description']}")
        
        # Setup a fresh student for this scenario
        student_id = f"eval_{scenario_name}"
        manager.create_student_from_dict(student_id, student_id, {})
        
        # Set all concepts to 0 initially
        for node in G.nodes():
            manager.update_mastery(student_id, node, 0.0)
        
        # Apply known mastery
        for concept_id, score in scenario["known"].items():
            manager.update_mastery(student_id, concept_id, score)
        
        # Run MSMS targeting just the single sink
        mastery = manager.get_student_mastery(student_id)
        modeler = StateModeler(manager)
        sources, _ = modeler.get_sources_and_sinks(student_id, list(G.nodes()))
        
        sinks = [scenario["target_sink"]]
        optimizer = MSMSOptimizer(G, sources, sinks, mastery)
        optimal_paths = optimizer.greedy_set_cover()
        
        if optimal_paths:
            generated_names = [G.nodes[n]['name'] for n in optimal_paths[0]]
            expert_names = [G.nodes[n]['name'] for n in scenario["expert_path"]]
            breakdown = compute_pathsim(optimal_paths[0], scenario["expert_path"])
            
            print(f"  Expert Path:    {' -> '.join(expert_names)}")
            print(f"  Generated Path: {' -> '.join(generated_names)}")
            print(
                f"  PathSim Score:  {breakdown.total_score:.4f} "
                f"{'✓' if breakdown.total_score >= 0.8 else '✗ (below threshold)'}"
            )
            print(f"  Node Overlap:   {breakdown.node_similarity:.4f}")
            print(f"  Edge Overlap:   {breakdown.edge_similarity:.4f}")
            print(f"  Sequence Sim:   {breakdown.sequence_similarity:.4f}\n")
            results.append(breakdown.total_score)
        else:
            print(f"  No path generated!\n")
            results.append(0.0)
    
    conn.close()
    
    avg_pathsim = sum(results) / len(results) if results else 0.0
    print(f"\n{'='*50}")
    print(f"Average PathSim Score: {avg_pathsim:.4f}")
    if avg_pathsim >= 0.8:
        print("System Quality: GOOD (>= 0.8 threshold)")
    else:
        print("System Quality: NEEDS IMPROVEMENT (< 0.8 threshold)")
    print(f"{'='*50}")
    return avg_pathsim

if __name__ == "__main__":
    run_pathsim_evaluation()
