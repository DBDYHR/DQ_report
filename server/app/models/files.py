from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class UploadedFileInfo(BaseModel):
    """Information about an uploaded and parsed file."""

    file_id: str
    name: str
    content_type: str
    text: str
    summary: Optional[str] = None

