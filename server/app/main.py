from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router


app = FastAPI(
    title="DQ Report Backend",
    version="0.1.0",
    description="Backend service for the intelligent report generation platform.",
)

# Allow frontend (Vite dev server) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 如需限制可改为 ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All business APIs are mounted under /api
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def root_health() -> dict:
    """Simple root health check for quick verification."""
    return {"status": "ok"}

