from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import List

from ddgs import DDGS


@dataclass
class SearchResult:
    title: str
    snippet: str
    url: str


class SearchClient:
    """DuckDuckGo 真实网页搜索，使用 ddgs 库获取搜索结果。"""

    async def search(
        self, query: str, max_results: int = 5, timeout: float = 15.0
    ) -> List[SearchResult]:
        """搜索 DuckDuckGo 并返回网页结果列表。"""
        if not query.strip():
            return []

        def _do_search() -> List[SearchResult]:
            results: list[SearchResult] = []
            try:
                ddgs = DDGS(timeout=int(timeout))
                raw = ddgs.text(query, max_results=max_results, region="wt-wt")
                for item in raw or []:
                    if not isinstance(item, dict):
                        continue
                    title = str(item.get("title") or "").strip()
                    href = str(item.get("href") or item.get("url") or "").strip()
                    body = str(item.get("body") or item.get("snippet") or "").strip()
                    if title or body:
                        results.append(
                            SearchResult(
                                title=title or "无标题",
                                snippet=body[:400] if body else "",
                                url=href,
                            )
                        )
                    if len(results) >= max_results:
                        break
            except Exception:
                raise
            return results[:max_results]

        return await asyncio.to_thread(_do_search)
