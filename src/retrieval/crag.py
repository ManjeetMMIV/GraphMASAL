"""
CRAG — Corrective Retrieval-Augmented Generation
==================================================
Implements a lightweight self-correction loop that verifies generated answers
are grounded in the retrieved context before returning them to the student.

Flow:
  1. Tutor generates an answer from retrieved context.
  2. CRAG verifier checks: "Does this answer contain claims not supported by the context?"
  3. If hallucination detected → flag the ungrounded claims.
  4. Tutor regenerates with an explicit instruction to stay grounded.
  5. Max 1 correction cycle to keep latency acceptable (~2-3s overhead).

Reference: Yan et al., "Corrective Retrieval Augmented Generation" (2024).
"""
from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.llm import get_chat_model


def verify_and_correct(
    question: str,
    answer: str,
    context: str,
    *,
    max_retries: int = 1,
) -> dict:
    """
    Verify that `answer` is grounded in `context`. If hallucination is detected,
    regenerate a corrected answer.
    
    Returns:
        {
            "answer": str,          # Final (possibly corrected) answer
            "was_corrected": bool,  # Whether correction was applied
            "verification": str,    # Verifier's assessment
        }
    """
    llm = get_chat_model(temperature=0.0)

    # ── Step 1: Verify grounding ──────────────────────────────────────────
    verify_prompt = f"""You are a factual accuracy auditor. Check if the ANSWER is fully supported by the CONTEXT.

CONTEXT:
{context[:3000]}

QUESTION: {question}

ANSWER:
{answer}

Instructions:
1. Identify any claims in the ANSWER that are NOT supported by the CONTEXT.
2. If ALL claims are supported, respond with exactly: GROUNDED
3. If ANY claims are unsupported, respond with: UNGROUNDED: [list the specific unsupported claims]

Your verdict:"""

    messages = [
        SystemMessage(content="You are a precise factual auditor. Be strict — any claim not explicitly in the context is ungrounded."),
        HumanMessage(content=verify_prompt),
    ]

    try:
        verification = llm.invoke(messages).content.strip()
    except Exception:
        # If verification fails, return original answer
        return {
            "answer": answer,
            "was_corrected": False,
            "verification": "Verification skipped (LLM error)",
        }

    # ── Step 2: If grounded, return as-is ─────────────────────────────────
    if "GROUNDED" in verification.upper() and "UNGROUNDED" not in verification.upper():
        return {
            "answer": answer,
            "was_corrected": False,
            "verification": verification,
        }

    # ── Step 3: Regenerate with correction instruction ────────────────────
    if max_retries < 1:
        return {
            "answer": answer,
            "was_corrected": False,
            "verification": verification,
        }

    correction_prompt = f"""You are an expert tutor. You previously generated an answer that contained ungrounded claims.

CONTEXT (use ONLY this information):
{context[:3000]}

QUESTION: {question}

PREVIOUS ANSWER (contains errors):
{answer}

VERIFIER FEEDBACK:
{verification}

Generate a CORRECTED answer that:
1. Uses facts from the CONTEXT above.
2. Removes or corrects all ungrounded claims.
3. Synthesizes the supported concepts to answer the question clearly and directly.
4. Maintains an authoritative, educational tone.

Corrected answer:"""

    messages = [
        SystemMessage(content="You are a careful, accurate tutor. Never add information not in the context."),
        HumanMessage(content=correction_prompt),
    ]

    try:
        corrected = llm.invoke(messages).content.strip()
    except Exception:
        return {
            "answer": answer,
            "was_corrected": False,
            "verification": verification,
        }

    return {
        "answer": corrected,
        "was_corrected": True,
        "verification": verification,
    }
