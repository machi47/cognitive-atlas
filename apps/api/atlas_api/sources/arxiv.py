from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import httpx

from atlas_api.models.sources import SourceCardIn
from atlas_api.sources.base import SourceClient


class ArxivClient(SourceClient):
    async def search(self, query: str, limit: int = 5) -> list[SourceCardIn]:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(
                "https://export.arxiv.org/api/query",
                params={"search_query": f"all:{query}", "start": 0, "max_results": min(limit, 10)},
            )
            response.raise_for_status()
        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        results = []
        for entry in root.findall("atom:entry", ns)[:limit]:
            title = _text(entry.find("atom:title", ns)) or "Untitled arXiv paper"
            url = _text(entry.find("atom:id", ns))
            arxiv_id = url.rstrip("/").split("/")[-1] if url else None
            published = _text(entry.find("atom:published", ns))
            year = int(published[:4]) if published and re.match(r"\d{4}", published) else None
            authors = [_text(author.find("atom:name", ns)) for author in entry.findall("atom:author", ns)]
            results.append(
                SourceCardIn(
                    title=" ".join(title.split()),
                    url=url,
                    arxiv_id=arxiv_id,
                    source_type="arxiv",
                    year=year,
                    authors=[author for author in authors if author],
                    venue="arXiv",
                    abstract=" ".join((_text(entry.find("atom:summary", ns)) or "").split())[:1200],
                    relevance_score=0.58,
                    credibility_score=0.45,
                    freshness_score=0.65,
                    metadata={"published": published},
                )
            )
        return results


def _text(element: ET.Element | None) -> str | None:
    return element.text.strip() if element is not None and element.text else None

