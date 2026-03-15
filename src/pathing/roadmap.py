from __future__ import annotations

from typing import Any

from src.graph.student import StudentManager
from src.pathing.graph_adapter import GraphAdapter
from src.pathing.msms import MSMSOptimizer
from src.pathing.state import StateModeler


def compute_student_roadmap(conn, student_id: str) -> dict[str, Any]:
    adapter = GraphAdapter(conn)
    nx_graph = adapter.get_networkx_graph()

    manager = StudentManager(conn)
    modeler = StateModeler(manager)
    mastery = manager.get_student_mastery(student_id)
    sources, sinks = modeler.get_sources_and_sinks(student_id, list(nx_graph.nodes()))

    optimizer = MSMSOptimizer(nx_graph, sources, sinks, mastery)
    paths = optimizer.greedy_set_cover()

    path_details: list[dict[str, Any]] = []
    for idx, path in enumerate(paths, start=1):
        path_details.append(
            {
                "index": idx,
                "node_ids": path,
                "names": [nx_graph.nodes[node].get("name", node) for node in path],
            }
        )

    return {
        "graph": nx_graph,
        "mastery": mastery,
        "sources": sources,
        "sinks": sinks,
        "paths": path_details,
    }


def format_roadmap_lines(roadmap: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for path in roadmap.get("paths", []):
        lines.append(f"{path['index']}. {' -> '.join(path['names'])}")
    return lines