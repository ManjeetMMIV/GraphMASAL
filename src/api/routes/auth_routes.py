from fastapi import APIRouter, Header
from typing import Optional
from src.api.controllers.auth_controller import (
    RegisterRequest,
    LoginRequest,
    register_logic,
    login_logic,
    logout_logic,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register")
async def register(req: RegisterRequest):
    return register_logic(req)


@router.post("/login")
async def login(req: LoginRequest):
    return login_logic(req)


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(default=None)):
    return logout_logic(authorization)
