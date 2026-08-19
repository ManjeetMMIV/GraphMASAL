from fastapi import APIRouter
from src.api.controllers.media_controller import (
    LectureRequest,
    PPTRequest,
    generate_lecture_logic,
    generate_ppt_logic
)

router = APIRouter(tags=["Media"])

@router.post("/api/lecture/generate")
async def generate_lecture(req: LectureRequest):
    return await generate_lecture_logic(req)

@router.post("/api/ppt/generate")
async def generate_ppt(req: PPTRequest):
    return generate_ppt_logic(req)
