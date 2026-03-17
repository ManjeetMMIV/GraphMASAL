import os
import logging

from src.agents.state import AgentState
from src.agents.tools import generate_paths_tool


def planner_node(state: AgentState):
    """
    The Planner Agent — two modes:
    1. Misconception remediation: recalculate MSMS path when a misconception is detected.
    2. Active plan progression: when the student has a selected plan, return the
       next concept(s) to teach as learning_paths so the Tutor follows the plan.
    """
    print("\n--- [Planner Agent] Executing ---")

    active_plan = state.get("active_plan", [])
    misconception = state.get("misconception_detected", False)

    # Mode 1: Misconception remediation (original behavior)
    if misconception:
        affected = state.get("affected_concepts", [])
        print(f"Misconception detected on {affected}. Re-calculating MSMS paths...")
        try:
            path_result = generate_paths_tool.invoke({"student_id": state["student_id"]})
            paths_list = [p for p in path_result.split("\n") if p.strip()]
        except Exception as e:
            logging.warning(f"Planner: generate_paths_tool failed: {e}")
            paths_list = []
        print(f"Planner generated {len(paths_list)} remediation paths.")
        return {"learning_paths": paths_list}

    # Mode 2: Active plan — resolve concept IDs → names for the Tutor
    if active_plan:
        try:
            from src.graph.db import Neo4jConnection as _Neo4jConn
            _conn = _Neo4jConn(
                os.getenv("NEO4J_URI", ""),
                os.getenv("NEO4J_USERNAME", ""),
                os.getenv("NEO4J_PASSWORD", ""),
            )
            # Fetch names and mastery scores for all concepts in the plan
            rows = _conn.query(
                """
                UNWIND $ids AS cid 
                MATCH (c:Concept {id: cid}) 
                OPTIONAL MATCH (s:Student {id: $sid})-[r:HAS_MASTERY_OF]->(c)
                RETURN c.id AS id, c.name AS name, coalesce(r.score, 0.0) AS score
                """,
                {"ids": active_plan, "sid": state["student_id"]},
            )
            _conn.close()
            
            # Filter out concepts that are already mastered (score >= 0.8)
            unmastered_ids = []
            id_to_name = {}
            for r in (rows or []):
                id_to_name[r["id"]] = r["name"]
                
            for cid in active_plan:
                # Find the row for this concept to check its score (default 0.0 if not found)
                row = next((r for r in (rows or []) if r["id"] == cid), None)
                score = row["score"] if row else 0.0
                if score < 0.8:
                    unmastered_ids.append(cid)
            
            if not unmastered_ids:
                print("Planner: All concepts in the active plan are mastered!")
                return {"learning_paths": ["The student has mastered the entire active plan! Congratulations!"]}
                
            # Take the next up to 10 unmastered concepts
            next_ids = unmastered_ids[:10]
            plan_names = [id_to_name.get(cid, cid) for cid in next_ids]
            print(f"Planner active_plan progression → next unmastered: {plan_names}")
            return {"learning_paths": plan_names}
        except Exception as e:
            logging.warning(f"Planner: failed to resolve and filter concept names: {e}")
            return {"learning_paths": active_plan[:10]}

    print("Planner: no misconception and no active plan — nothing to do.")
    return {"learning_paths": []}
