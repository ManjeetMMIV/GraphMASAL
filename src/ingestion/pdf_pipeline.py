import hashlib
import logging
import os
import re
from contextlib import redirect_stderr, redirect_stdout
from functools import lru_cache
from io import BytesIO, StringIO

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from src.graph.db import Neo4jConnection


def _verbose_pdf_ingestion() -> bool:
    return os.getenv("GRAPHMASAL_VERBOSE_INGESTION", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "pdf"


@lru_cache(maxsize=2)
def _get_embedding_model(model_name: str) -> SentenceTransformer:
    verbose = _verbose_pdf_ingestion()
    if verbose:
        return SentenceTransformer(model_name)

    logging.getLogger("transformers").setLevel(logging.ERROR)
    logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
        return SentenceTransformer(model_name)


def _chunk_page_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        if end < len(cleaned):
            split_at = cleaned.rfind(" ", start, end)
            if split_at > start + (chunk_size // 2):
                end = split_at

        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(cleaned):
            break
        start = max(end - overlap, start + 1)

    return chunks


class PdfEmbeddingPipeline:
    def __init__(self, conn: Neo4jConnection, model_name: str = "all-MiniLM-L6-v2"):
        self.conn = conn
        self.model_name = model_name
        self.model = _get_embedding_model(model_name)

    def initialize_schema(self) -> None:
        self.conn.query(
            "CREATE CONSTRAINT pdf_document_id IF NOT EXISTS FOR (d:PDFDocument) REQUIRE d.id IS UNIQUE;"
        )
        self.conn.query(
            "CREATE CONSTRAINT pdf_chunk_id IF NOT EXISTS FOR (c:PDFChunk) REQUIRE c.id IS UNIQUE;"
        )
        self.conn.query(
            """
            CREATE VECTOR INDEX pdf_chunk_embedding IF NOT EXISTS
            FOR (c:PDFChunk) ON (c.embedding)
            OPTIONS {indexConfig: {
             `vector.dimensions`: 384,
             `vector.similarity_function`: 'cosine'
            }}
            """
        )

    def ingest_pdf_bytes(self, file_name: str, file_bytes: bytes) -> dict:
        reader = PdfReader(BytesIO(file_bytes))
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        base_id = _slugify(PathSafe.stem(file_name))
        document_id = f"pdf-{base_id}-{file_hash[:12]}"

        self.conn.query(
            """
            MERGE (d:PDFDocument {id: $id})
            SET d.file_name = $file_name,
                d.sha256 = $sha256,
                d.page_count = $page_count,
                d.embedding_model = $embedding_model,
                d.updated_at = datetime(),
                d.created_at = coalesce(d.created_at, datetime())
            """,
            {
                "id": document_id,
                "file_name": file_name,
                "sha256": file_hash,
                "page_count": len(reader.pages),
                "embedding_model": self.model_name,
            },
        )

        chunk_count = 0
        for page_index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            page_chunks = _chunk_page_text(page_text)
            if not page_chunks:
                continue

            embeddings = self.model.encode(page_chunks)
            for idx, (chunk_text, embedding) in enumerate(zip(page_chunks, embeddings), start=1):
                chunk_id = f"{document_id}-p{page_index}-c{idx}"
                self.conn.query(
                    """
                    MATCH (d:PDFDocument {id: $document_id})
                    MERGE (c:PDFChunk {id: $chunk_id})
                    SET c.document_id = $document_id,
                        c.file_name = $file_name,
                        c.page_number = $page_number,
                        c.chunk_number = $chunk_number,
                        c.content = $content,
                        c.embedding = $embedding,
                        c.updated_at = datetime(),
                        c.created_at = coalesce(c.created_at, datetime())
                    MERGE (d)-[:HAS_CHUNK]->(c)
                    """,
                    {
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "file_name": file_name,
                        "page_number": page_index,
                        "chunk_number": idx,
                        "content": chunk_text,
                        "embedding": embedding.tolist(),
                    },
                )
                chunk_count += 1

        return {
            "document_id": document_id,
            "file_name": file_name,
            "page_count": len(reader.pages),
            "chunk_count": chunk_count,
            "sha256": file_hash,
        }

    def list_recent_documents(self, limit: int = 10) -> list[dict]:
        records = self.conn.query(
            """
            MATCH (d:PDFDocument)
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:PDFChunk)
            RETURN d.id AS document_id,
                   d.file_name AS file_name,
                   d.page_count AS page_count,
                   count(c) AS chunk_count,
                   d.updated_at AS updated_at
            ORDER BY d.updated_at DESC
            LIMIT $limit
            """,
            {"limit": limit},
        )
        if not records:
            return []
            
        return [
            {
                "document_id": record["document_id"],
                "file_name": record["file_name"],
                "page_count": record["page_count"],
                "chunk_count": record["chunk_count"],
                "updated_at": str(record["updated_at"]),
            }
            for record in records
        ]


class PathSafe:
    @staticmethod
    def stem(file_name: str) -> str:
        normalized = file_name.replace("\\", "/").rsplit("/", 1)[-1]
        if "." in normalized:
            return normalized.rsplit(".", 1)[0]
        return normalized