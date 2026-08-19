from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Setup Jinja2 templates
REPO_ROOT = Path(__file__).resolve().parents[3]
templates = Jinja2Templates(directory=str(REPO_ROOT / "src" / "ui" / "templates"))

router = APIRouter(tags=["UI"])

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
