from __future__ import annotations

import httpx

from atlas_api.models.sources import SourceCardIn
from atlas_api.sources.base import SourceClient


class CrossrefClient(SourceClient):
    async def search(self, query: str, limit: int = 5) -> list[SourceCardIn]:
        async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "cognitive-atlas/0.1"}) as client:
            response = await client.get("https://api.crossref.org/works", params={"query": query, "rows": min(limit, 10)})
            response.raise_for_status()
            data = response.json()
        results = []
        for item in data.get("message", {}).get("items", [])[:limit]:
            authors = [
                " ".join(part for part in [author.get("given"), author.get("family")] if part)
                for author in item.get("author", [])[:6]
            ]
            year_parts = item.get("published-print", item.get("published-online", {})).get("date-parts", [[None]])
            title = (item.get("title") or ["Untitled Crossref work"])[0]
            results.append(
                SourceCardIn(
                    title=title,
                    url=item.get("URL"),
                    doi=item.get("DOI"),
                    source_type="crossref",
                    year=year_parts[0][0],
                    authors=[author for author in authors if author],
                    venue=(item.get("container-title") or [None])[0],
                    abstract=_strip_jats(item.get("abstract")),
                    relevance_score=0.55,
                    credibility_score=0.55,
                    freshness_score=0.45,
                    metadata={"crossref_type": item.get("type")},
                )
            )
        return results


def _strip_jats(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace("<jats:p>", "").replace("</jats:p>", "")[:1200]

