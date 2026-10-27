"""
Contextual Compressor
======================
Strips irrelevant sentences from retrieved context chunks before feeding
them to the tutor LLM.

Problem: Retrieved chunks contain noise — sentences about unrelated subtopics
that reduce Context Precision and inject irrelevant information.

Solution: Use a fast LLM to extract ONLY the sentences from each chunk that
are directly relevant to the student's query. This dramatically improves:
  - Context Precision (removes noise from top-k)
  - Faithfulness (less irrelevant context = less hallucination)
  - Answer Correctness (focused context = more precise answers)
"""
from __future__ import annotations

import hashlib
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.llm import get_chat_model


# ── Cache to avoid re-compressing identical (query, chunk) pairs ──────────
_compression_cache: dict[str, str] = {}
_MAX_CACHE = 512


def _cache_key(query: str, chunk: str) -> str:
    combined = f"{query.strip().lower()}|||{chunk.strip()[:200]}"
    return hashlib.md5(combined.encode()).hexdigest()


def compress_context(query: str, chunk_text: str, *, min_chunk_len: int = 250) -> str:
    """
    Extract only the sentences from `chunk_text` that are directly relevant
    to answering the student's `query`.
    
    Short chunks (< min_chunk_len chars) are returned as-is since they're
    already focused.
    
    Returns the compressed text, or the original if compression fails.
    """
    if len(chunk_text.strip()) < min_chunk_len:
        return chunk_text.strip()

    key = _cache_key(query, chunk_text)
    if key in _compression_cache:
        return _compression_cache[key]

    llm = get_chat_model(temperature=0.0)

    prompt = f"""Extract ONLY the sentences from the following text that are directly relevant to answering the question. Remove all irrelevant sentences. If nothing is relevant, return "NOT_RELEVANT".

Question: {query}

Text:
{chunk_text}

Relevant extract:"""

    messages = [
        SystemMessage(content="You are a precise context extractor. Return only the relevant sentences, preserving their original wording. No preamble, no explanation."),
        HumanMessage(content=prompt),
    ]

    try:
        response = llm.invoke(messages).content.strip()
        # If the model says nothing is relevant, return empty
        if "NOT_RELEVANT" in response.upper():
            result = ""
        elif len(response) < 40:
            result = chunk_text  # Safeguard: overly short snippet loses vital context
        else:
            result = response
    except Exception:
        result = chunk_text  # Fall back to original on error

    # Cache result
    if len(_compression_cache) >= _MAX_CACHE:
        oldest = next(iter(_compression_cache))
        del _compression_cache[oldest]
    _compression_cache[key] = result

    return result


def compress_contexts(query: str, chunks: list[str], *, min_chunk_len: int = 50) -> list[str]:
    """
    Compress a list of context chunks, removing irrelevant sentences.
    Empty results (fully irrelevant chunks) are filtered out.
    """
    compressed = []
    for chunk in chunks:
        result = compress_context(query, chunk, min_chunk_len=min_chunk_len)
        if result.strip():
            compressed.append(result)
    return compressed if compressed else chunks  # Never return empty — fall back to originals


def clear_compression_cache() -> None:
    """Clear the context compression cache."""
    _compression_cache.clear()
