"""
RAGAS Evaluation for GraphMASAL
================================
Evaluates the quality of the RAG pipeline using RAGAS metrics:
- Faithfulness: Is the answer factually grounded in the retrieved context?
- Answer Relevancy: How relevant is the answer to the question?
- Context Precision: Are relevant documents ranked higher?
- Context Recall: Does the context cover the ground truth?
- Answer Correctness: How accurate is the answer vs ground truth?

Usage:
    uv run python tests/test_ragas_eval.py              # Full run (generates answers via LLM)
    uv run python tests/test_ragas_eval.py --no-gen      # Skip LLM generation, only compute metrics
    uv run python tests/test_ragas_eval.py --max 5       # Only process first 5 questions
"""

import os
import sys
import json
import time
import argparse
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph.db import Neo4jConnection
from src.retrieval.hybrid import HybridRetriever
from src.agents.llm import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage


DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", "ragas_eval_dataset.json")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ragas_eval_report.json")


def load_dataset(max_questions: int | None = None) -> list[dict]:
    with open(DATASET_PATH, "r") as f:
        data = json.load(f)
    if max_questions:
        data = data[:max_questions]
    return data


def retrieve_contexts(query: str, retriever: HybridRetriever, student_id: str) -> list[str]:
    results = retriever.retrieve(query, student_id, top_k=3)
    if not results:
        return ["No relevant concepts found."]
    return [
        f"{r['concept']}: {r['description']}" for r in results
    ]


def generate_answer(question: str, contexts: list[str], llm) -> str:
    context_text = "\n\n".join(contexts)
    prompt = f"""You are an expert computer science tutor. Answer the student's question based ONLY on the provided knowledge context.

Knowledge context:
{context_text}

Student question: {question}

Provide a clear, concise answer using only information from the context above. If the context does not contain enough information, say so."""
    messages = [
        SystemMessage(content="You are a helpful, accurate tutor."),
        HumanMessage(content=prompt),
    ]
    response = llm.invoke(messages)
    return response.content


def compute_ragas(results: list[dict]) -> dict:
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    if os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

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

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    dataset = Dataset.from_dict({
        "question": [r["question"] for r in results],
        "answer": [r["answer"] for r in results],
        "contexts": [r["contexts"] for r in results],
        "ground_truth": [r["ground_truth"] for r in results],
    })

    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            answer_correctness,
        ],
        llm=llm,
        embeddings=embeddings,
    )

    df = result.to_pandas()
    metric_names = ["faithfulness", "answer_relevancy", "context_precision", "context_recall", "answer_correctness"]
    scores = {}
    for metric in metric_names:
        if metric in df.columns:
            values = df[metric].dropna()
            if not values.empty:
                scores[metric] = round(float(values.mean()), 4)
    return scores


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-gen", action="store_true", help="Skip LLM answer generation")
    parser.add_argument("--max", type=int, default=None, help="Max number of questions to process")
    args = parser.parse_args()

    dataset = load_dataset(args.max)
    print(f"Loaded {len(dataset)} evaluation questions")

    conn = Neo4jConnection(
        os.getenv("NEO4J_URI", ""),
        os.getenv("NEO4J_USERNAME", ""),
        os.getenv("NEO4J_PASSWORD", ""),
    )
    retriever = HybridRetriever(conn)
    llm = get_chat_model(temperature=0) if not args.no_gen else None

    results = []
    for i, item in enumerate(dataset, 1):
        print(f"\n[{i}/{len(dataset)}] {item['question'][:60]}...")

        t0 = time.perf_counter()
        contexts = retrieve_contexts(item["question"], retriever, "student_123")
        retrieval_ms = (time.perf_counter() - t0) * 1000

        if llm:
            t0 = time.perf_counter()
            answer = generate_answer(item["question"], contexts, llm)
            gen_ms = (time.perf_counter() - t0) * 1000
        else:
            answer = ""
            gen_ms = 0

        results.append({
            "question": item["question"],
            "ground_truth": item["ground_truth"],
            "answer": answer,
            "contexts": contexts,
            "retrieval_time_ms": round(retrieval_ms, 2),
            "generation_time_ms": round(gen_ms, 2),
        })

        print(f"   Contexts: {len(contexts)} chunks, Retrieval: {retrieval_ms:.0f}ms")
        if answer:
            print(f"   Answer: {answer[:80]}... Gen: {gen_ms:.0f}ms")

    conn.close()

    if not results:
        print("\nNo results to evaluate")
        return

    if all(r["answer"] for r in results):
        print("\n" + "=" * 60)
        print("  Computing RAGAS metrics...")
        print("=" * 60)
        scores = compute_ragas(results)

        print("\n" + "-" * 60)
        print("  RAGAS EVALUATION RESULTS")
        print("-" * 60)
        for metric, value in scores.items():
            if isinstance(value, float):
                print(f"  {metric:25s}: {value:.4f}")
            else:
                print(f"  {metric:25s}: {value}")
        print("-" * 60)

        report = {
            "metrics": {k: v for k, v in scores.items()},
            "per_question": results,
        }
    else:
        print("\nSkipping RAGAS computation (no answers generated).")
        print("Use without --no-gen to generate answers first.")
        report = {"per_question": results}

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nReport saved -> {os.path.abspath(REPORT_PATH)}")


if __name__ == "__main__":
    main()
