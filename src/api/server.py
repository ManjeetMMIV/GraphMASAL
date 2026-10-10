import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="GraphMASAL API", version="1.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from src.api.routes import (
    auth_routes,
    sessions_routes,
    graph_routes,
    documents_routes,
    teacher_routes,
    media_routes,
    chat_routes,
    ui_routes
)

app.include_router(auth_routes.router)
app.include_router(sessions_routes.router)
app.include_router(sessions_routes.session_router)
app.include_router(graph_routes.router)
app.include_router(documents_routes.router)
app.include_router(teacher_routes.router)
app.include_router(media_routes.router)
app.include_router(chat_routes.router)
app.include_router(ui_routes.router)

# Mount static files (for css/js/audio/presentations)
REPO_ROOT = Path(__file__).resolve().parents[2]
public_dir = REPO_ROOT / "public"
public_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(public_dir)), name="static")
app.mount("/audio", StaticFiles(directory=str(public_dir / "audio")), name="audio")
app.mount("/presentations", StaticFiles(directory=str(public_dir / "presentations")), name="presentations")

if __name__ == "__main__":
    import uvicorn
    # Render binds to $PORT
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=port, reload=True)
