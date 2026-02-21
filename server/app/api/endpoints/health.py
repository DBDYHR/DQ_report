from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
async def api_health() -> dict:
    """Health check under /api/health."""
    return {"status": "ok"}

