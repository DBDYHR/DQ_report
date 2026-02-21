from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from ..models.reports import Report, ReportCreate, ReportUpdate


class ReportsStore:
    """Very simple JSON-file–backed storage for reports.

    This is suitable for initial development and single-user usage.
    Later you can replace this with a real database implementation.
    """

    def __init__(self, data_dir: Path) -> None:
        self._path = data_dir / "reports.json"

    def _load_all(self) -> List[dict]:
        if not self._path.exists():
            return []
        with self._path.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _save_all(self, items: List[dict]) -> None:
        self._path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list_reports(self) -> List[Report]:
        items = self._load_all()
        return [self._to_model(item) for item in items]

    def create_report(self, payload: ReportCreate) -> Report:
        items = self._load_all()
        now = datetime.now(timezone.utc).isoformat()
        report_id = f"rpt_{uuid.uuid4().hex[:8]}"

        new_item = {
            "id": report_id,
            "title": payload.title,
            "type": payload.type,
            "content": payload.content,
            "sources": payload.sources,
            "create_time": now,
            "update_time": now,
        }
        items.insert(0, new_item)
        self._save_all(items)
        return self._to_model(new_item)

    def get_report(self, report_id: str) -> Optional[Report]:
        items = self._load_all()
        for item in items:
            if item.get("id") == report_id:
                return self._to_model(item)
        return None

    def update_report(self, report_id: str, payload: ReportUpdate) -> Optional[Report]:
        items = self._load_all()
        updated: Optional[dict] = None
        for item in items:
            if item.get("id") == report_id:
                if payload.title is not None:
                    item["title"] = payload.title
                if payload.content is not None:
                    item["content"] = payload.content
                if payload.sources is not None:
                    item["sources"] = payload.sources
                item["update_time"] = datetime.now(timezone.utc).isoformat()
                updated = item
                break

        if updated is None:
            return None

        self._save_all(items)
        return self._to_model(updated)

    def delete_report(self, report_id: str) -> bool:
        """Delete a report by id. Returns True if something was deleted."""
        items = self._load_all()
        new_items = [item for item in items if item.get("id") != report_id]
        if len(new_items) == len(items):
            return False
        self._save_all(new_items)
        return True

    def _to_model(self, data: dict) -> Report:
        return Report(
            id=str(data.get("id")),
            title=str(data.get("title", "")),
            type=str(data.get("type", "")),
            content=str(data.get("content", "")),
            sources=list(data.get("sources") or []),
            create_time=datetime.fromisoformat(str(data.get("create_time"))),
            update_time=datetime.fromisoformat(str(data.get("update_time"))),
        )

