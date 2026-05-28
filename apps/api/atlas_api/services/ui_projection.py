from __future__ import annotations

from atlas_api.db.repositories import Repository
from atlas_api.models.atlas import AtlasTree


class UiProjectionService:
    def __init__(self, repo: Repository):
        self.repo = repo

    async def atlas_tree(self, workspace_id: str) -> AtlasTree:
        return await self.repo.atlas_tree(workspace_id)

