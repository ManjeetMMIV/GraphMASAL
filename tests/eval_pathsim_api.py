"""
Evaluation 3 (API Domain): PathSim + MSMS Ablation on REST API Design
====================================================================
Compares MSMS Optimizer vs BFS Baseline on the REST API Design curriculum:
  1. CRUD & Request Design
  2. Safe Retries & Long-Running Jobs
  3. AI Streaming & LLM APIs

Usage:
    uv run python tests/eval_pathsim_api.py
"""
import os
import sys
import json
import logging
import warnings
from dotenv import load_dotenv

import networkx as nx

warnings.filterwarnings("ignore")
logging.getLogger("neo4j").setLevel(logging.ERROR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph.db import Neo4jConnection
from src.graph.student import StudentManager
from src.pathing.graph_adapter import GraphAdapter
from src.pathing.state import StateModeler
from src.pathing.msms import MSMSOptimizer
from src.evaluation.pathsim import compute_pathsim

REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "eval_pathsim_api_report.json")

EXPERT_SCENARIOS = {
    "crud_and_request_design": {
        "description": "Student knows HTTP Methods -> wants to learn Request & Response Payload Design",
        "known": {"http-methods": 0.95},
        "target_sink": "request-response-design",
        "expert_path": ["http-methods", "resource-naming", "request-response-design"],
    },
    "safe_retries_and_jobs": {
        "description": "Student knows HTTP Methods -> wants to learn Asynchronous Long-Running Jobs",
        "known": {"http-methods": 0.95},
        "target_sink": "long-running-jobs",
        "expert_path": ["http-methods", "idempotency-and-retries", "long-running-jobs"],
    },
    "ai_streaming_apis": {
        "description": "Student knows Long-Running Jobs -> wants to learn AI & Event Streaming APIs",
        "known": {"http-methods": 0.95, "idempotency-and-retries": 0.90, "long-running-jobs": 0.95},
        "target_sink": "ai-and-streaming-apis",
        "expert_path": ["long-running-jobs", "ai-and-streaming-apis"],
    },
}


def bfs_shortest_paths(G: nx.DiGraph, sources: list[str], sinks: list[str]) -> list[list[str]]:
    paths = []
    for sink in sinks:
        best_path = None
        best_len = float("inf")
        for source in sources:
            try:
                path = nx.shortest_path(G, source, sink)
                if len(path) < best_len:
                    best_path = path
                    best_len = len(path)
            except nx.NetworkXNoPath:
                continue
        if best_path:
            paths.append(best_path)
    return paths


def path_efficiency(expert_path: list[str], generated_path: list[str]) -> float:
    if not generated_path:
        return 0.0
    return round(len(expert_path) / len(generated_path), 4)


def prerequisite_integrity(G: nx.DiGraph, path: list[str]) -> float:
    if len(path) < 2:
        return 1.0
    valid = 0
    total = len(path) - 1
    for i in range(total):
        if G.has_edge(path[i], path[i + 1]) or nx.has_path(G, path[i], path[i + 1]):
            valid += 1
    return round(valid / total, 4) if total > 0 else 1.0


def run_scenario(scenario_name: str, scenario: dict, G: nx.DiGraph, manager: StudentManager, method: str) -> dict:
    student_id = f"eval_api_{method}_{scenario_name}"
    manager.create_student_from_dict(student_id, student_id, {})

    for node in G.nodes():
        manager.update_mastery(student_id, node, 0.0)

    for concept_id, score in scenario["known"].items():
        manager.update_mastery(student_id, concept_id, score)

    mastery = manager.get_student_mastery(student_id)
    modeler = StateModeler(manager)
    sources, _ = modeler.get_sources_and_sinks(student_id, list(G.nodes()))
    sinks = [scenario["target_sink"]]

    if method == "msms":
        optimizer = MSMSOptimizer(G, sources, sinks, mastery)
        generated_paths = optimizer.greedy_set_cover()
    else:
        generated_paths = bfs_shortest_paths(G, sources, sinks)

    expert_path = scenario["expert_path"]
    if not generated_paths:
        return {
            "scenario": scenario_name,
            "method": method,
            "description": scenario["description"],
            "expert_path": expert_path,
            "generated_path": [],
            "pathsim": 0.0,
            "node_similarity": 0.0,
            "edge_similarity": 0.0,
            "sequence_similarity": 0.0,
            "path_efficiency": 0.0,
            "prerequisite_integrity": 0.0,
            "sink_reached": False,
        }

    gen_path = generated_paths[0]
    breakdown = compute_pathsim(gen_path, expert_path)

    return {
        "scenario": scenario_name,
        "method": method,
        "description": scenario["description"],
        "expert_path": [G.nodes[n].get("name", n) for n in expert_path],
        "expert_path_ids": expert_path,
        "generated_path": [G.nodes[n].get("name", n) for n in gen_path],
        "generated_path_ids": gen_path,
        "pathsim": breakdown.total_score,
        "node_similarity": breakdown.node_similarity,
        "edge_similarity": breakdown.edge_similarity,
        "sequence_similarity": breakdown.sequence_similarity,
        "path_efficiency": path_efficiency(expert_path, gen_path),
        "prerequisite_integrity": prerequisite_integrity(G, gen_path),
        "sink_reached": scenario["target_sink"] in gen_path,
    }


