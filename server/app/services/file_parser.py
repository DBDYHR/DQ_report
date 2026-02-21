from __future__ import annotations

import io
import uuid
from pathlib import Path

import pdfplumber
import docx  # type: ignore[import-untyped]
from fastapi import HTTPException, UploadFile

from ..models.files import UploadedFileInfo


async def save_and_parse_upload(file: UploadFile, uploads_dir: Path) -> UploadedFileInfo:
    """Save an uploaded file and extract plain text & a short summary."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".txt", ".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="Unsupported file type, only .txt/.pdf/.docx are supported.")

    file_id = str(uuid.uuid4())
    target_path = uploads_dir / f"{file_id}{suffix}"

    raw_bytes = await file.read()
    target_path.write_bytes(raw_bytes)

    if suffix == ".txt":
        text = raw_bytes.decode("utf-8", errors="ignore")
    elif suffix == ".pdf":
        text = _extract_text_from_pdf(raw_bytes)
    else:  # .docx
        text = _extract_text_from_docx(raw_bytes)

    text = text.strip()
    summary = text[:2000]  # naive summary: first N characters

    return UploadedFileInfo(
        file_id=file_id,
        name=file.filename or file_id,
        content_type=file.content_type or "application/octet-stream",
        text=text,
        summary=summary,
    )


def _extract_text_from_pdf(raw_bytes: bytes) -> str:
    """Extract text from a PDF using pdfplumber."""
    buf = io.BytesIO(raw_bytes)
    text_parts: list[str] = []
    with pdfplumber.open(buf) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_text_from_docx(raw_bytes: bytes) -> str:
    """Extract text from a DOCX using python-docx."""
    buf = io.BytesIO(raw_bytes)
    document = docx.Document(buf)
    paragraphs = [p.text for p in document.paragraphs if p.text]
    return "\n".join(paragraphs)

