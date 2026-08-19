import os
import uvicorn
from src.api.server import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    is_dev = os.environ.get("RENDER") is None  # RENDER env var is set automatically on Render
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=is_dev,      # reload only in local dev, NOT on Render
        workers=1 if is_dev else None,
    )
