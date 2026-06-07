"""
Routing Accuracy & Latency-per-Route Evaluation
================================================
Measures two metrics WITHOUT modifying any pipeline code:

1. **Routing Accuracy** — % of queries routed to the correct agent.
   Each test case carries a ground-truth label (which agent *should* handle it).

2. **Latency per Route** — average extra time (ms) the router adds per query.
   Important for showing the system is practical / deployable.

Usage:
    uv run python tests/test_router_metrics.py
"""
import os
import sys
import time
import json
import logging
import warnings
from dotenv import load_dotenv

# Suppress verbose Neo4j warnings and logs
warnings.filterwarnings("ignore")
logging.getLogger("neo4j").setLevel(logging.ERROR)

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# pyrefly: ignore [missing-import]
from src.agents.router_agent import router_node

# ─────────────────────────────────────────────────────────────
# Ground-truth test dataset
# Each entry: (user_input, expected_route)
#   "diagnose"  → user is confused / struggling / needs remediation
#   "retrieve"  → user wants an explanation / definition / example
# ─────────────────────────────────────────────────────────────
TEST_CASES = [
    # ── Should route to DIAGNOSE ──────────────────────────────
    {
        "user_input": "I'm stuck on this problem and can't figure out what I'm doing wrong.",
        "expected_route": "diagnose",
    },
    {
        "user_input": "I keep failing the quiz on memory virtualization, how can I improve?",
        "expected_route": "diagnose",
    },
    {
        "user_input": "I don't understand why page faults happen, I'm so confused.",
        "expected_route": "diagnose",
    },
    {
        "user_input": "I misunderstood how TLBs work. Can you help me learn the right way?",
        "expected_route": "diagnose",
    },
    {
        "user_input": "I made a mistake on the context switching question. What should I learn next?",
        "expected_route": "diagnose",
    },
    # ── Should route to RETRIEVE ──────────────────────────────
    {
        "user_input": "What is the difference between paging and segmentation?",
        "expected_route": "retrieve",
    },
    {
        "user_input": "Explain how round-robin scheduling works with an example.",
        "expected_route": "retrieve",
    },
    {
        "user_input": "Can you define what a semaphore is?",
        "expected_route": "retrieve",
    },
    {
        "user_input": "Give me an overview of how virtual memory is implemented.",
        "expected_route": "retrieve",
    },
    {
        "user_input": "What are the key properties of a deadlock?",
        "expected_route": "retrieve",
    },
]

# Load dataset from file if available
DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", "router_eval_dataset.json")
if os.path.exists(DATASET_PATH):
    try:
        with open(DATASET_PATH, "r") as f:
            TEST_CASES = json.load(f)
        print(f"Loaded {len(TEST_CASES)} dense test cases from {DATASET_PATH}")
    except Exception as e:
        print(f"Failed to load dataset: {e}. Using fallback 10 test cases.")
else:
    print("Using default 10 hardcoded test cases.")
    
STUDENT_ID = "test_student_metrics"


def evaluate_routing():
    """Run every test case through the real router and collect metrics."""
    results = []
    correct = 0

    for idx, case in enumerate(TEST_CASES, 1):
        state = {
            "user_input": case["user_input"],
            "student_id": STUDENT_ID,
            "chat_history": [],
        }

        # ── Measure latency ──────────────────────────────────
        t0 = time.perf_counter()
        output = router_node(state)
        latency_ms = (time.perf_counter() - t0) * 1000

        predicted = output.get("route", "retrieve")
        expected = case["expected_route"]
        is_correct = predicted == expected
        if is_correct:
            correct += 1

        results.append({
            "id": idx,
            "query": case["user_input"],
            "expected": expected,
            "predicted": predicted,
            "correct": is_correct,
            "reason": output.get("route_reason", ""),
            "latency_ms": round(latency_ms, 2),
        })

        status = "PASS" if is_correct else "FAIL"
        print(f"  [{status}] #{idx}  expected={expected:<9} predicted={predicted:<9}  ({latency_ms:.0f} ms)")

    # ── Aggregate metrics ─────────────────────────────────────
    total = len(results)
    accuracy = (correct / total) * 100 if total else 0
    avg_latency = sum(r["latency_ms"] for r in results) / total if total else 0
    min_latency = min(r["latency_ms"] for r in results) if results else 0
    max_latency = max(r["latency_ms"] for r in results) if results else 0

    diagnose_latencies = [r["latency_ms"] for r in results if r["predicted"] == "diagnose"]
    retrieve_latencies = [r["latency_ms"] for r in results if r["predicted"] == "retrieve"]

    metrics = {
        "total_queries": total,
        "correct": correct,
        "routing_accuracy_pct": round(accuracy, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "min_latency_ms": round(min_latency, 2),
        "max_latency_ms": round(max_latency, 2),
        "avg_latency_diagnose_ms": round(sum(diagnose_latencies) / len(diagnose_latencies), 2) if diagnose_latencies else None,
        "avg_latency_retrieve_ms": round(sum(retrieve_latencies) / len(retrieve_latencies), 2) if retrieve_latencies else None,
        "per_query_results": results,
    }
    return metrics


def main():
    print("=" * 60)
    print("  GraphMASAL — Router Accuracy & Latency Evaluation")
    print("=" * 60)
    print(f"\n  Student ID : {STUDENT_ID}")
    print(f"  Test cases : {len(TEST_CASES)}\n")

    metrics = evaluate_routing()

    print("\n" + "-" * 60)
    print("  RESULTS SUMMARY")
    print("-" * 60)
    print(f"  Routing Accuracy : {metrics['routing_accuracy_pct']}%  ({metrics['correct']}/{metrics['total_queries']})")
    print(f"  Avg Latency      : {metrics['avg_latency_ms']} ms")
    print(f"  Min / Max        : {metrics['min_latency_ms']} ms / {metrics['max_latency_ms']} ms")
    if metrics["avg_latency_diagnose_ms"] is not None:
        print(f"  Avg (diagnose)   : {metrics['avg_latency_diagnose_ms']} ms")
    if metrics["avg_latency_retrieve_ms"] is not None:
        print(f"  Avg (retrieve)   : {metrics['avg_latency_retrieve_ms']} ms")
    print("-" * 60)

    # ── Save full JSON report ─────────────────────────────────
    report_path = os.path.join(os.path.dirname(__file__), "..", "data", "router_eval_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n  Full report saved -> {os.path.abspath(report_path)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
