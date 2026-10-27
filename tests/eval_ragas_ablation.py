"""
Evaluation 2: RAGAS + Retrieval Ablation (Hybrid vs Vector-Only)
================================================================
Runs the same question set through TWO retrieval configurations:
  1. **Hybrid** — HybridRetriever (vector + graph neighborhood + reranker)
  2. **Vector-Only** — SemanticSearch (raw vector similarity, no graph)

Then computes RAGAS metrics for both and reports the delta, proving
the Knowledge Graph augmentation adds measurable value.

Usage:
    uv run python tests/eval_ragas_ablation.py               # Full run
    uv run python tests/eval_ragas_ablation.py --no-ragas     # Skip RAGAS (just retrieval + generation)
    uv run python tests/eval_ragas_ablation.py --max 5        # Limit to N questions
"""
import os
import sys
import json
import time
import argparse
import logging
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
logging.getLogger("neo4j").setLevel(logging.ERROR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph.db import Neo4jConnection
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.search import SemanticSearch
from src.agents.llm import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

# ─────────────────────────────────────────────────────────
# Dataset & Settings
# ─────────────────────────────────────────────────────────
STUDENT_ID = "eval_ragas_student"


def get_paths(is_api: bool):
    dataset_file = "ragas_eval_dataset_api.json" if is_api else "ragas_eval_dataset.json"
    report_file = "eval_ragas_api_report.json" if is_api else "eval_ragas_ablation_report.json"
    d_path = os.path.join(os.path.dirname(__file__), "data", dataset_file)
    r_path = os.path.join(os.path.dirname(__file__), "..", "data", report_file)
    return d_path, r_path


def load_dataset(dataset_path: str, max_q=None):
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[:max_q] if max_q else data


def retrieve_hybrid(query: str, retriever: HybridRetriever) -> list[str]:
    results = retriever.retrieve(query, STUDENT_ID, top_k=3)
    if not results:
        return ["No relevant concepts found."]
    contexts = []
    for r in results:
        ctx = f"{r['concept']}: {r.get('description', '')}"
        neighborhood = r.get("graph_neighborhood", {})
        prereqs = neighborhood.get("prerequisites", [])
        if prereqs:
            ctx += f" (Prerequisites: {', '.join(prereqs)})"
        contexts.append(ctx)

    # Apply contextual compression to remove noise if chunks are long
    try:
        from src.retrieval.compressor import compress_contexts
        contexts = compress_contexts(query, contexts)
    except Exception:
        pass

    return contexts


def retrieve_vector_only(query: str, searcher: SemanticSearch) -> list[str]:
    """Pure vector similarity — no graph neighborhood, no reranker, no mastery, no HyDE."""
    query_embedding = searcher.model.encode(query).tolist()
    cypher = """
    CALL db.index.vector.queryNodes('concept_embedding', $top_k, $embedding)
    YIELD node AS concept, score AS similarity
    RETURN concept.name AS name, concept.description AS description, similarity
    """
    results = searcher.conn.query(cypher, {"embedding": query_embedding, "top_k": 3})
    if not results:
        return ["No relevant concepts found."]
    return [f"{r['name']}: {r['description']}" for r in results]


def generate_answer(question: str, contexts: list[str], llm, *, use_crag: bool = False) -> str:
    context_text = "\n\n".join(contexts)
    prompt = f"""You are an expert computer science tutor. Answer the student's question accurately, thoroughly, and directly based on the provided knowledge context.

Knowledge context:
{context_text}

Student question: {question}

Provide an authoritative, clear, and comprehensive answer:"""
    messages = [
        SystemMessage(content="You are a helpful, expert tutor. Answer directly and comprehensively using the provided context."),
        HumanMessage(content=prompt),
    ]
    answer = llm.invoke(messages).content

    # Apply CRAG self-correction for the hybrid pipeline
    if use_crag:
        try:
            from src.retrieval.crag import verify_and_correct
            crag_result = verify_and_correct(
                question=question,
                answer=answer,
                context=context_text,
                max_retries=1,
            )
            if crag_result["was_corrected"]:
                answer = crag_result["answer"]
        except Exception:
            pass  # Fall back to uncorrected answer

    return answer


def compute_ragas_scores(results: list[dict]) -> dict:
    """Compute RAGAS metrics. Requires ragas + datasets packages."""
    from langchain_openai import ChatOpenAI
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        answer_correctness,
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    dataset = Dataset.from_dict({
        "question": [r["question"] for r in results],
        "answer": [r["answer"] for r in results],
        "contexts": [r["contexts"] for r in results],
        "ground_truth": [r["ground_truth"] for r in results],
    })

    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall, answer_correctness],
        llm=llm,
        embeddings=embeddings,
    )

    df = result.to_pandas()
    scores = {}
    for metric in ["faithfulness", "answer_relevancy", "context_precision", "context_recall", "answer_correctness"]:
        if metric in df.columns:
            values = df[metric].dropna()
            if not values.empty:
                scores[metric] = round(float(values.mean()), 4)
    return scores


