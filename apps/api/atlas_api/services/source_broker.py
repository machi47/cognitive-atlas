from __future__ import annotations

from atlas_api.db.repositories import Repository
from atlas_api.models.sources import SourceCardIn
from atlas_api.sources.arxiv import ArxivClient
from atlas_api.sources.crossref import CrossrefClient
from atlas_api.sources.dedupe import dedupe_sources
from atlas_api.sources.openalex import OpenAlexClient


class SourceBroker:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.clients = {
            "openalex": OpenAlexClient(),
            "crossref": CrossrefClient(),
            "arxiv": ArxivClient(),
        }

    async def search_and_store(self, workspace_id: str, query: str, source_types: list[str], limit: int = 5) -> list[dict]:
        candidates: list[SourceCardIn] = []
        for source_type in source_types:
            client = self.clients.get(source_type)
            if not client:
                continue
            try:
                candidates.extend(await client.search(query, limit=limit))
            except Exception:
                continue
        stored = []
        for source in dedupe_sources(candidates)[:limit]:
            stored.append((await self.repo.create_source(workspace_id, source)).model_dump())
        return stored

