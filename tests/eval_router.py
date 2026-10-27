"""
Evaluation 1: Router Agent — Full Classification Metrics
=========================================================
Computes research-grade classification metrics for the Router Agent:
  - Confusion Matrix (2×2: diagnose vs retrieve)
  - Per-class Precision, Recall, F1
  - Macro F1 and Weighted F1
  - Cohen's Kappa (κ) — inter-rater reliability
  - Latency percentiles (p50, p95, p99)

Usage:
    uv run python tests/eval_router.py
"""
import os
import sys
import time
import json
import math
import logging
import warnings
from dotenv import load_dotenv
from collections import Counter

warnings.filterwarnings("ignore")
logging.getLogger("neo4j").setLevel(logging.ERROR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.router_agent import router_node

# ─────────────────────────────────────────────────────────
# Dataset & Arguments
# ─────────────────────────────────────────────────────────
import argparse

parser = argparse.ArgumentParser(description="Evaluate Router Agent")
parser.add_argument("--api", action="store_true", help="Use REST API Design dataset instead of OS dataset")
args, _ = parser.parse_known_args()

dataset_file = "router_eval_dataset_api.json" if args.api else "router_eval_dataset.json"
report_file = "eval_router_api_report.json" if args.api else "eval_router_report.json"

DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", dataset_file)
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", report_file)
STUDENT_ID = "eval_router_student"
CLASSES = ["diagnose", "retrieve"]


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────
# Statistical helpers (no scipy dependency required)
# ─────────────────────────────────────────────────────────
def percentile(data: list[float], p: float) -> float:
    """Compute the p-th percentile of a list of numbers."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)


def confusion_matrix(y_true: list[str], y_pred: list[str], labels: list[str]) -> list[list[int]]:
    """Build a confusion matrix. Rows = true, Cols = predicted."""
    n = len(labels)
    idx = {label: i for i, label in enumerate(labels)}
    matrix = [[0] * n for _ in range(n)]
    for t, p in zip(y_true, y_pred):
        if t in idx and p in idx:
            matrix[idx[t]][idx[p]] += 1
    return matrix


def precision_recall_f1(cm: list[list[int]], labels: list[str]) -> dict:
    """Compute per-class precision, recall, F1 from a confusion matrix."""
    n = len(labels)
    metrics = {}
    for i, label in enumerate(labels):
        tp = cm[i][i]
        fp = sum(cm[j][i] for j in range(n)) - tp
        fn = sum(cm[i][j] for j in range(n)) - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        support = sum(cm[i])
        metrics[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": support,
        }
    return metrics


def macro_f1(per_class: dict) -> float:
    f1s = [v["f1"] for v in per_class.values()]
    return round(sum(f1s) / len(f1s), 4) if f1s else 0.0


def weighted_f1(per_class: dict) -> float:
    total_support = sum(v["support"] for v in per_class.values())
    if total_support == 0:
        return 0.0
    return round(
        sum(v["f1"] * v["support"] for v in per_class.values()) / total_support, 4
    )


def cohens_kappa(cm: list[list[int]]) -> float:
    """Cohen's Kappa — agreement beyond chance."""
    n = sum(sum(row) for row in cm)
    if n == 0:
        return 0.0
    po = sum(cm[i][i] for i in range(len(cm))) / n  # observed agreement
    # Expected agreement
    pe = 0.0
    for i in range(len(cm)):
        row_total = sum(cm[i])
        col_total = sum(cm[j][i] for j in range(len(cm)))
        pe += (row_total * col_total) / (n * n)
    if pe == 1.0:
        return 1.0
    return round((po - pe) / (1.0 - pe), 4)


# ─────────────────────────────────────────────────────────
# Main evaluation
# ─────────────────────────────────────────────────────────
def evaluate():
    dataset = load_dataset()
    print(f"  Loaded {len(dataset)} test cases\n")

    y_true = []
    y_pred = []
    latencies = []
    per_query = []

    for idx, case in enumerate(dataset, 1):
        state = {
            "user_input": case["user_input"],
            "student_id": STUDENT_ID,
            "chat_history": [],
        }

        t0 = time.perf_counter()
        output = router_node(state)
        latency_ms = (time.perf_counter() - t0) * 1000

        predicted = output.get("route", "retrieve")
        expected = case["expected_route"]

        y_true.append(expected)
        y_pred.append(predicted)
        latencies.append(latency_ms)

        is_correct = predicted == expected
        status = "PASS" if is_correct else "FAIL"
        print(f"  [{status}] #{idx:02d}  expected={expected:<9} predicted={predicted:<9}  ({latency_ms:.0f} ms)")

        per_query.append({
            "id": idx,
            "query": case["user_input"][:80],
            "expected": expected,
            "predicted": predicted,
            "correct": is_correct,
            "reason": output.get("route_reason", ""),
            "latency_ms": round(latency_ms, 2),
        })

    # ── Compute all metrics ─────────────────────────────
    cm = confusion_matrix(y_true, y_pred, CLASSES)
    per_class = precision_recall_f1(cm, CLASSES)
    m_f1 = macro_f1(per_class)
    w_f1 = weighted_f1(per_class)
    kappa = cohens_kappa(cm)
    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true) * 100

    metrics = {
        "total_queries": len(y_true),
        "accuracy_pct": round(accuracy, 2),
        "macro_f1": m_f1,
        "weighted_f1": w_f1,
        "cohens_kappa": kappa,
        "confusion_matrix": {
            "labels": CLASSES,
            "matrix": cm,
            "note": "rows=true, cols=predicted"
        },
        "per_class": per_class,
        "latency": {
            "avg_ms": round(sum(latencies) / len(latencies), 2),
            "p50_ms": round(percentile(latencies, 50), 2),
            "p95_ms": round(percentile(latencies, 95), 2),
            "p99_ms": round(percentile(latencies, 99), 2),
            "min_ms": round(min(latencies), 2),
            "max_ms": round(max(latencies), 2),
        },
        "per_query_results": per_query,
    }
    return metrics


