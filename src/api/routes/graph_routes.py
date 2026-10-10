from fastapi import APIRouter, Depends
from src.api.dependencies import get_current_user
from src.api.controllers.graph_controller import (
    ComputePathRequest,
    SelectPlanRequest,
    get_roadmap_logic,
    list_concepts_logic,
    compute_path_logic,
    select_plan_logic,
    get_knowledge_graph_logic,
    get_videos_logic,
)

router = APIRouter(tags=["Graph"], dependencies=[Depends(get_current_user)])

@router.get("/api/roadmap")
async def get_roadmap(student_id: str, session_id: str = ""):
    return get_roadmap_logic(student_id, session_id)

@router.get("/api/concepts")
async def list_concepts(student_id: str):
    return list_concepts_logic(student_id)

@router.post("/api/compute_path")
async def compute_path(req: ComputePathRequest):
    return compute_path_logic(req)

@router.post("/api/select_plan")
async def select_plan(req: SelectPlanRequest):
    return select_plan_logic(req)

@router.get("/api/knowledge_graph")
async def get_knowledge_graph(student_id: str, session_id: str = ""):
    return get_knowledge_graph_logic(student_id, session_id)

@router.get("/api/videos")
async def get_videos(student_id: str, session_id: str = ""):
    return get_videos_logic(student_id, session_id)
