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


import fitz  # PyMuPDF

class PdfEmbeddingPipeline:
    def __init__(self, conn: Neo4jConnection, model_name: str = "all-MiniLM-L6-v2", student_id: str = None):
        self.conn = conn
        self.model_name = model_name
        self.student_id = student_id
        self.model = _get_embedding_model(model_name)

    def initialize_concept_schema(self) -> None:
        """Create constraints and vector index for Concept nodes."""
        self.conn.query(
            "CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;"
        )
        self.conn.query(
            """
            CREATE VECTOR INDEX concept_embedding IF NOT EXISTS
            FOR (c:Concept) ON (c.embedding)
            OPTIONS {indexConfig: {
             `vector.dimensions`: 384,
             `vector.similarity_function`: 'cosine'
            }}
            """
        )

    def _extract_and_store_concepts(
        self, document_id: str, file_name: str, all_chunks: list[str]
    ) -> int:
        """
        Use GPT to extract an ordered list of key concepts from the document chunks,
        then store them as Concept nodes with IS_PREREQUISITE_FOR edges in Neo4j.
        Returns the number of concepts created.
        """
        import os
        from openai import OpenAI

        if not all_chunks:
            return 0

        # Concatenate a representative sample of the document (max 6000 chars)
        sample_text = "\n\n".join(all_chunks)[:6000]

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert curriculum designer. Extract the key learning concepts "
                            "from the following document text. Return ONLY a JSON array of objects in "
                            "learning order (foundational first), where each object has:\n"
                            '  "id": a slugified lowercase string (e.g. "von-neumann-architecture"),\n'
                            '  "name": the human-readable concept name,\n'
                            '  "description": one sentence describing the concept.\n'
                            "Return 5–15 concepts. No markdown, just raw JSON."
                        ),
                    },
                    {"role": "user", "content": f"Document: {file_name}\n\n{sample_text}"},
                ],
                max_tokens=1200,
                temperature=0,
            )
        except Exception as e:
            logging.warning(f"Concept extraction LLM call failed: {e}")
            return 0

        raw = (response.choices[0].message.content or "").strip()

        import json
        try:
            # Strip optional markdown code fences
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            concepts: list[dict] = json.loads(raw)
        except Exception as e:
            logging.warning(f"Failed to parse concept JSON: {e}\nRaw: {raw[:300]}")
            return 0

        if not isinstance(concepts, list) or not concepts:
            return 0

        # Store each concept with an embedding
        stored = 0
        concept_ids: list[str] = []
        for concept in concepts:
            c_id = concept.get("id", "").strip()
            c_name = concept.get("name", "").strip()
            c_desc = concept.get("description", "").strip()
            if not c_id or not c_name:
                continue

            embedding = self.model.encode(f"{c_name}. {c_desc}").tolist()
            self.conn.query(
                """
                MERGE (c:Concept {id: $id})
                SET c.name = $name,
                    c.description = $desc,
                    c.source_document = $doc_id,
                    c.embedding = $embedding,
                    c.updated_at = datetime(),
                    c.created_at = coalesce(c.created_at, datetime())
                """,
                {"id": c_id, "name": c_name, "desc": c_desc, "doc_id": document_id, "embedding": embedding},
            )
            
            if self.student_id:
                self.conn.query(
                    """
                    MERGE (s:Student {id: $student_id})
                    WITH s
                    MATCH (c:Concept {id: $concept_id})
                    MERGE (s)-[:HAS_EXTRACTED]->(c)
                    """,
                    {"student_id": self.student_id, "concept_id": c_id}
                )

            concept_ids.append(c_id)
            stored += 1

        # Create IS_PREREQUISITE_FOR edges between consecutive concepts (document order)
        for i in range(len(concept_ids) - 1):
            self.conn.query(
                """
                MATCH (a:Concept {id: $from_id}), (b:Concept {id: $to_id})
                MERGE (a)-[:IS_PREREQUISITE_FOR]->(b)
                """,
                {"from_id": concept_ids[i], "to_id": concept_ids[i + 1]},
            )

        logging.info(f"Extracted and stored {stored} concepts from '{file_name}'.")
        return stored

    def ingest_pdf_bytes(self, file_name: str, file_bytes: bytes) -> dict:
        print(f"DEBUG: ingest_pdf_bytes called with file_bytes length: {len(file_bytes)}")
        # Load document from bytes using PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
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
                "page_count": len(doc),
                "embedding_model": self.model_name,
            },
        )

        if self.student_id:
            self.conn.query(
                """
                MERGE (s:Student {id: $student_id})
                WITH s
                MATCH (d:PDFDocument {id: $document_id})
                MERGE (s)-[:HAS_UPLOADED]->(d)
                """,
                {"student_id": self.student_id, "document_id": document_id}
            )

        import base64
        import os
        from openai import OpenAI

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        chunk_count = 0
        all_chunk_texts: list[str] = []  # collect for concept extraction

        for page_index in range(len(doc)):
            page = doc[page_index]
            # PyMuPDF extraction
            page_text = page.get_text("text") or ""
            images = page.get_images(full=True)

            # OpenAI Vision OCR Fallback for pages with negligible text
            if len(page_text.strip()) < 50:
                logging.warning(f"DEBUG: Triggering OCR fallback for Page {page_index + 1} (text length: {len(page_text.strip())}, images: {len(images)})")
                pix = page.get_pixmap(dpi=150)
                base64_image = base64.b64encode(pix.tobytes("png")).decode("utf-8")

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Extract all readable text from this scanned document page. Return ONLY the extracted text, formatting it as cleanly as possible. If there is no text, return nothing."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                                ]
                            }
                        ],
                        max_tokens=2000
                    )
                    ocr_text = response.choices[0].message.content or ""
                    page_text += "\n" + ocr_text.strip()
                except Exception as e:
                    print(f"DEBUG: OCR failed for Page {page_index + 1}: {e}")

            page_chunks = _chunk_page_text(page_text)
            if not page_chunks:
                continue

            all_chunk_texts.extend(page_chunks)  # collect for concept extraction
            embeddings = self.model.encode(page_chunks)
            for idx, (chunk_text, embedding) in enumerate(zip(page_chunks, embeddings), start=1):
                chunk_id = f"{document_id}-p{page_index + 1}-c{idx}"
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
                        "page_number": page_index + 1,
                        "chunk_number": idx,
                        "content": chunk_text,
                        "embedding": embedding.tolist(),
                    },
                )
                chunk_count += 1  # ← was missing before, caused 0 chunks reported

        page_count_total = len(doc)
        doc.close()

        # Extract and store concepts from all collected chunks
        self.initialize_concept_schema()
        concept_count = self._extract_and_store_concepts(document_id, file_name, all_chunk_texts)
        logging.info(f"Ingestion complete: {chunk_count} chunks, {concept_count} concepts for '{file_name}'")

        return {
            "document_id": document_id,
            "file_name": file_name,
            "page_count": page_count_total,
            "chunk_count": chunk_count,
            "concept_count": concept_count,
            "sha256": file_hash,
        }


    def list_recent_documents(self, limit: int = 10) -> list[dict]:
        match_clause = "MATCH (d:PDFDocument)"
        params = {"limit": limit}
        
        if self.student_id:
            match_clause = "MATCH (s:Student {id: $student_id})-[:HAS_UPLOADED]->(d:PDFDocument)"
            params["student_id"] = self.student_id

        records = self.conn.query(
            f"""
            {match_clause}
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:PDFChunk)
            RETURN d.id AS document_id,
                   d.file_name AS file_name,
                   d.page_count AS page_count,
                   count(c) AS chunk_count,
                   d.updated_at AS updated_at
            ORDER BY d.updated_at DESC
            LIMIT $limit
            """,
            params,
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