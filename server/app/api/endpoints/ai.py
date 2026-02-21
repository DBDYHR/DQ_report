import httpx
from fastapi import APIRouter, Depends, HTTPException

from ...deps import get_ai_client
from ...models.ai import (
    OpenReportRequest,
    OpenReportResponse,
    SearchForReportRequest,
    SearchForReportResponse,
)
from ...services.ai_client import AiClient


router = APIRouter()


@router.post(
    "/search-for-report",
    response_model=SearchForReportResponse,
    summary="Search for report materials (pre-step before generation)",
)
async def search_for_report(
    body: SearchForReportRequest,
    client: AiClient = Depends(get_ai_client),
) -> SearchForReportResponse:
    try:
        data = await client.search_for_report(body)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return SearchForReportResponse(**data)


@router.post(
    "/open-report",
    response_model=OpenReportResponse,
    summary="Generate or polish an open report with AI",
)
async def generate_open_report(
    body: OpenReportRequest,
    client: AiClient = Depends(get_ai_client),
) -> OpenReportResponse:
    try:
        content = await client.generate_open_report(body)
    except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
        raise HTTPException(
            status_code=503,
            detail="无法连接到 AI 服务，请检查网络连接或代理设置（如设置了 HTTP_PROXY/HTTPS_PROXY）。",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return OpenReportResponse(content=content)

