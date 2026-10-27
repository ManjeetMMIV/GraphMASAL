from __future__ import annotations

import re
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.agents.llm import get_chat_model
from src.agents.state import AgentState
from src.agents.tools import update_mastery_tool, hybrid_retrieval_tool, _managed_connection

_CONCEPTS_CACHE: Optional[list[dict]] = None

# Aliases and subtopics mapping to canonical KG concept IDs
_CONCEPT_ALIASES = {
    # REST API Domain
    "put": "http-methods",
    "patch": "http-methods",
    "get": "http-methods",
    "post": "http-methods",
    "delete": "http-methods",
    "http-method": "http-methods",
    "http-methods": "http-methods",
    "idempotency": "http-methods",
    "restful-api-design": "resource-naming",
    "resource-naming": "resource-naming",
    "uri-design": "resource-naming",
    "naming": "resource-naming",
    "endpoint-naming": "resource-naming",
    "status-codes": "status-codes-and-errors",
    "status-codes-and-errors": "status-codes-and-errors",
    "error-handling": "status-codes-and-errors",
    "rfc-9457": "status-codes-and-errors",
    "401": "status-codes-and-errors",
    "403": "status-codes-and-errors",
    "payload-design": "request-response-design",
    "request-response-design": "request-response-design",
    "json-styling": "request-response-design",
    "monetary-values": "request-response-design",
    "money": "request-response-design",
    "pagination": "pagination-and-filtering",
    "pagination-and-filtering": "pagination-and-filtering",
    "cursor-pagination": "pagination-and-filtering",
    "offset-pagination": "pagination-and-filtering",
    "idempotency-keys": "idempotency-and-retries",
    "idempotency-and-retries": "idempotency-and-retries",
    "retries": "idempotency-and-retries",
    "caching": "caching-and-etags",
    "caching-and-etags": "caching-and-etags",
    "etags": "caching-and-etags",
    "optimistic-locking": "caching-and-etags",
    "long-running-jobs": "long-running-jobs",
    "webhooks": "long-running-jobs",
    "async-operations": "long-running-jobs",
    "api-security": "api-security",
    "jwt": "api-security",
    "auth": "api-security",
    "cors": "api-security",
    "bola": "api-security",
    "streaming": "ai-and-streaming-apis",
    "ai-and-streaming-apis": "ai-and-streaming-apis",
    "sse": "ai-and-streaming-apis",
    "api-architectures": "api-architectures",
    "graphql": "api-architectures",
    "grpc": "api-architectures",
    # OS Domain
    "architecture": "computer-architecture",
    "computer-architecture": "computer-architecture",
    "hardware": "computer-architecture",
    "cpu": "cpu-virtualization",
    "cpu-virtualization": "cpu-virtualization",
    "process": "processes",
    "processes": "processes",
    "fork": "processes",
    "thread": "threads",
    "threads": "threads",
    "concurrency": "concurrency",
    "concurrency-and-threads": "concurrency",
    "scheduler": "scheduling",
    "scheduling": "scheduling",
    "round-robin": "scheduling",
    "mlfq": "scheduling",
    "virtual-memory": "memory-virtualization",
    "memory-virtualization": "memory-virtualization",
    "memory": "memory-virtualization",
    "page": "paging",
    "pages": "paging",
    "paging": "paging",
    "tlb": "paging",
    "lock": "locks",
    "locks": "locks",
    "mutex": "locks",
    "spinlock": "locks",
    "persistence": "persistence",
    "persistent": "persistence",
    "file": "file-systems",
    "files": "file-systems",
    "file-system": "file-systems",
    "file-systems": "file-systems",
    "inode": "file-systems",
    "inodes": "file-systems",
    "data-integrity": "data-integrity",
    "integrity": "data-integrity",
    "checksum": "data-integrity",
    "checksums": "data-integrity",
    "raid": "data-integrity",
}


def _get_concepts_list() -> list[dict]:
    try:
        from src.agents.tools import _managed_connection
        with _managed_connection() as conn:
            records = conn.query("MATCH (c:Concept) RETURN c.id AS id, c.name AS name, c.description AS desc ORDER BY c.id")
            if records:
                return [{"id": r["id"], "name": r["name"], "desc": r.get("desc", "") or ""} for r in records]
    except Exception:
        pass

    # Fallback to union of both curricula
    return [
        {"id": "http-methods", "name": "HTTP Methods and Idempotency", "desc": "Semantics of GET, POST, PUT, PATCH, DELETE"},
        {"id": "resource-naming", "name": "Resource Naming and URI Design", "desc": "Plural nouns, kebab-case, no verbs"},
        {"id": "status-codes-and-errors", "name": "HTTP Status Codes and Error Handling", "desc": "200, 201, 204, 400, 401, 403, 404, 422, 500, RFC 9457"},
        {"id": "request-response-design", "name": "Request and Response Payload Design", "desc": "JSON styling, ISO 8601, money in minor units (cents)"},
        {"id": "pagination-and-filtering", "name": "Pagination, Filtering, and Sorting", "desc": "Offset vs cursor pagination trade-offs"},
        {"id": "idempotency-and-retries", "name": "Idempotency Keys and Safe Retries", "desc": "Idempotency-Key headers for safe POST retries"},
        {"id": "caching-and-etags", "name": "HTTP Caching and Optimistic Locking", "desc": "ETags, If-None-Match (304), If-Match (412)"},
        {"id": "long-running-jobs", "name": "Asynchronous Operations and Webhooks", "desc": "202 Accepted, polling /jobs/{id}, signed webhooks"},
        {"id": "api-security", "name": "API Authentication, Authorization, and Security", "desc": "Auth, OWASP, preventing BOLA, JWT pitfalls, CORS"},
        {"id": "ai-and-streaming-apis", "name": "AI APIs and Event Streaming", "desc": "Server-Sent Events (SSE) text/event-stream"},
        {"id": "api-architectures", "name": "API Architecture Comparison and Testing", "desc": "REST vs GraphQL vs gRPC"},
        {"id": "computer-architecture", "name": "Computer Architecture", "desc": "CPU, RAM, I/O, storage hierarchy"},
        {"id": "cpu-virtualization", "name": "CPU Virtualization", "desc": "Time-sharing the physical CPU among processes"},
        {"id": "processes", "name": "Processes", "desc": "Process abstraction, address spaces, fork"},
        {"id": "scheduling", "name": "Process Scheduling", "desc": "FIFO, SJF, RR, MLFQ scheduling algorithms"},
        {"id": "memory-virtualization", "name": "Memory Virtualization", "desc": "Virtual address space, address translation"},
        {"id": "paging", "name": "Paging", "desc": "Fixed-size pages, page tables, TLB"},
        {"id": "concurrency", "name": "Concurrency", "desc": "Concurrent execution, synchronization challenges"},
        {"id": "threads", "name": "Threads", "desc": "Execution units within a process, shared heap, private stack"},
        {"id": "locks", "name": "Locks", "desc": "Mutual exclusion, spinlocks, mutexes, preventing race conditions"},
        {"id": "persistence", "name": "Persistence", "desc": "Non-volatile storage devices, saving data across restarts"},
        {"id": "file-systems", "name": "File Systems", "desc": "Inodes, directories, file organization, block pointers"},
        {"id": "data-integrity", "name": "Data Integrity and Protection", "desc": "Checksums, RAID redundancy, crash recovery"},
    ]
    return _CONCEPTS_CACHE


