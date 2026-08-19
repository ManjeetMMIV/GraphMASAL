from fastapi import HTTPException
from pydantic import BaseModel
from fastapi import UploadFile

from src.api.dependencies import get_neo4j_connection, bootstrap_student
from src.ingestion.pdf_pipeline import PdfEmbeddingPipeline

class ExtractConceptsRequest(BaseModel):
    student_id: str

class ResetRequest(BaseModel):
    student_id: str

def list_documents_logic(student_id: str):
    conn = get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        pipeline = PdfEmbeddingPipeline(conn, student_id=student_id)
        docs = pipeline.list_recent_documents(limit=50)
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

def extract_concepts_logic(req: ExtractConceptsRequest):
    bootstrap_student(req.student_id)
    
    conn = get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        records = conn.query(
            """
            MATCH (s:Student {id: $student_id})-[:HAS_UPLOADED]->(d:PDFDocument)-[:HAS_CHUNK]->(c:PDFChunk)
            RETURN d.id AS doc_id, d.file_name AS file_name,
                   collect(c.content) AS chunks
            """,
            {"student_id": req.student_id}
        )
        if not records:
            return {"status": "ok", "message": "No PDFDocument nodes found for this student.", "total_concepts": 0}

        pipeline = PdfEmbeddingPipeline(conn, student_id=req.student_id)
        pipeline.initialize_concept_schema()

        total_concepts = 0
        results = []
        for rec in records:
            doc_id = rec["doc_id"]
            file_name = rec["file_name"]
            chunks = rec["chunks"] or []
            count = pipeline._extract_and_store_concepts(doc_id, file_name, chunks)
            total_concepts += count
            results.append({"file": file_name, "concepts_extracted": count})

        from src.pathing.graph_adapter import GraphAdapter
        GraphAdapter.invalidate_cache(req.student_id)

        return {"status": "ok", "total_concepts": total_concepts, "documents": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

async def upload_pdf_logic(student_id: str, file: UploadFile):
    conn = get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        bootstrap_student(student_id)
        bytes_data = await file.read()
        pipeline = PdfEmbeddingPipeline(conn, student_id=student_id)
        pipeline.initialize_concept_schema()
        result = pipeline.ingest_pdf_bytes(file.filename, bytes_data)
        from src.pathing.graph_adapter import GraphAdapter
        GraphAdapter.invalidate_cache(student_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

def delete_all_documents_logic(student_id: str):
    conn = get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        conn.query(
            "MATCH (s:Student {id: $student_id})-[:HAS_UPLOADED]->(d:PDFDocument)-[:HAS_CHUNK]->(c:PDFChunk) DETACH DELETE c",
            {"student_id": student_id}
        )
        result = conn.query(
            "MATCH (s:Student {id: $student_id})-[:HAS_UPLOADED]->(d:PDFDocument) DETACH DELETE d RETURN count(d) as deleted",
            {"student_id": student_id}
        )
        conn.query(
            "MATCH (s:Student {id: $student_id})-[r:HAS_EXTRACTED]->(:Concept) DELETE r",
            {"student_id": student_id}
        )
        
        from src.pathing.graph_adapter import GraphAdapter
        GraphAdapter.invalidate_cache(student_id)
        
        deleted = result[0]["deleted"] if result else 0
        return {"status": "success", "documents_deleted": deleted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

def reset_data_logic(req: ResetRequest):
    conn = get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        conn.query("MATCH (:Student {id: $id})-[:REMEMBERS]->(m:Memory) DETACH DELETE m", {"id": req.student_id})
        conn.query("MATCH (:Student {id: $id})-[r:HAS_MASTERY_OF]->(c:Concept) DELETE r", {"id": req.student_id})
        conn.query("MATCH (c:PDFChunk) DETACH DELETE c")
        conn.query("MATCH (d:PDFDocument) DETACH DELETE d")
        
        from src.storage.qa_store import delete_student_history
        docs_deleted = delete_student_history(req.student_id)
        
        from src.pathing.graph_adapter import GraphAdapter
        GraphAdapter.invalidate_cache(req.student_id)
        
        return {"status": "success", "message": f"All data cleared: memories, mastery, PDFs, and {docs_deleted} chat turns."}
    finally:
        conn.close()
