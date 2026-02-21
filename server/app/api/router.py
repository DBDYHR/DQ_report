from fastapi import APIRouter

from .endpoints import ai, files, health, reports


api_router = APIRouter()

# /api/health
api_router.include_router(health.router, tags=["health"])

# /api/ai/...
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])

# /api/files/...
api_router.include_router(files.router, prefix="/files", tags=["files"])

# /api/reports/...
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