def _normalize_concept_id(raw_id: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\-]", "", raw_id.strip().lower().replace(" ", "-"))
    if cleaned in _CONCEPT_ALIASES:
        return _CONCEPT_ALIASES[cleaned]
    for alias, canonical in _CONCEPT_ALIASES.items():
        if alias in cleaned or cleaned in alias:
            return canonical
    return cleaned


def diagnoser_node(state: AgentState):
    """
    The Diagnoser Agent.
    Analyzes the user's input to determine if they are struggling with a concept
    or asserting a fundamental misconception.
    """
    print("\n--- [Diagnoser Agent] Executing ---")

    llm = get_chat_model(temperature=0)
    llm_with_tools = llm.bind_tools([update_mastery_tool])

    concepts = _get_concepts_list()
    concept_list_text = "\n".join(f"  - `{c['id']}`: {c['name']} ({c.get('desc', '')})" for c in concepts)

    system_prompt = f"""You are the Diagnostic Engine of an AI Tutor.
The student's ID is: {state['student_id']}.

Your sole job is to detect whether the student is expressing a fundamental misconception or severe misunderstanding about a computer science concept.

## Known Knowledge Graph Concepts (USE THESE EXACT IDs):
{concept_list_text}

## Classification Rules:
1. **Misconception (Invoke `update_mastery_tool`)**:
   - The student states a factual falsehood, anti-pattern, or false assumption as if it were true.
   - Examples of misconceptions:
     * "I want to update just one field so I should use PUT" -> `http-methods`
     * "To get active orders I should create GET /getOrders" -> `resource-naming`
     * "If validation fails I return 200 OK with error in body" -> `status-codes-and-errors`
     * "Store price as float in JSON body" -> `request-response-design`
     * "CPU executes programs directly from hard drive" -> `computer-architecture`
     * "Child process shares same memory space as parent after fork" -> `processes`
     * "Round robin guarantees shortest jobs finish first" -> `scheduling`
     * "Paging suffers from external fragmentation" -> `paging`
     * "On multi-core, no need to worry about race conditions" -> `concurrency-and-threads`

2. **NOT a Misconception (DO NOT invoke any tool)**:
   - The student asks a question ("How should I...", "What is the difference between...", "Why does...").
   - The student expresses uncertainty or asks for advice without asserting an error ("Should I use cursor pagination?").
   - The student states a factually correct statement ("PUT replaces the entire resource", "GET is idempotent", "Virtual memory translates virtual addresses").

## Action:
- If and ONLY IF a misconception is asserted, invoke `update_mastery_tool(student_id='{state['student_id']}', concept_id='<EXACT_ID_FROM_LIST>', mastery_score=0.0)`.
- If NO misconception is present, output a brief explanation without calling any tools."""

    messages = [SystemMessage(content=system_prompt)]
    for turn in state.get("chat_history", []):
        if turn.get("role") == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn.get("role") == "assistant":
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=state["user_input"]))

    response = llm_with_tools.invoke(messages)

    misconception_detected = False
    affected_concepts = []

    if response.tool_calls:
        print(f"Diagnoser invoked {len(response.tool_calls)} tools.")
        for tool_call in response.tool_calls:
            args = tool_call.get("args", {})
            raw_concept = args.get("concept_id") or args.get("concept") or args.get("query") or ""
            concept_id = _normalize_concept_id(raw_concept)

            if concept_id:
                misconception_detected = True
                if concept_id not in affected_concepts:
                    affected_concepts.append(concept_id)
                print(f"Diagnoser identified misconception on: {concept_id}")
                update_mastery_tool.invoke({
                    "student_id": state["student_id"],
                    "concept_id": concept_id,
                    "mastery_score": 0.0,
                })
    else:
        print("Diagnoser: No misconceptions detected.")

    return {
        "misconception_detected": misconception_detected,
        "affected_concepts": affected_concepts,
    }

