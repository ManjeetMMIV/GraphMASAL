from fastapi import APIRouter, Request
from src.api.controllers.chat_controller import (
    ChatRequest,
    chat_stream_logic
)

router = APIRouter(tags=["Chat"])

@router.post("/api/chat")
async def chat_stream(request: Request, body: ChatRequest):
    return await chat_stream_logic(request, body)
