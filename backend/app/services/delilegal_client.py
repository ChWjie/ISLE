"""
得理开放平台检索客户端
- 凭据仅从环境变量读取，不在源码中保留密钥
- 并发检索：类案 + 法规
- 结构化压缩：提取标题、摘要、条文片段
- 可追溯引用：生成 [Case-x] / [Law-x] 来源编号
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List

import httpx


class DeliLegalClient:
    """得理开放平台 API 客户端"""

    DEFAULT_BASE_URL = "https://openapi.delilegal.com"

    def __init__(self):
        self.base_url = os.getenv("DELILEGAL_BASE_URL", self.DEFAULT_BASE_URL)
        self.app_id = os.getenv("DELILEGAL_APP_ID", "").strip()
        self.secret = os.getenv("DELILEGAL_SECRET", "").strip()
        self.case_page_size = int(os.getenv("DELILEGAL_CASE_PAGE_SIZE", "5"))
        self.law_page_size = int(os.getenv("DELILEGAL_LAW_PAGE_SIZE", "5"))
        self.law_field_name = os.getenv("DELILEGAL_LAW_FIELD_NAME", "semantic")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=15.0,
            headers={
                "Content-Type": "application/json",
                "appid": self.app_id,
                "secret": self.secret,
            },
        )

    async def _safe_post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.app_id or not self.secret:
            return {"_error": "DeliLegal credentials are not configured", "_path": path}
        try:
            resp = await self.client.post(path, json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"_error": str(e), "_path": path}

    async def search_cases(self, query: str, page_size: int | None = None) -> Dict[str, Any]:
        payload = {
            "pageNo": 1,
            "pageSize": page_size or self.case_page_size,
            "sortField": "correlation",
            "sortOrder": "desc",
            "condition": {
                "keywordArr": [query],
                "longText": query,
            },
        }
        return await self._safe_post("/api/qa/v3/search/queryListCase", payload)

    async def search_laws(
        self,
        query: str,
        page_size: int | None = None,
        field_name: str | None = None,
    ) -> Dict[str, Any]:
        payload = {
            "pageNo": 1,
            "pageSize": page_size or self.law_page_size,
            "sortField": "correlation",
            "sortOrder": "desc",
            "condition": {
                "keywords": [query],
                "fieldName": field_name or self.law_field_name,
            },
        }
        return await self._safe_post("/api/qa/v3/search/queryListLaw", payload)

    @staticmethod
    def _pick_items(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not isinstance(raw, dict):
            return []
        if isinstance(raw.get("data"), list):
            return raw["data"]
        if isinstance(raw.get("data"), dict):
            data = raw["data"]
            for key in ("records", "list", "items", "result", "rows"):
                if isinstance(data.get(key), list):
                    return data[key]
        for key in ("records", "list", "items", "result", "rows"):
            if isinstance(raw.get(key), list):
                return raw[key]
        return []

    @staticmethod
    def _truncate_text(value: Any, limit: int = 180) -> str:
        text = str(value or "").strip().replace("\n", " ")
        return text[:limit]

    def _normalize_case(self, item: Dict[str, Any], idx: int) -> Dict[str, str]:
        title = (
            item.get("title")
            or item.get("caseName")
            or item.get("name")
            or item.get("case_title")
            or f"未命名案例{idx}"
        )
        summary = (
            item.get("reason")
            or item.get("summary")
            or item.get("abstract")
            or item.get("caseGist")
            or item.get("content")
            or ""
        )
        return {
            "id": f"Case-{idx}",
            "title": self._truncate_text(title, 80),
            "summary": self._truncate_text(summary, 180),
        }

    def _normalize_law(self, item: Dict[str, Any], idx: int) -> Dict[str, str]:
        title = (
            item.get("title")
            or item.get("lawName")
            or item.get("name")
            or item.get("regulationName")
            or f"未命名法规{idx}"
        )
        article = (
            item.get("article")
            or item.get("clause")
            or item.get("content")
            or item.get("summary")
            or ""
        )
        return {
            "id": f"Law-{idx}",
            "title": self._truncate_text(title, 80),
            "article": self._truncate_text(article, 220),
        }

    def _build_context(self, cases: List[Dict[str, str]], laws: List[Dict[str, str]], degraded_reason: str = "") -> str:
        lines: List[str] = []
        lines.append("## 得理检索增强上下文")

        if degraded_reason:
            lines.append(f"- 检索降级说明：{degraded_reason}")

        lines.append("\n### 类案（结构化）")
        if cases:
            for c in cases:
                lines.append(f"- [{c['id']}] {c['title']}")
                if c.get("summary"):
                    lines.append(f"  - 要点：{c['summary']}")
        else:
            lines.append("- 无有效类案结果")

        lines.append("\n### 法规（结构化）")
        if laws:
            for l in laws:
                lines.append(f"- [{l['id']}] {l['title']}")
                if l.get("article"):
                    lines.append(f"  - 条文片段：{l['article']}")
        else:
            lines.append("- 无有效法规结果")

        lines.append("\n### 引用规则")
        lines.append("- 在输出论证中优先引用以上来源编号，如 [Case-1]、[Law-2]。")
        lines.append("- 不得虚构未出现的来源编号。")

        return "\n".join(lines)

    async def retrieve_pack(
        self,
        query: str,
        use_case: bool = True,
        use_law: bool = True,
        timeout_sec: float = 12.0,
    ) -> Dict[str, Any]:
        """并发检索并返回结构化结果包"""
        case_task = asyncio.create_task(self.search_cases(query)) if use_case else None
        law_task = asyncio.create_task(self.search_laws(query)) if use_law else None

        case_raw: Dict[str, Any] = {}
        law_raw: Dict[str, Any] = {}
        degraded_reason = ""

        try:
            tasks = [t for t in [case_task, law_task] if t is not None]
            if tasks:
                await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout_sec)
        except Exception as e:
            degraded_reason = f"并发检索超时或失败：{e}"

        if case_task:
            if case_task.done() and not case_task.cancelled():
                try:
                    case_raw = case_task.result()
                except Exception as e:
                    degraded_reason = degraded_reason or f"类案检索失败：{e}"
            else:
                case_task.cancel()

        if law_task:
            if law_task.done() and not law_task.cancelled():
                try:
                    law_raw = law_task.result()
                except Exception as e:
                    degraded_reason = degraded_reason or f"法规检索失败：{e}"
            else:
                law_task.cancel()

        case_items = self._pick_items(case_raw)
        law_items = self._pick_items(law_raw)

        # 结构化压缩 TopN
        cases = [self._normalize_case(it, i + 1) for i, it in enumerate(case_items[:5])]
        laws = [self._normalize_law(it, i + 1) for i, it in enumerate(law_items[:5])]

        # API返回错误信息补充
        if not degraded_reason:
            if isinstance(case_raw, dict) and case_raw.get("_error"):
                degraded_reason = f"类案检索失败：{case_raw.get('_error')}"
            if isinstance(law_raw, dict) and law_raw.get("_error"):
                degraded_reason = (degraded_reason + "；" if degraded_reason else "") + f"法规检索失败：{law_raw.get('_error')}"

        source_map = [f"[{c['id']}] {c['title']}" for c in cases] + [f"[{l['id']}] {l['title']}" for l in laws]
        context = self._build_context(cases, laws, degraded_reason)

        return {
            "query": query,
            "cases": cases,
            "laws": laws,
            "source_map": source_map,
            "degraded": bool(degraded_reason),
            "degraded_reason": degraded_reason,
            "retrieval_context": context,
        }

    async def build_search_context(self, query: str) -> str:
        """兼容旧调用：仅返回上下文字符串"""
        pack = await self.retrieve_pack(query)
        return pack.get("retrieval_context", "")

    async def close(self):
        await self.client.aclose()


_delilegal_client: DeliLegalClient | None = None


def get_delilegal_client() -> DeliLegalClient:
    global _delilegal_client
    if _delilegal_client is None:
        _delilegal_client = DeliLegalClient()
    return _delilegal_client
