#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

DATA_DIR="${REAL_CODEX_PROBE_DATA_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/cognitive-atlas-real-codex.XXXXXX")}"
export ATLAS_DATA_DIR="$DATA_DIR"
export ATLAS_LLM_PROVIDER=codex
export ATLAS_ALLOW_FAKE_FOR_TESTS=false
export ATLAS_CODEX_TIMEOUT_SECONDS="${ATLAS_CODEX_TIMEOUT_SECONDS:-240}"

python - <<'PY'
from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from fastapi.testclient import TestClient

from atlas_api.config import get_settings
from atlas_api.db.repositories import Repository
from atlas_api.main import app

PROMPT = "I want to learn everything I'd need to know to build substrateCAD from first principles."
GARBAGE_TITLES = {"extract exchange only", "current user message", "recent dialogue", "discussion reply", "post-turn extraction"}


def main() -> None:
    get_settings.cache_clear()
    with TestClient(app) as client:
        provider = client.get("/api/health").json()["provider"]
        assert provider["provider_name"] == "codex", provider
        assert provider["available"] is True, provider

        session_response = client.post("/api/sessions", json={"title": "Real Codex substrateCAD probe"})
        assert session_response.status_code == 200, session_response.text
        session = session_response.json()

        turn_response = client.post(f"/api/sessions/{session['id']}/turns", json={"content": PROMPT})
        assert turn_response.status_code == 200, turn_response.text
        turn = turn_response.json()

        assert turn["session"]["id"] == session["id"]
        assert turn["user_turn"]["content"] == PROMPT
        assert turn["assistant_turn"] is not None, turn
        assert turn["model_error"] is None, turn.get("model_error")
        assert turn["processing_state"]["message"] != "structure update failed", turn["processing_state"]
        assert turn["artifacts_summary"]["artifact_ids"], "artifact_ids is empty"
        assert turn["artifacts_summary"]["patch_ids"], "patch_ids is empty"
        assert turn["artifacts_summary"]["map_ids"], "map_ids is empty"

        repo = Repository(client.app.state.db)
        workspace_id = asyncio.run(repo.ensure_default_workspace())
        evidence = asyncio.run(collect_evidence(repo, workspace_id, session["id"]))
        assert not evidence["failed_artifacts"], evidence["failed_artifacts"]

        titles = {title.lower() for title in evidence["map_titles"]}
        assert any("substratecad" in title or "fabrication-aware cad" in title for title in titles), evidence["map_titles"]
        assert not titles.intersection(GARBAGE_TITLES), evidence["map_titles"]

        labels = {label.lower() for label in evidence["concept_labels"]}
        assert "substratecad" in labels, evidence["concept_labels"]
        assert "geometry kernel" in labels or "geometry/cad kernel" in labels, evidence["concept_labels"]
        assert "fabrication/process constraints" in labels or "fabrication process constraints" in labels, evidence["concept_labels"]
        assert evidence["open_questions"], "open_questions is empty"
        assert not evidence["source_backed_claims_without_sources"], evidence["source_backed_claims_without_sources"]

        overview = client.get("/api/learn/overview").json()
        assert overview["concepts"], "Learn overview has no concepts"
        assert overview["current_frame"]["project"], "Learn overview has no current project frame"

        print(json.dumps({
            "status": "passed",
            "data_dir": os.environ["ATLAS_DATA_DIR"],
            "provider": provider,
            "turn": {
                "session_id": session["id"],
                "user_turn_id": turn["user_turn"]["id"],
                "assistant_turn_id": turn["assistant_turn"]["id"],
                "processing_message": turn["processing_state"]["message"],
                "artifact_ids": turn["artifacts_summary"]["artifact_ids"],
                "patch_ids": turn["artifacts_summary"]["patch_ids"],
                "map_ids": turn["artifacts_summary"]["map_ids"],
            },
            "db": evidence,
            "learn_current_frame": overview["current_frame"],
        }, indent=2))


async def collect_evidence(repo: Repository, workspace_id: str, session_id: str) -> dict[str, Any]:
    map_rows = await repo.db.fetchall("select title from topic_maps where workspace_id = ? order by title", (workspace_id,))
    concept_rows = await repo.db.fetchall("select label from concept_nodes where workspace_id = ? order by label", (workspace_id,))
    question_rows = await repo.db.fetchall("select question from open_questions where workspace_id = ? order by question", (workspace_id,))
    bad_claims = await repo.db.fetchall(
        "select id, text from claims where workspace_id = ? and epistemic_status = 'source_backed' and source_ids_json = '[]'",
        (workspace_id,),
    )
    failed_artifacts = await repo.db.fetchall(
        """
        select artifact_type, status, title, content_json, metadata_json
        from artifacts
        where workspace_id = ? and status = 'failed'
        order by created_at
        """,
        (workspace_id,),
    )
    turns = await repo.list_turns(session_id)
    return {
        "session_turn_roles": [turn.role for turn in turns],
        "map_titles": [row["title"] for row in map_rows],
        "concept_labels": [row["label"] for row in concept_rows],
        "open_questions": [row["question"] for row in question_rows],
        "source_backed_claims_without_sources": bad_claims,
        "failed_artifacts": failed_artifacts,
    }


if __name__ == "__main__":
    main()
PY
