from fastapi import APIRouter, Depends
from src.api.dependencies import get_current_user
from src.api.controllers.sessions_controller import (
    NewSessionRequest,
    create_new_session,
    list_sessions,
    get_session,
    delete_session_logic
)

router = APIRouter(prefix="/api/sessions", tags=["Sessions"], dependencies=[Depends(get_current_user)])
session_router = APIRouter(prefix="/api/session", tags=["Session"], dependencies=[Depends(get_current_user)])

@router.post("/new")
async def new_session_route(req: NewSessionRequest):
    return create_new_session(req)

@router.get("")
async def list_sessions_route(student_id: str):
    return list_sessions(student_id)

@session_router.get("/{session_id}")
async def get_session_route(session_id: str):
    return get_session(session_id)

@session_router.delete("/{session_id}")
async def delete_session_route(session_id: str):
    return delete_session_logic(session_id)
