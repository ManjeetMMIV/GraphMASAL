"""
Evaluation 4: Diagnoser Agent — Misconception Detection Metrics
================================================================
Evaluates the Diagnoser Agent's ability to:
  1. Detect misconceptions (Precision, Recall, F1)
  2. Correctly identify the affected concept (Concept Attribution Accuracy)
  3. Avoid false positives on tricky edge cases

Uses a ground-truth dataset of 30 cases (15 misconceptions + 15 true negatives).

Usage:
    uv run python tests/eval_diagnoser.py
"""
import os
import sys
import json
import time
import logging
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
logging.getLogger("neo4j").setLevel(logging.ERROR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.diagnoser_agent import diagnoser_node

# ─────────────────────────────────────────────────────────
# Dataset & Arguments
# ─────────────────────────────────────────────────────────
import argparse

parser = argparse.ArgumentParser(description="Evaluate Diagnoser Agent")
parser.add_argument("--api", action="store_true", help="Use REST API Design dataset instead of OS dataset")
args, _ = parser.parse_known_args()

dataset_file = "diagnoser_eval_dataset_api.json" if args.api else "diagnoser_eval_dataset.json"
report_file = "eval_diagnoser_api_report.json" if args.api else "eval_diagnoser_report.json"

DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", dataset_file)
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", report_file)
STUDENT_ID = "eval_diagnoser_student"


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate():
    dataset = load_dataset()
    print(f"  Loaded {len(dataset)} test cases "
          f"({sum(1 for d in dataset if d['has_misconception'])} misconceptions, "
          f"{sum(1 for d in dataset if not d['has_misconception'])} true negatives)\n")

    # Counters for classification metrics
    tp = 0  # Correctly detected misconception
    fp = 0  # Flagged misconception when there was none
    tn = 0  # Correctly identified no misconception
    fn = 0  # Missed a real misconception

    # Concept attribution
    correct_concepts = 0
    total_detections = 0

    per_case = []

    for idx, case in enumerate(dataset, 1):
        expected_has = case["has_misconception"]
        expected_concept = case.get("affected_concept")

        state = {
            "student_id": STUDENT_ID,
            "user_input": case["user_input"],
            "chat_history": [],
            "long_term_memory": "",
            "learning_pace": "normal",
        }

        t0 = time.perf_counter()
        try:
            result = diagnoser_node(state)
            latency_ms = (time.perf_counter() - t0) * 1000
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000
            print(f"  [ERROR] #{idx:02d} — {e}")
            result = {"misconception_detected": False, "affected_concepts": []}

        predicted_has = result.get("misconception_detected", False)
        predicted_concepts = result.get("affected_concepts", [])

        # Classification
        if expected_has and predicted_has:
            tp += 1
            classification = "TP"
        elif not expected_has and not predicted_has:
            tn += 1
            classification = "TN"
        elif not expected_has and predicted_has:
            fp += 1
            classification = "FP"
        else:  # expected_has and not predicted_has
            fn += 1
            classification = "FN"

        # Concept attribution (only when both expected and predicted a misconception)
        concept_correct = False
        if expected_has and predicted_has and expected_concept:
            total_detections += 1
            from src.agents.diagnoser_agent import _normalize_concept_id
            norm_expected = _normalize_concept_id(expected_concept)
            norm_predicted = [_normalize_concept_id(p) for p in predicted_concepts]
            if norm_expected in norm_predicted or any(norm_expected in p or p in norm_expected for p in norm_predicted):
                correct_concepts += 1
                concept_correct = True

        status_icon = {
            "TP": "OK TP", "TN": "OK TN",
            "FP": "FAIL FP", "FN": "FAIL FN",
        }[classification]

        print(
            f"  [{status_icon:<7}] #{idx:02d}  "
            f"expected={'YES' if expected_has else 'NO ':3s}  "
            f"predicted={'YES' if predicted_has else 'NO ':3s}  "
            f"({latency_ms:.0f} ms)"
            + (f"  concept: {expected_concept} -> {predicted_concepts}" if expected_has else "")
        )

        per_case.append({
            "id": idx,
            "input": case["user_input"][:80],
            "expected_misconception": expected_has,
            "expected_concept": expected_concept,
            "predicted_misconception": predicted_has,
            "predicted_concepts": predicted_concepts,
            "classification": classification,
            "concept_correct": concept_correct if expected_has and predicted_has else None,
            "latency_ms": round(latency_ms, 2),
        })

    # ── Compute metrics ──────────────────────────────────
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(dataset) * 100
    concept_accuracy = correct_concepts / total_detections if total_detections > 0 else 0.0

    metrics = {
        "total_cases": len(dataset),
        "accuracy_pct": round(accuracy, 2),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "concept_attribution_accuracy": round(concept_accuracy, 4),
        "confusion": {
            "TP": tp, "FP": fp,
            "TN": tn, "FN": fn,
        },
        "per_case_results": per_case,
    }
    return metrics


def print_report(metrics: dict):
    print("\n" + "=" * 60)
    print("  DIAGNOSER EVALUATION RESULTS")
    print("=" * 60)

    print(f"\n  Accuracy                   : {metrics['accuracy_pct']}%")
    print(f"  Precision                  : {metrics['precision']:.4f}")
    print(f"  Recall                     : {metrics['recall']:.4f}")
    print(f"  F1 Score                   : {metrics['f1_score']:.4f}")
    print(f"  Concept Attribution Acc.   : {metrics['concept_attribution_accuracy']:.4f}")

    c = metrics["confusion"]
    print(f"\n  Confusion Matrix:")
    print(f"  {'':>20}  {'Predicted YES':>14}  {'Predicted NO':>13}")
    print(f"  {'Actual YES':>20}  {c['TP']:>14}  {c['FN']:>13}")
    print(f"  {'Actual NO':>20}  {c['FP']:>14}  {c['TN']:>13}")

    print("=" * 60)


def main():
    print("=" * 60)
    print("  GraphMASAL — Diagnoser Agent Evaluation")
    print("=" * 60)

    metrics = evaluate()
    print_report(metrics)

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n  Full report saved -> {os.path.abspath(REPORT_PATH)}")


if __name__ == "__main__":
    main()
