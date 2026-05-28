from __future__ import annotations

import httpx

from atlas_api.models.sources import SourceCardIn
from atlas_api.sources.base import SourceClient


class OpenAlexClient(SourceClient):
    async def search(self, query: str, limit: int = 5) -> list[SourceCardIn]:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get("https://api.openalex.org/works", params={"search": query, "per-page": min(limit, 10)})
            response.raise_for_status()
            data = response.json()
        results = []
        for item in data.get("results", [])[:limit]:
            authors = [
                auth.get("author", {}).get("display_name")
                for auth in item.get("authorships", [])[:6]
                if auth.get("author", {}).get("display_name")
            ]
            results.append(
                SourceCardIn(
                    title=item.get("title") or "Untitled OpenAlex work",
                    url=item.get("primary_location", {}).get("landing_page_url") or item.get("doi"),
                    doi=(item.get("doi") or "").replace("https://doi.org/", "") or None,
                    source_type="openalex",
                    year=item.get("publication_year"),
                    authors=authors,
                    venue=(item.get("primary_location", {}).get("source") or {}).get("display_name"),
                    abstract=_abstract_from_inverted_index(item.get("abstract_inverted_index")),
                    relevance_score=0.65,
                    credibility_score=0.55,
                    freshness_score=0.5,
                    metadata={"openalex_id": item.get("id")},
                )
            )
        return results


def _abstract_from_inverted_index(index: dict | None) -> str | None:
    if not index:
        return None
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        for pos in positions:
            words.append((pos, word))
    return " ".join(word for _, word in sorted(words))[:1200]

