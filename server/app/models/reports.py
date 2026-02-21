from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ReportBase(BaseModel):
    """Base fields shared by all report models."""

    title: str
    type: str = Field(default="open_report", description="Report type identifier")
    content: str
    sources: List[str] = []


class ReportCreate(ReportBase):
    """Payload for creating a new report."""

    pass


class ReportUpdate(BaseModel):
    """Partial update of a report."""

    title: Optional[str] = None
    content: Optional[str] = None
    sources: Optional[List[str]] = None


class Report(ReportBase):
    """Full report representation returned by API."""

    id: str
    create_time: datetime
    update_time: datetime

