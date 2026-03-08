"""
Phase 5.1: Scenario Testing
Manually sets a student profile in Neo4j and asserts the paths generated
by MSMS are logically correct (match the expected prerequisite chain).
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

# ---- Test Configuration ----
STUDENT_ID = "test_student_scenario"
# The student knows the very basics, and nothing else
KNOWN_CONCEPTS = {
    "computer-architecture": 0.95
}
# We want the system to learn Process Scheduling — which requires:
#   - Computer Architecture -> CPU Virtualization -> Processes -> Process Scheduling
EXPECTED_PATH = ["computer-architecture", "cpu-virtualization", "processes", "scheduling"]
TARGET_SINK = "scheduling"

def run_scenario_test():
    uri = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USERNAME", "")
    pwd = os.getenv("NEO4J_PASSWORD", "")
    conn = Neo4jConnection(uri, user, pwd)
    
    manager = StudentManager(conn)
    adapter = GraphAdapter(conn)
    G = adapter.get_networkx_graph()
    
    # --- Setup the test student ---
    print("\n[Setup] Creating test student and initializing mastery...")
    manager.create_student_from_dict(STUDENT_ID, "TestStudent", {})
    
    # Set all concepts to "unknown" initially
    for node in G.nodes():
        manager.update_mastery(STUDENT_ID, node, 0.0)
    
    # Only the known concepts get a high mastery score
    for concept_id, score in KNOWN_CONCEPTS.items():
        manager.update_mastery(STUDENT_ID, concept_id, score)

    print(f"[Setup] Student '{STUDENT_ID}' knows only: {list(KNOWN_CONCEPTS.keys())}")
    print(f"[Test] Goal: Learn '{TARGET_SINK}'")

    # --- Run MSMS ---
    mastery = manager.get_student_mastery(STUDENT_ID)
    modeler = StateModeler(manager)
    sources, sinks = modeler.get_sources_and_sinks(STUDENT_ID, list(G.nodes()))
    
    capped_sinks = [TARGET_SINK]  # Focus only on our test's specific target sink
    
    optimizer = MSMSOptimizer(G, sources, capped_sinks, mastery)
    optimal_paths = optimizer.greedy_set_cover()
    
    print(f"\n[Result] MSMS generated {len(optimal_paths)} path(s):")
    all_passed = True
    for idx, path in enumerate(optimal_paths, 1):
        names = [G.nodes[n]["name"] for n in path]
        print(f"  Path {idx}: {' -> '.join(names)}")
        
        # --- Assert the target sink is reached via the correct prerequisites ---
        if TARGET_SINK in path:
            # Check every concept in EXPECTED_PATH is a subset of the generated path
            generated_set = set(path)
            expected_set = set(EXPECTED_PATH)
            if expected_set.issubset(generated_set):
                print(f"\n[PASS] ✓ Generated path correctly covers expected prerequisite chain: {EXPECTED_PATH}")
            else:
                missing = expected_set - generated_set
                print(f"\n[FAIL] ✗ Path is missing expected prerequisites: {missing}")
                all_passed = False
    
    conn.close()
    return all_passed

if __name__ == "__main__":
    success = run_scenario_test()
    print("\n" + "="*50)
    if success:
        print("All scenario tests PASSED.")
    else:
        print("Some scenario tests FAILED.")
    print("="*50)
