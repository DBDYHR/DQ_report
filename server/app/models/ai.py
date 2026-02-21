from __future__ import annotations

from typing import List, Optional, Dict, Any

from pydantic import BaseModel


class Material(BaseModel):
    """Text material parsed from uploaded files."""

    file_id: Optional[str] = None
    name: Optional[str] = None
    text: str
    summary: Optional[str] = None


class SearchResultItem(BaseModel):
    """单条检索结果，用于 API 透传。"""

    title: str
    snippet: str
    url: str


class PrefetchedSearch(BaseModel):
    """预取的检索结果，供 open-report 直接使用。"""

    query: str
    results: List[SearchResultItem] = []


class OpenReportRequest(BaseModel):
    """Request body for open-report AI generation."""

    task_type: str = "open_report"
    title: Optional[str] = None
    outline: Optional[str] = None
    draft: Optional[str] = None
    materials: List[Material] = []
    user_config: Optional[Dict[str, Any]] = None
    # 可选：前端先调用 search-for-report 获取结果，确认后带上此字段，跳过检索
    search_results: Optional[PrefetchedSearch] = None


class OpenReportResponse(BaseModel):
    """Simplified AI response body."""

    content: str


class SearchForReportRequest(BaseModel):
    """Request body for search-for-report，与 open-report 的 payload 结构一致。"""

    task_type: str = "open_report"
    title: Optional[str] = None
    outline: Optional[str] = None
    draft: Optional[str] = None
    materials: List[Material] = []
    user_config: Optional[Dict[str, Any]] = None


class SearchForReportResponse(BaseModel):
    """检索结果，供前端展示并确认。"""

    query: str
    results: List[SearchResultItem]