def main():
    print("=" * 65)
    print("  GraphMASAL — PathSim Ablation on REST API Design")
    print("=" * 65)

    conn = Neo4jConnection(
        os.getenv("NEO4J_URI", ""),
        os.getenv("NEO4J_USERNAME", ""),
        os.getenv("NEO4J_PASSWORD", ""),
    )
    manager = StudentManager(conn)
    adapter = GraphAdapter(conn)
    G = adapter.get_networkx_graph()

    print(f"  Graph: {G.number_of_nodes()} concepts, {G.number_of_edges()} prerequisites")
    print(f"  Scenarios: {len(EXPERT_SCENARIOS)}\n")

    msms_results = []
    bfs_results = []

    for name, scenario in EXPERT_SCENARIOS.items():
        print(f"  Scenario: {scenario['description']}")
        msms_r = run_scenario(name, scenario, G, manager, "msms")
        bfs_r = run_scenario(name, scenario, G, manager, "bfs")

        msms_results.append(msms_r)
        bfs_results.append(bfs_r)

        print(f"    MSMS Path : {' -> '.join(msms_r['generated_path'])}")
        print(f"    BFS Path  : {' -> '.join(bfs_r['generated_path'])}")
        print(f"    Expert    : {' -> '.join(msms_r['expert_path'])}")
        print(f"    PathSim   : MSMS={msms_r['pathsim']:.4f}  BFS={bfs_r['pathsim']:.4f}")
        print()

    conn.close()

    def avg(items, key):
        vals = [i[key] for i in items]
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    metrics_keys = ["pathsim", "node_similarity", "edge_similarity", "sequence_similarity",
                    "path_efficiency", "prerequisite_integrity"]

    summary = {"msms": {}, "bfs": {}, "delta_msms_minus_bfs": {}}
    for key in metrics_keys:
        summary["msms"][key] = avg(msms_results, key)
        summary["bfs"][key] = avg(bfs_results, key)
        summary["delta_msms_minus_bfs"][key] = round(
            summary["msms"][key] - summary["bfs"][key], 4
        )

    summary["msms"]["sink_coverage"] = sum(1 for r in msms_results if r["sink_reached"]) / len(msms_results)
    summary["bfs"]["sink_coverage"] = sum(1 for r in bfs_results if r["sink_reached"]) / len(bfs_results)

    print("=" * 65)
    print("  PATHSIM ABLATION RESULTS (REST API DESIGN)")
    print("=" * 65)
    print(f"\n  {'Metric':<25} {'MSMS':>10} {'BFS':>10} {'Delta':>10}")
    print("  " + "-" * 55)
    for key in metrics_keys:
        m = summary["msms"][key]
        b = summary["bfs"][key]
        d = summary["delta_msms_minus_bfs"][key]
        print(f"  {key:<25} {m:>10.4f} {b:>10.4f} {d:>+10.4f}")

    print(f"  {'sink_coverage':<25} {summary['msms']['sink_coverage']:>10.2%} {summary['bfs']['sink_coverage']:>10.2%}")
    print("=" * 65)

    report = {
        "domain": "REST API Design",
        "summary": summary,
        "msms_per_scenario": msms_results,
        "bfs_per_scenario": bfs_results,
    }
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Full report saved -> {os.path.abspath(REPORT_PATH)}")


if __name__ == "__main__":
    main()
