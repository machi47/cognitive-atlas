from __future__ import annotations

from abc import ABC, abstractmethod

from atlas_api.models.sources import SourceCardIn


class SourceClient(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> list[SourceCardIn]:
        raise NotImplementedError

