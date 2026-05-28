from __future__ import annotations

from atlas_api.models.sources import SourceCardIn


def manual_source_card(**kwargs) -> SourceCardIn:
    return SourceCardIn(**kwargs)

