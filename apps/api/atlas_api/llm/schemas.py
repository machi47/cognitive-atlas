from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_schema(name: str) -> dict[str, Any]:
    path = Path(__file__).resolve().parents[4] / "schemas" / f"{name}.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))
