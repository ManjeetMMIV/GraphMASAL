"""
HyDE (Hypothetical Document Embeddings) Query Transformer
==========================================================
Transforms vague or ambiguous student queries into richer representations
for improved vector search retrieval.

Strategy:
  1. Generate a hypothetical ideal answer to the student's question using a fast LLM.
  2. Embed the hypothetical answer instead of (or alongside) the raw query.
  3. The hypothetical answer contains domain-specific terminology that better matches
     the indexed concept embeddings, dramatically improving recall.

Reference: Gao et al., "Precise Zero-Shot Dense Retrieval without Relevance Labels" (2022).
"""
from __future__ import annotations

import hashlib
from functools import lru_cache
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.llm import get_chat_model


# ── In-memory semantic cache ───────────────────────────────────────────────
_hyde_cache: dict[str, str] = {}
_MAX_CACHE_SIZE = 256


def _cache_key(query: str) -> str:
    return hashlib.md5(query.strip().lower().encode()).hexdigest()


def generate_hypothetical_answer(
    query: str,
    *,
    domain_hint: str = "computer science and software engineering",
    max_tokens: int = 200,
) -> str:
    """
    Generate a hypothetical ideal answer to the student's question.
    This answer is used as a richer embedding target for vector search (HyDE).
    
    The hypothetical answer contains domain-specific keywords and terminology
    that match indexed concept descriptions, improving cosine similarity with
    relevant chunks.
    """
    key = _cache_key(query)
    if key in _hyde_cache:
        return _hyde_cache[key]

    llm = get_chat_model(temperature=0.0)

    system_prompt = f"""You are a {domain_hint} expert writing a textbook answer.
Given a student's question, write a concise, factually dense paragraph that directly answers it.
Include relevant technical terms, definitions, and key relationships.
Do NOT say "the answer is" or add preamble — start directly with the content.
Keep your answer under 150 words."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query),
    ]

    try:
        response = llm.invoke(messages).content.strip()
    except Exception:
        # If LLM fails, fall back to the original query
        return query

    # Cache the result
    if len(_hyde_cache) >= _MAX_CACHE_SIZE:
        # Evict oldest entry (FIFO approximation)
        oldest_key = next(iter(_hyde_cache))
        del _hyde_cache[oldest_key]
    _hyde_cache[key] = response

    return response


def hyde_augmented_query(query: str, *, weight_original: float = 0.3, weight_hyde: float = 0.7) -> str:
    """
    Combine the original query with the HyDE hypothetical answer for embedding.
    
    This creates a composite text that:
    - Retains the original query's intent (weight_original)
    - Adds domain-rich terminology from the hypothetical answer (weight_hyde)
    
    The result is embedded as a single string for vector search.
    """
    hyde_answer = generate_hypothetical_answer(query)
    # Simply concatenate — the embedding model will capture both signals
    return f"{query}\n\n{hyde_answer}"


def clear_hyde_cache() -> None:
    """Clear the HyDE query transformation cache."""
    _hyde_cache.clear()
