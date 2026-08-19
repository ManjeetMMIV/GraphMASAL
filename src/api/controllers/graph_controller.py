from fastapi import HTTPException
from pydantic import BaseModel

from src.api.dependencies import get_neo4j_connection

class SelectPlanRequest(BaseModel):
    student_id: str
    session_id: str
    plan_id: str
    concept_sequence: list[str]

class ComputePathRequest(BaseModel):
    student_id: str
    source_ids: list
    sink_ids: list

def get_roadmap_logic(student_id: str, session_id: str = ""):
    if not session_id:
        return {"paths": []}
        
    try:
        from src.storage.qa_store import get_db as _qa_get_db
        session_doc = _qa_get_db()["sessions"].find_one({"session_id": session_id})
        if not session_doc:
            return {"paths": []}
            
        active_plan = session_doc.get("active_plan", [])
        if not active_plan:
            return {"paths": []}
            
        conn = get_neo4j_connection()
        if not conn:
            return {"paths": [{"index": 1, "node_ids": active_plan, "names": active_plan}]}
            
        try:
            from src.pathing.graph_adapter import GraphAdapter
            adapter = GraphAdapter(conn)
            nx_graph = adapter.get_networkx_graph(student_id=student_id)
            names = [nx_graph.nodes[n].get("name", n) if n in nx_graph else n for n in active_plan]
            return {"paths": [{"index": 1, "node_ids": active_plan, "names": names}]}
        finally:
            conn.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def list_concepts_logic(student_id: str):
    conn = get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        rows = conn.query(
            """
            MATCH (s:Student {id: $student_id})-[:HAS_EXTRACTED]->(c:Concept)
            RETURN c.id AS id, c.name AS name, c.description AS desc 
            ORDER BY c.name
            """,
            {"student_id": student_id}
        )
        concepts = [{"id": r["id"], "name": r["name"], "desc": r.get("desc", "")}
                    for r in (rows or [])]
        return {"concepts": concepts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

def compute_path_logic(req: ComputePathRequest):
    conn = get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        from src.pathing.graph_adapter import GraphAdapter
        from src.pathing.msms import MSMSOptimizer

        adapter = GraphAdapter(conn)
        nx_graph = adapter.get_networkx_graph(student_id=req.student_id)

        if nx_graph.number_of_nodes() == 0:
            return {"path": [], "path_names": [], "message": f"No concept graph found for student {req.student_id}. Please upload and extract concepts first."}

        all_nodes = list(nx_graph.nodes())

        valid_sources = [nid for nid in req.source_ids if nid in all_nodes]
        valid_sinks   = [nid for nid in req.sink_ids   if nid in all_nodes]
        explicit_sources = set(valid_sources)

        implicit_sources = [n for n in all_nodes if nx_graph.in_degree(n) == 0]
        for n in implicit_sources:
            if n not in valid_sources:
                valid_sources.append(n)

        if not valid_sinks:
            valid_sinks = [n for n in all_nodes if nx_graph.out_degree(n) == 0]

        valid_sinks = [s for s in valid_sinks if s not in explicit_sources]

        if not valid_sinks:
            return {"path": [], "path_names": [], "message": "Nothing left to learn — all target concepts are already marked as known."}

        mastery = {nid: 1.0 for nid in explicit_sources}

        optimizer = MSMSOptimizer(nx_graph, valid_sources, valid_sinks, mastery)
        paths = optimizer.greedy_set_cover()

        flat_path: list[str] = []
        seen: set[str] = set()
        for path in paths:
            for node in path:
                if node not in seen and node not in explicit_sources:
                    flat_path.append(node)
                    seen.add(node)

        path_names = [nx_graph.nodes[nid].get("name", nid) for nid in flat_path]

        return {
            "path": flat_path,
            "path_names": path_names,
            "total_concepts": len(flat_path),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

def select_plan_logic(req: SelectPlanRequest):
    from src.storage.qa_store import get_db
    db = get_db()
    db["sessions"].update_one(
        {"session_id": req.session_id},
        {"$set": {
            "active_plan": req.concept_sequence,
            "plan_id": req.plan_id,
        }},
    )
    return {"status": "ok", "plan_id": req.plan_id, "concept_count": len(req.concept_sequence)}

def get_knowledge_graph_logic(student_id: str, session_id: str = ""):
    conn = get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        from src.pathing.graph_adapter import GraphAdapter
        adapter = GraphAdapter(conn)
        nx_graph = adapter.get_networkx_graph(student_id=student_id)

        mastery_rows = conn.query(
            """
            MATCH (s:Student {id: $sid})-[r:HAS_MASTERY_OF]->(c:Concept)
            RETURN c.id AS id, coalesce(r.score, 0.0) AS score
            """,
            {"sid": student_id}
        )
        mastery_map = {row["id"]: row["score"] for row in (mastery_rows or [])}

        nodes = [
            {
                "id": n,
                "name": nx_graph.nodes[n].get("name", n),
                "desc": nx_graph.nodes[n].get("description", ""),
                "mastery": mastery_map.get(n, 0.0),
            }
            for n in nx_graph.nodes()
        ]
        edges = [
            {"source": u, "target": v}
            for u, v in nx_graph.edges()
        ]

        active_plan = []
        if session_id:
            try:
                from src.storage.qa_store import get_db as _qa_get_db
                session_doc = _qa_get_db()["sessions"].find_one({"session_id": session_id})
                if session_doc:
                    active_plan = session_doc.get("active_plan", [])
            except Exception:
                pass

        current_concept = None
        mastered_in_plan = []
        upcoming_in_plan = []
        for cid in active_plan:
            score = mastery_map.get(cid, 0.0)
            if score >= 0.8:
                mastered_in_plan.append(cid)
            elif current_concept is None:
                current_concept = cid
            else:
                upcoming_in_plan.append(cid)

        justification = {
            "mastered_count": len(mastered_in_plan),
            "mastered_concepts": mastered_in_plan,
            "current_concept": current_concept,
            "upcoming_count": len(upcoming_in_plan),
            "reason": (
                f"{len(mastered_in_plan)} concept(s) already mastered and skipped. "
                f"Now focusing on: '{mastery_map and next((n['name'] for n in nodes if n['id'] == current_concept), current_concept) or 'N/A'}'."
                if current_concept else
                "All concepts in the learning plan have been mastered! 🎉"
            )
        }

        return {
            "nodes": nodes,
            "edges": edges,
            "active_plan": active_plan,
            "current_concept": current_concept,
            "justification": justification,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
