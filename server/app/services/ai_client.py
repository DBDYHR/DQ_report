from __future__ import annotations

import traceback
from textwrap import dedent
from typing import Any, Dict, List, Tuple

import httpx

from ..config import Settings
from ..models.ai import OpenReportRequest, PrefetchedSearch, SearchForReportRequest, SearchResultItem
from .search_client import SearchClient, SearchResult


class AiClient:
    """Wrapper around a yeysai / OpenAI-style chat completion endpoint.

    同时封装一个“深度检索”流程（简化版）：
    - 当 payload.user_config.web_search_enabled 为 True 时：
      1) 从 payload 构建 1 个简单 query；
      2) 单次 DuckDuckGo 搜索；
      3) 调用模型综合搜索结果和原始材料生成报告。
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._search_client = SearchClient()

    async def generate_open_report(self, payload: OpenReportRequest) -> str:
        """根据配置选择普通模式或深度检索模式.

        - 若 payload.search_results 非空：直接使用预取的检索结果，跳过搜索
        - 若 web_search_enabled 且无 search_results：执行搜索后生成
        - 异常时回退到普通模式
        """
        prefetched = payload.search_results
        use_prefetched = prefetched is not None

        if use_prefetched:
            if len(prefetched.results or []) > 0:
                try:
                    return await self._generate_with_prefetched_research(payload)
                except Exception as exc:  # noqa: BLE001
                    print("prefetched_research failed, fallback to simple:", type(exc).__name__, repr(exc))
                    traceback.print_exc()
                    return await self._generate_simple(payload)
            return await self._generate_simple(payload)

        use_deep_research = bool(
            payload.user_config
            and isinstance(payload.user_config, dict)
            and payload.user_config.get("web_search_enabled")
        )
        if use_deep_research:
            try:
                return await self._generate_with_research(payload)
            except Exception as exc:  # noqa: BLE001
                print("deep_research failed, fallback to simple:", type(exc).__name__, repr(exc))
                traceback.print_exc()
                return await self._generate_simple(payload)
        return await self._generate_simple(payload)

    async def search_for_report(self, payload: SearchForReportRequest) -> dict:
        """仅执行检索，返回 query 与 results，供前端展示并确认。"""
        req = OpenReportRequest(
            task_type=payload.task_type,
            title=payload.title,
            outline=payload.outline,
            draft=payload.draft,
            materials=payload.materials,
            user_config=payload.user_config,
        )
        query = self._build_simple_query(req)
        print(f"[search-for-report] query={query!r}")

        results = await self._search_client.search(query, max_results=5)
        print(f"[search-for-report] results count={len(results)}")

        items = [
            SearchResultItem(title=r.title, snippet=r.snippet, url=r.url)
            for r in results
        ]
        return {"query": query, "results": items}

    # ====== 基础单轮生成 ======

    async def _generate_simple(self, payload: OpenReportRequest) -> str:
        base_url = self._settings.ai_base_url.rstrip("/")
        url = f"{base_url}/chat/completions"

        system_prompt = dedent(
            """
            你是一名专业的技术报告与工作报告写作助手，擅长根据给定材料与草稿，
            用规范、清晰、结构化的 Markdown 格式生成或润色“开放报告”类文档。

            要求：
            - 内容逻辑清晰、结构完整，标题层级合理（使用 #, ##, ### 等）
            - 语言正式、专业，但尽量通俗易懂
            - 尽量保留用户草稿中的关键信息与专业术语
            - 如有表格类结构，可使用 Markdown 表格语法
            """
        ).strip()

        parts: list[str] = []
        parts.append(f"任务类型: {payload.task_type}")
        if payload.title:
            parts.append(f"\n报告标题(可调整): {payload.title}")
        if payload.outline:
            parts.append(f"\n报告大纲(可参考):\n{payload.outline}")
        if payload.draft:
            parts.append(
                "\n当前草稿内容(需要在此基础上优化/续写):\n"
                f"{payload.draft}"
            )

        if payload.materials:
            parts.append("\n以下是若干参考材料的摘要，请在内容上尽量与之保持一致：")
            for idx, m in enumerate(payload.materials, start=1):
                snippet = (m.summary or m.text[:1200]).strip()
                parts.append(
                    f"\n[材料 {idx} - {m.name or m.file_id}]\n{snippet}"
                )

        if payload.user_config:
            parts.append(
                "\n写作偏好配置(语气/篇幅/侧重点等，可参考但不必逐字遵循):\n"
                f"{payload.user_config}"
            )

        user_message = "\n\n".join(parts)

        headers = {"Content-Type": "application/json"}
        if self._settings.ai_api_key:
            headers["Authorization"] = f"Bearer {self._settings.ai_api_key}"

        body = {
            "model": self._settings.ai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "top_p": 0.95,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()

        try:
            return data["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                f"Unexpected AI response format: {data}"
            ) from exc

    # ====== 深度检索版生成（简化：单次 DuckDuckGo 查询） ======

    def _build_simple_query(self, payload: OpenReportRequest) -> str:
        """从 payload 构建一个简单检索 query，不依赖 AI 规划。"""
        parts = []
        if payload.title and payload.title.strip():
            parts.append(payload.title.strip())
        if payload.user_config and isinstance(payload.user_config, dict):
            inst = str(payload.user_config.get("instruction") or "")
            if inst:
                parts.append(inst[:80])
        if not parts and payload.materials:
            first = payload.materials[0]
            snippet = (first.summary or first.text or "")[:80]
            if snippet:
                parts.append(snippet)
        return " ".join(parts).strip() or "智能报告 行业分析"

    async def _generate_with_prefetched_research(self, payload: OpenReportRequest) -> str:
        """使用前端预取的检索结果生成报告。"""
        pref = payload.search_results
        results = [SearchResult(r.title, r.snippet, r.url) for r in pref.results]
        research_bundles: list[Tuple[Dict[str, Any], List[SearchResult]]] = [
            ({"query": pref.query, "reason": "用户确认的检索结果"}, results)
        ]
        return await self._generate_report_with_research(payload, research_bundles)

    async def _generate_with_research(self, payload: OpenReportRequest) -> str:
        """单次检索：构建 query -> DuckDuckGo -> 综合写报告。"""
        query = self._build_simple_query(payload)
        print(f"[open-report] simple_search query={query!r}")

        results = await self._search_client.search(query, max_results=5)
        print(f"[open-report] search results count={len(results)}")

        if not results:
            print("[open-report] no search results, fallback to _generate_simple")
            return await self._generate_simple(payload)

        research_bundles: list[Tuple[Dict[str, Any], List[SearchResult]]] = [
            ({"query": query, "reason": "单次检索验证"}, results)
        ]
        return await self._generate_report_with_research(payload, research_bundles)

    async def _generate_report_with_research(
        self,
        payload: OpenReportRequest,
        research_bundles: List[Tuple[Dict[str, Any], List[SearchResult]]],
    ) -> str:
        """第二轮调用：综合搜索结果 + 原始材料，生成最终报告。"""
        base_url = self._settings.ai_base_url.rstrip("/")
        url = f"{base_url}/chat/completions"

        system_prompt = dedent(
            """
            你是一名专业的技术报告与工作报告写作助手，
            现在需要在综合“用户提供的材料”和“互联网检索结果”的基础上，
            生成一篇结构化的“开放报告”（Markdown 格式）。

            要求：
            - 报告结构完整，标题层级清晰（使用 #, ##, ### 等）
            - 语言正式、专业，但尽量通俗易懂
            - 明确区分“用户提供的材料信息”和“从外部检索获得的补充信息”
            - 当某个结论明显来自检索结果时，可以在句末用 [参考] 标注
            - 如有需要，可在文末添加“参考资料”小节，列出主要外部信息来源的标题或简要描述
            """
        ).strip()

        parts: list[str] = []
        parts.append(f"任务类型: {payload.task_type}")
        if payload.title:
            parts.append(f"\n报告标题(可调整): {payload.title}")
        if payload.outline:
            parts.append(f"\n用户提供的大纲(可参考):\n{payload.outline}")
        if payload.draft:
            parts.append(
                "\n用户提供的草稿(需要在此基础上优化/补充):\n"
                f"{payload.draft}"
            )

        if payload.materials:
            parts.append("\n以下是用户上传材料的摘要：")
            for idx, m in enumerate(payload.materials, start=1):
                snippet = (m.summary or m.text[:800]).strip()
                parts.append(
                    f"\n[材料 {idx} - {m.name or m.file_id}]\n{snippet}"
                )

        parts.append("\n下面是根据任务自动检索到的外部信息（已按检索任务分组）：")
        for i, (q, results) in enumerate(research_bundles, start=1):
            parts.append(
                f"\n=== 检索任务 {i} ===\n"
                f"查询语句: {q.get('query')}\n"
                f"目的: {q.get('reason') or '（未说明）'}\n"
                "主要检索结果摘要："
            )
            for j, res in enumerate(results, start=1):
                parts.append(
                    f"\n- 结果 {j}: {res.title}\n"
                    f"  摘要: {res.snippet}\n"
                    f"  链接: {res.url}"
                )

        if payload.user_config:
            parts.append(
                "\n用户的写作偏好(语气/篇幅/侧重点等，可适度参考):\n"
                f"{payload.user_config}"
            )

        user_message = "\n\n".join(parts)

        headers = {"Content-Type": "application/json"}
        if self._settings.ai_api_key:
            headers["Authorization"] = f"Bearer {self._settings.ai_api_key}"

        body = {
            "model": self._settings.ai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "top_p": 0.95,
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()

        try:
            return data["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                f"Unexpected AI response format (research stage): {data}"
            ) from exc

