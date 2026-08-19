import os
import uvicorn
from src.api.server import app

if __name__ == "__main__":
    # Local development server
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
