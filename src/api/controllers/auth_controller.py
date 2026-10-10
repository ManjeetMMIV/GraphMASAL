from fastapi import HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from src.storage.qa_store import (
    register_user,
    verify_user,
    create_auth_token,
    revoke_auth_token,
)


class RegisterRequest(BaseModel):
    user_id: str
    password: str
    role: str  # "student" or "teacher"


class LoginRequest(BaseModel):
    user_id: str
    password: str
    role: str  # "student" or "teacher"


def register_logic(req: RegisterRequest):
    """Register a new student or teacher account."""
    if req.role not in ("student", "teacher"):
        raise HTTPException(status_code=400, detail="role must be 'student' or 'teacher'")
    if not req.user_id.strip() or not req.password:
        raise HTTPException(status_code=400, detail="user_id and password are required")
    created = register_user(req.user_id.strip(), req.password, req.role)
    if not created:
        raise HTTPException(status_code=409, detail="User ID already registered")
    token = create_auth_token(req.user_id.strip(), req.role)
    return {"token": token, "user_id": req.user_id.strip(), "role": req.role}


def login_logic(req: LoginRequest):
    """Authenticate and return a session token."""
    if not verify_user(req.user_id.strip(), req.password, req.role):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_auth_token(req.user_id.strip(), req.role)
    return {"token": token, "user_id": req.user_id.strip(), "role": req.role}


def logout_logic(authorization: Optional[str]):
    """Revoke the caller's token."""
    token = _extract_token(authorization)
    revoke_auth_token(token)
    return {"status": "ok"}


def _extract_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return authorization.removeprefix("Bearer ").strip()