def run_retrieval_pipeline(dataset, retriever_fn, llm, label: str, *, use_crag: bool = False) -> list[dict]:
    """Run retrieval + generation for a single configuration."""
    results = []
    for i, item in enumerate(dataset, 1):
        print(f"  [{label}] [{i}/{len(dataset)}] {item['question'][:55]}...")

        t0 = time.perf_counter()
        contexts = retriever_fn(item["question"])
        retrieval_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        answer = generate_answer(item["question"], contexts, llm, use_crag=use_crag)
        gen_ms = (time.perf_counter() - t0) * 1000

        results.append({
            "question": item["question"],
            "ground_truth": item["ground_truth"],
            "answer": answer,
            "contexts": contexts,
            "retrieval_time_ms": round(retrieval_ms, 2),
            "generation_time_ms": round(gen_ms, 2),
        })
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", action="store_true", help="Use REST API Design dataset instead of OS dataset")
    parser.add_argument("--no-ragas", action="store_true", help="Skip RAGAS metric computation")
    parser.add_argument("--max", type=int, default=None, help="Max questions to process")
    args = parser.parse_args()

    dataset_path, report_path = get_paths(args.api)
    dataset = load_dataset(dataset_path, args.max)
    domain_label = "REST API Design" if args.api else "Operating Systems"
    print("=" * 65)
    print(f"  GraphMASAL — RAGAS Ablation ({domain_label})")
    print("=" * 65)
    print(f"  Questions: {len(dataset)}\n")

    # ── Connect to Neo4j ─────────────────────────────────
    conn = Neo4jConnection(
        os.getenv("NEO4J_URI", ""),
        os.getenv("NEO4J_USERNAME", ""),
        os.getenv("NEO4J_PASSWORD", ""),
    )
    hybrid_retriever = HybridRetriever(conn)
    vector_searcher = SemanticSearch(conn)
    llm = get_chat_model(temperature=0)

    # ── Run HYBRID pipeline ──────────────────────────────
    print("\n--- Configuration A: HYBRID (Vector + Graph + Reranker + HyDE + CRAG) ---")
    hybrid_results = run_retrieval_pipeline(
        dataset,
        lambda q: retrieve_hybrid(q, hybrid_retriever),
        llm,
        "HYBRID",
        use_crag=True,
    )

    # ── Run VECTOR-ONLY pipeline ─────────────────────────
    print("\n--- Configuration B: VECTOR-ONLY (No Graph, No Reranker, No HyDE, No CRAG) ---")
    vector_results = run_retrieval_pipeline(
        dataset,
        lambda q: retrieve_vector_only(q, vector_searcher),
        llm,
        "VECTOR",
        use_crag=False,
    )

    conn.close()

    # ── Compute RAGAS ────────────────────────────────────
    report = {
        "hybrid_results": hybrid_results,
        "vector_only_results": vector_results,
    }

    if not args.no_ragas:
        print("\n" + "=" * 65)
        print("  Computing RAGAS metrics for BOTH configurations...")
        print("=" * 65)

        try:
            hybrid_scores = compute_ragas_scores(hybrid_results)
            vector_scores = compute_ragas_scores(vector_results)

            # Compute delta
            delta = {}
            for key in hybrid_scores:
                if key in vector_scores:
                    delta[key] = round(hybrid_scores[key] - vector_scores[key], 4)

            report["hybrid_ragas"] = hybrid_scores
            report["vector_only_ragas"] = vector_scores
            report["delta_hybrid_minus_vector"] = delta

            # ── Print results ────────────────────────────
            print("\n" + "-" * 65)
            print(f"  {'Metric':<25} {'Hybrid':>10} {'Vector-Only':>12} {'Delta':>10}")
            print("  " + "-" * 57)
            for metric in ["faithfulness", "answer_relevancy", "context_precision", "context_recall", "answer_correctness"]:
                h = hybrid_scores.get(metric, "N/A")
                v = vector_scores.get(metric, "N/A")
                d = delta.get(metric, "N/A")
                h_str = f"{h:.4f}" if isinstance(h, float) else str(h)
                v_str = f"{v:.4f}" if isinstance(v, float) else str(v)
                d_str = f"{d:+.4f}" if isinstance(d, float) else str(d)
                print(f"  {metric:<25} {h_str:>10} {v_str:>12} {d_str:>10}")
            print("-" * 65)
        except Exception as e:
            print(f"\n  RAGAS computation failed: {e}")
            print("  (Install ragas, datasets, langchain-openai if missing)")
            report["ragas_error"] = str(e)
    else:
        print("\n  Skipping RAGAS computation (--no-ragas flag).")

    # ── Retrieval latency comparison ─────────────────────
    avg_hybrid_ret = sum(r["retrieval_time_ms"] for r in hybrid_results) / len(hybrid_results)
    avg_vector_ret = sum(r["retrieval_time_ms"] for r in vector_results) / len(vector_results)
    report["latency_comparison"] = {
        "avg_retrieval_ms_hybrid": round(avg_hybrid_ret, 2),
        "avg_retrieval_ms_vector_only": round(avg_vector_ret, 2),
        "overhead_ms": round(avg_hybrid_ret - avg_vector_ret, 2),
    }
    print(f"\n  Retrieval Latency: Hybrid={avg_hybrid_ret:.0f}ms  Vector-Only={avg_vector_ret:.0f}ms  Overhead={avg_hybrid_ret - avg_vector_ret:+.0f}ms")

    # ── Save report ──────────────────────────────────────
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  Full report saved -> {os.path.abspath(report_path)}")
    print("=" * 65)


if __name__ == "__main__":
    main()
