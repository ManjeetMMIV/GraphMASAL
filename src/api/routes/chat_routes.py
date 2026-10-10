from fastapi import APIRouter, Depends, Request
from src.api.dependencies import get_current_user
from src.api.controllers.chat_controller import (
    ChatRequest,
    chat_stream_logic
)

router = APIRouter(tags=["Chat"], dependencies=[Depends(get_current_user)])

@router.post("/api/chat")
async def chat_stream(request: Request, body: ChatRequest):
    return await chat_stream_logic(request, body)
