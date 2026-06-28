from __future__ import annotations

from html import unescape
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import httpx

from app.config.settings import Settings, get_settings
from app.models import EvidenceSource, ToolResult


class SearchClient:
    """Search adapter using Tavily when configured and DuckDuckGo HTML as a fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def web_search(self, query: str, max_results: int | None = None) -> ToolResult:
        limit = max_results or self.settings.max_search_results
        if self.settings.tavily_api_key:
            return await self._tavily_search(query, limit)
        return await self._duckduckgo_search(query, limit)

    async def academic_search(self, query: str, max_results: int | None = None) -> ToolResult:
        academic_query = f"{query} site:pubmed.ncbi.nlm.nih.gov OR site:scholar.google.com OR site:arxiv.org"
        return await self.web_search(academic_query, max_results)

    async def traceback_search(self, claim: str, max_results: int | None = None) -> ToolResult:
        limit = max_results or self.settings.max_search_results
        shortened = " ".join(claim.split()[:8])
        core_terms = " ".join(word for word in claim.split()[:5] if len(word) > 3)
        queries = [
            f'"{claim}"',
            f'"{shortened}"',
            f'{core_terms} origin',
            f'{core_terms} fact check',
            f'{core_terms} myth',
        ]
        all_results: list[dict[str, str | None]] = []
        errors: list[str] = []
        seen_urls: set[str] = set()
        for query in queries:
            result = await self.web_search(query, max(2, limit // 2))
            if not result.success:
                if result.error:
                    errors.append(result.error)
                continue
            if isinstance(result.data, list):
                for item in result.data:
                    url = str(item.get("url") or "")
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    item["trace_query"] = query
                    all_results.append(item)
                    if len(all_results) >= limit:
                        break
            if len(all_results) >= limit:
                break
        return ToolResult(
            success=bool(all_results),
            tool="traceback_search",
            query=" | ".join(queries),
            data=all_results,
            error=None if all_results else "; ".join(errors) or "No TraceBack candidates returned.",
        )

    async def _tavily_search(self, query: str, limit: int) -> ToolResult:
        try:
            async with httpx.AsyncClient(timeout=self.settings.search_timeout_seconds) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.settings.tavily_api_key,
                        "query": query,
                        "max_results": limit,
                        "search_depth": "advanced",
                        "include_answer": False,
                    },
                )
                response.raise_for_status()
            payload = response.json()
            results = [
                {
                    "title": item.get("title") or "Untitled source",
                    "url": item.get("url") or "",
                    "snippet": item.get("content") or "",
                    "published_date": item.get("published_date"),
                }
                for item in payload.get("results", [])
                if item.get("url")
            ]
            return ToolResult(success=True, tool="web_search", query=query, data=results)
        except Exception as exc:  # noqa: BLE001
            return ToolResult(success=False, tool="web_search", query=query, data=[], error=str(exc))

    async def _duckduckgo_search(self, query: str, limit: int) -> ToolResult:
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.search_timeout_seconds,
                headers={"User-Agent": "ProofPathAI/0.1 evidence verification"},
                follow_redirects=True,
            ) as client:
                response = await client.get(f"https://duckduckgo.com/html/?q={quote_plus(query)}")
                response.raise_for_status()
            results = self._parse_duckduckgo_html(response.text, limit)
            return ToolResult(success=True, tool="web_search", query=query, data=results)
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                success=False,
                tool="web_search",
                query=query,
                data=[],
                error=(
                    "Search failed. Configure TAVILY_API_KEY or enable network access for live evidence "
                    f"retrieval. Details: {exc}"
                ),
            )

    def _parse_duckduckgo_html(self, html: str, limit: int) -> list[dict[str, str | None]]:
        results: list[dict[str, str | None]] = []
        blocks = html.split('class="result__a"')
        for block in blocks[1:]:
            if len(results) >= limit:
                break
            href_marker = 'href="'
            href_start = block.find(href_marker)
            if href_start == -1:
                continue
            href_start += len(href_marker)
            href_end = block.find('"', href_start)
            title_start = block.find(">", href_end) + 1
            title_end = block.find("</a>", title_start)
            snippet_marker = 'class="result__snippet"'
            snippet = ""
            snippet_pos = block.find(snippet_marker)
            if snippet_pos != -1:
                snippet_start = block.find(">", snippet_pos) + 1
                snippet_end = block.find("</a>", snippet_start)
                if snippet_end == -1:
                    snippet_end = block.find("</", snippet_start)
                snippet = self._strip_tags(block[snippet_start:snippet_end])
            url = self._clean_result_url(unescape(block[href_start:href_end]))
            title = self._strip_tags(block[title_start:title_end])
            if title and url:
                results.append(
                    {
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "published_date": None,
                    }
                )
        return results

    def _strip_tags(self, value: str) -> str:
        cleaned = ""
        inside_tag = False
        for character in value:
            if character == "<":
                inside_tag = True
            elif character == ">":
                inside_tag = False
            elif not inside_tag:
                cleaned += character
        return " ".join(unescape(cleaned).split())

    def _clean_result_url(self, url: str) -> str:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if "uddg" in query and query["uddg"]:
            return unquote(query["uddg"][0])
        return url


def sources_from_tool_result(result: ToolResult) -> list[EvidenceSource]:
    if not result.success or not isinstance(result.data, list):
        return []
    sources: list[EvidenceSource] = []
    seen_urls: set[str] = set()
    for item in result.data:
        url = str(item.get("url") or "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        sources.append(
            EvidenceSource(
                title=str(item.get("title") or "Untitled source"),
                url=url,
                snippet=str(item.get("snippet") or ""),
                published_date=item.get("published_date"),
            )
        )
    return sources
