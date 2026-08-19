from fastapi import APIRouter, File, Form, UploadFile
from src.api.controllers.documents_controller import (
    ExtractConceptsRequest,
    ResetRequest,
    list_documents_logic,
    extract_concepts_logic,
    upload_pdf_logic,
    delete_all_documents_logic,
    reset_data_logic
)

router = APIRouter(tags=["Documents"])

@router.get("/api/documents")
async def list_documents(student_id: str):
    return list_documents_logic(student_id)

@router.post("/api/extract_concepts")
async def extract_concepts(req: ExtractConceptsRequest):
    return extract_concepts_logic(req)

@router.post("/api/upload_pdf")
async def upload_pdf(student_id: str = Form(...), file: UploadFile = File(...)):
    return await upload_pdf_logic(student_id, file)

@router.delete("/api/documents")
async def delete_all_documents(student_id: str):
    return delete_all_documents_logic(student_id)

@router.post("/api/reset")
async def reset_data(req: ResetRequest):
    return reset_data_logic(req)
