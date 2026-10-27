"""
Script: seed_api_knowledge.py
==============================
Seeds Neo4j with the complete REST API Design curriculum:
  1. Sets up vector indexes (concept_embedding, pdf_chunk_embedding).
  2. Cleans out prior curriculum data.
  3. Inserts 11 canonical REST API Design concepts with 384-d MiniLM embeddings.
  4. Inserts all directed IS_PREREQUISITE_FOR relationships.
  5. Ingests all 4 pages of api-design-cheat-sheet.pdf into PDFDocument and PDFChunk nodes with vector embeddings.
  6. Links PDFChunks to their most relevant Concept nodes via COVERS_CONCEPT.

Usage:
    uv run python scripts/seed_api_knowledge.py
"""
import os
import sys
import hashlib
import warnings
import logging
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
logging.getLogger("neo4j").setLevel(logging.ERROR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from src.graph.db import Neo4jConnection
from src.ingestion.pdf_pipeline import _chunk_page_text

PDF_PATH = os.path.abspath("D:/ML Projects/imggencheck/api-design-cheat-sheet.pdf")
MODEL_NAME = "all-MiniLM-L6-v2"

API_CONCEPTS = [
    {
        "id": "http-methods",
        "name": "HTTP Methods and Idempotency",
        "description": "Semantics of GET, POST, PUT, PATCH, and DELETE; safe vs idempotent methods; full resource replacement vs partial update.",
        "prerequisites": [],
        "domain": "REST API Design",
    },
    {
        "id": "resource-naming",
        "name": "Resource Naming and URI Design",
        "description": "Naming REST resources using plural lowercase nouns, kebab-case, sub-resources, and avoiding verbs in URIs.",
        "prerequisites": ["http-methods"],
        "domain": "REST API Design",
    },
    {
        "id": "status-codes-and-errors",
        "name": "HTTP Status Codes and Error Handling",
        "description": "Standard status codes (200, 201, 204, 400, 401, 403, 404, 409, 422, 500), RFC 9457 Problem Details, and distinguishing 401 vs 403.",
        "prerequisites": ["http-methods"],
        "domain": "REST API Design",
    },
    {
        "id": "request-response-design",
        "name": "Request and Response Payload Design",
        "description": "Consistent JSON styling, ISO 8601 timestamps, money representation in minor units (cents/paise), string IDs, and Pydantic validation.",
        "prerequisites": ["http-methods", "resource-naming"],
        "domain": "REST API Design",
    },
    {
        "id": "pagination-and-filtering",
        "name": "Pagination, Filtering, and Sorting",
        "description": "Offset vs cursor pagination trade-offs, query filtering (?status=paid), sorting (?sort=-created_at), and sparse fieldsets.",
        "prerequisites": ["resource-naming", "request-response-design"],
        "domain": "REST API Design",
    },
    {
        "id": "idempotency-and-retries",
        "name": "Idempotency Keys and Safe Retries",
        "description": "Using Idempotency-Key headers for safe POST retries, preventing duplicate charges, and client exponential backoff with jitter.",
        "prerequisites": ["http-methods", "status-codes-and-errors"],
        "domain": "REST API Design",
    },
    {
        "id": "caching-and-etags",
        "name": "HTTP Caching and Optimistic Locking",
        "description": "Conditional HTTP requests using ETags, If-None-Match for 304 cache validation, and If-Match for 412 concurrent edit protection.",
        "prerequisites": ["http-methods", "status-codes-and-errors"],
        "domain": "REST API Design",
    },
    {
        "id": "long-running-jobs",
        "name": "Asynchronous Operations and Webhooks",
        "description": "Handling long-running background tasks with 202 Accepted, job status polling (/jobs/{id}), and HMAC-SHA256 signed webhooks.",
        "prerequisites": ["status-codes-and-errors", "idempotency-and-retries"],
        "domain": "REST API Design",
    },
    {
        "id": "api-security",
        "name": "API Authentication, Authorization, and Security",
        "description": "Auth mechanisms (API Keys, OAuth2/OIDC, JWT), OWASP API security, preventing BOLA, JWT pitfalls (alg: none), and strict CORS origin policies.",
        "prerequisites": ["http-methods", "status-codes-and-errors"],
        "domain": "REST API Design",
    },
    {
        "id": "ai-and-streaming-apis",
        "name": "AI APIs and Event Streaming",
        "description": "Server-Sent Events (SSE) with text/event-stream for LLM token streaming, token-based rate limits, RAG API architecture, and /health vs /ready endpoints.",
        "prerequisites": ["long-running-jobs", "request-response-design"],
        "domain": "REST API Design",
    },
    {
        "id": "api-architectures",
        "name": "API Architecture Comparison and Testing",
        "description": "Architectural trade-offs between REST, GraphQL, and gRPC; contract testing with TestClient; and automated OpenAPI specification generation.",
        "prerequisites": ["http-methods", "request-response-design"],
        "domain": "REST API Design",
    },
]


def setup_schema(conn: Neo4jConnection):
    """Ensure vector indexes and uniqueness constraints exist."""
    print("Setting up Neo4j schema & vector indexes...")
    conn.query("CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;")
    conn.query("""
        CREATE VECTOR INDEX concept_embedding IF NOT EXISTS
        FOR (c:Concept) ON (c.embedding)
        OPTIONS {indexConfig: {
          `vector.dimensions`: 384,
          `vector.similarity_function`: 'cosine'
        }}
    """)
    conn.query("""
        CREATE VECTOR INDEX pdf_chunk_embedding IF NOT EXISTS
        FOR (c:PDFChunk) ON (c.embedding)
        OPTIONS {indexConfig: {
          `vector.dimensions`: 384,
          `vector.similarity_function`: 'cosine'
        }}
    """)


def clean_old_data(conn: Neo4jConnection):
    """Remove prior curriculum data."""
    print("Cleaning out old Concept, PDFChunk, and PDFDocument nodes...")
    conn.query("MATCH (c:Concept) DETACH DELETE c")
    conn.query("MATCH (ch:PDFChunk) DETACH DELETE ch")
    conn.query("MATCH (d:PDFDocument) DETACH DELETE d")


def seed_concepts(conn: Neo4jConnection, model: SentenceTransformer) -> list[dict]:
    """Seed the 11 REST API Design concepts and prerequisite relationships."""
    print(f"\nSeeding {len(API_CONCEPTS)} REST API Design concepts with embeddings...")

    for c in API_CONCEPTS:
        text_for_embedding = f"{c['name']}. {c['description']}"
        embedding = model.encode(text_for_embedding).tolist()
        cypher = """
        MERGE (node:Concept {id: $id})
        SET node.name = $name,
            node.description = $description,
            node.domain = $domain,
            node.embedding = $embedding,
            node.updated_at = datetime()
        """
        conn.query(cypher, {
            "id": c["id"],
            "name": c["name"],
            "description": c["description"],
            "domain": c["domain"],
            "embedding": embedding,
        })
        print(f"  [Concept] {c['id']:<26} -> {c['name']}")

    edge_count = 0
    for c in API_CONCEPTS:
        for prereq_id in c.get("prerequisites", []):
            cypher_edge = """
            MATCH (prereq:Concept {id: $prereq_id}), (target:Concept {id: $target_id})
            MERGE (prereq)-[:IS_PREREQUISITE_FOR]->(target)
            """
            conn.query(cypher_edge, {"prereq_id": prereq_id, "target_id": c["id"]})
            edge_count += 1
            print(f"  [Edge] {prereq_id} -> {c['id']}")

    print(f"Seeded {len(API_CONCEPTS)} concepts and {edge_count} prerequisite edges.")
    return API_CONCEPTS


def ingest_api_pdf(conn: Neo4jConnection, model: SentenceTransformer, concepts: list[dict]):
    """Ingest api-design-cheat-sheet.pdf (4 pages) into PDFDocument & PDFChunk nodes."""
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF not found at {PDF_PATH}")

    file_name = os.path.basename(PDF_PATH)
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    file_hash = hashlib.sha256(file_bytes).hexdigest()
    doc_id = f"pdf-api-cheat-sheet-{file_hash[:12]}"

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page_count = len(doc)
    print(f"\nIngesting '{file_name}' ({page_count} pages, {len(file_bytes)/1024:.1f} KB)...")

    # Document node
    conn.query("""
        MERGE (d:PDFDocument {id: $id})
        SET d.file_name = $file_name,
            d.sha256 = $sha256,
            d.page_count = $page_count,
            d.embedding_model = $embedding_model,
            d.updated_at = datetime(),
            d.created_at = coalesce(d.created_at, datetime())
    """, {
        "id": doc_id,
        "file_name": file_name,
        "sha256": file_hash,
        "page_count": page_count,
        "embedding_model": MODEL_NAME,
    })

    total_chunks = 0
    all_chunks_data = []

    for page_idx in range(page_count):
        page = doc[page_idx]
        text = page.get_text("text") or ""
        chunks = _chunk_page_text(text, chunk_size=800, overlap=120)
        if not chunks:
            continue

        embeddings = model.encode(chunks)
        for c_idx, (chunk_text, emb) in enumerate(zip(chunks, embeddings), start=1):
            chunk_id = f"{doc_id}-p{page_idx + 1}-c{c_idx}"
            all_chunks_data.append({
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "file_name": file_name,
                "page_number": page_idx + 1,
                "chunk_number": c_idx,
                "content": chunk_text,
                "embedding": emb.tolist(),
            })
            total_chunks += 1

    doc.close()

    print(f"Creating {total_chunks} PDFChunk nodes in Neo4j...")
    batch_size = 50
    for i in range(0, len(all_chunks_data), batch_size):
        batch = all_chunks_data[i:i + batch_size]
        conn.query("""
            UNWIND $batch AS c
            MATCH (d:PDFDocument {id: c.document_id})
            MERGE (chunk:PDFChunk {id: c.chunk_id})
            SET chunk.document_id = c.document_id,
                chunk.file_name = c.file_name,
                chunk.page_number = c.page_number,
                chunk.chunk_number = c.chunk_number,
                chunk.content = c.content,
                chunk.embedding = c.embedding,
                chunk.updated_at = datetime()
            MERGE (d)-[:HAS_CHUNK]->(chunk)
        """, {"batch": batch})

    print(f"Created {total_chunks} PDFChunk nodes across {page_count} pages.")

    # Link chunks to relevant concepts
    print("Linking chunks to relevant REST API concepts...")
    link_count = 0
    for c in concepts:
        cypher_link = """
        CALL db.index.vector.queryNodes('pdf_chunk_embedding', 8, $concept_embedding)
        YIELD node AS chunk, score
        WHERE score >= 0.38
        MATCH (concept:Concept {id: $concept_id})
        MERGE (chunk)-[r:COVERS_CONCEPT]->(concept)
        SET r.relevance_score = score
        RETURN count(r) AS links
        """
        c_emb = model.encode(f"{c['name']}. {c['description']}").tolist()
        res = conn.query(cypher_link, {"concept_embedding": c_emb, "concept_id": c["id"]})
        if res:
            link_count += res[0].get("links", 0)

    print(f"Created {link_count} COVERS_CONCEPT semantic links between chunks and concepts.")


def main():
    print("=" * 65)
    print("  GraphMASAL — REST API Design Knowledge Seeder")
    print("=" * 65)

    conn = Neo4jConnection(
        os.getenv("NEO4J_URI", ""),
        os.getenv("NEO4J_USERNAME", ""),
        os.getenv("NEO4J_PASSWORD", ""),
    )
    model = SentenceTransformer(MODEL_NAME)

    setup_schema(conn)
    clean_old_data(conn)
    concepts = seed_concepts(conn, model)
    ingest_api_pdf(conn, model, concepts)

    from src.pathing.graph_adapter import GraphAdapter
    GraphAdapter.invalidate_cache()

    c_count = conn.query("MATCH (c:Concept) RETURN count(c) AS count")[0]["count"]
    r_count = conn.query("MATCH ()-[r:IS_PREREQUISITE_FOR]->() RETURN count(r) AS count")[0]["count"]
    ch_count = conn.query("MATCH (ch:PDFChunk) RETURN count(ch) AS count")[0]["count"]
    d_count = conn.query("MATCH (d:PDFDocument) RETURN count(d) AS count")[0]["count"]

    conn.close()

    print("\n" + "=" * 65)
    print("  VERIFICATION:")
    print(f"    Concepts in Neo4j          : {c_count}")
    print(f"    Prerequisite edges         : {r_count}")
    print(f"    PDF Documents              : {d_count}")
    print(f"    PDF Chunks indexed         : {ch_count}")
    print("=" * 65)
    print("  Database successfully seeded with REST API Design curriculum!")


if __name__ == "__main__":
    main()
