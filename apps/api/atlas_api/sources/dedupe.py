from __future__ import annotations

import re

from atlas_api.models.sources import SourceCardIn


def dedupe_sources(sources: list[SourceCardIn]) -> list[SourceCardIn]:
    seen: set[str] = set()
    output: list[SourceCardIn] = []
    for source in sources:
        key = source.doi or source.arxiv_id or _title_key(source.title)
        if key in seen:
            continue
        seen.add(key)
        output.append(source)
    return output


def _title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()

