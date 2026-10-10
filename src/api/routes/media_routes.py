from fastapi import APIRouter, Depends
from src.api.dependencies import get_current_user
from src.api.controllers.media_controller import (
    LectureRequest,
    PPTRequest,
    NotesRequest,
    generate_lecture_logic,
    generate_ppt_logic,
    generate_notes_logic,
)

router = APIRouter(tags=["Media"], dependencies=[Depends(get_current_user)])

@router.post("/api/lecture/generate")
async def generate_lecture(req: LectureRequest):
    return await generate_lecture_logic(req)

@router.post("/api/ppt/generate")
async def generate_ppt(req: PPTRequest):
    return generate_ppt_logic(req)

@router.post("/api/notes/generate")
async def generate_notes(req: NotesRequest):
    return generate_notes_logic(req)