def print_report(metrics: dict):
    print("\n" + "=" * 60)
    print("  ROUTER EVALUATION RESULTS")
    print("=" * 60)

    print(f"\n  Accuracy       : {metrics['accuracy_pct']}%")
    print(f"  Macro F1       : {metrics['macro_f1']}")
    print(f"  Weighted F1    : {metrics['weighted_f1']}")
    print(f"  Cohen's Kappa  : {metrics['cohens_kappa']}")

    print(f"\n  {'Class':<12} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>10}")
    print("  " + "-" * 52)
    for cls in CLASSES:
        m = metrics["per_class"][cls]
        print(f"  {cls:<12} {m['precision']:>10.4f} {m['recall']:>10.4f} {m['f1']:>10.4f} {m['support']:>10}")

    cm = metrics["confusion_matrix"]["matrix"]
    labels = metrics["confusion_matrix"]["labels"]
    print(f"\n  Confusion Matrix (rows=true, cols=predicted):")
    print(f"  {'':>12}  " + "  ".join(f"{l:>10}" for l in labels))
    for i, label in enumerate(labels):
        print(f"  {label:>12}  " + "  ".join(f"{cm[i][j]:>10}" for j in range(len(labels))))

    lat = metrics["latency"]
    print(f"\n  Latency: avg={lat['avg_ms']}ms  p50={lat['p50_ms']}ms  p95={lat['p95_ms']}ms  p99={lat['p99_ms']}ms")
    print("=" * 60)


def main():
    print("=" * 60)
    print("  GraphMASAL — Router Agent Evaluation (F1 + Kappa)")
    print("=" * 60)

    metrics = evaluate()
    print_report(metrics)

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n  Full report saved -> {os.path.abspath(REPORT_PATH)}")


if __name__ == "__main__":
    main()
