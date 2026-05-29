from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from atlas_api.config import get_settings
from atlas_api.db.repositories import Repository
from atlas_api.llm.base import LlmAdapter
from atlas_api.main import app
from atlas_api.models.llm import LlmHealth, LlmJsonRequest, LlmJsonResult, LlmTextRequest, LlmTextResult


CHAT_A = "I want to learn everything I'd need to know to build substrateCAD from first principles."
CHAT_B = "PCB trace impedance feels related to SoC interconnects and package substrates because it is all physical signal integrity."
CHAT_C = "I'm interested in analog compute and compute-in-memory, but I'm worried ADC/DAC overhead kills the benefit."


def test_minimum_cross_session_learning_loop_proof(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ATLAS_LLM_PROVIDER", "codex")
    monkeypatch.setenv("ATLAS_ALLOW_FAKE_FOR_TESTS", "false")
    get_settings.cache_clear()

    with TestClient(app) as client:
        client.app.state.llm_adapter = ContractFixtureLlmAdapter()
        sessions = [
            _create_chat(client, "Chat A"),
            _create_chat(client, "Chat B"),
            _create_chat(client, "Chat C"),
        ]
        responses = [
            _post_turn(client, sessions[0]["id"], CHAT_A),
            _post_turn(client, sessions[1]["id"], CHAT_B),
            _post_turn(client, sessions[2]["id"], CHAT_C),
        ]

        for response in responses:
            assert response["processing_state"]["status"] == "succeeded"
            assert response["assistant_turn"] is not None
            assert response["model_error"] is None
            assert response["artifacts_summary"]["artifact_ids"], "learning artifacts must be persisted"
            assert response["artifacts_summary"]["patch_ids"], "structure update failed: patch_ids is empty"
            assert response["artifacts_summary"]["map_ids"], "structure update failed: map_ids is empty"

        repo = Repository(client.app.state.db)
        workspace_id = asyncio.run(repo.ensure_default_workspace())
        db = DbEvidence(repo, workspace_id)

        assert len(asyncio.run(repo.list_sessions(workspace_id, include_archived=True))) == 3
        for session, prompt in zip(sessions, [CHAT_A, CHAT_B, CHAT_C], strict=True):
            turns = asyncio.run(repo.list_turns(session["id"]))
            assert [turn.role for turn in turns] == ["user", "assistant"]
            assert turns[0].content == prompt
            other_prompts = {CHAT_A, CHAT_B, CHAT_C} - {prompt}
            assert all(other not in turns[1].content for other in other_prompts), "chat response leaked another chat transcript"

        map_titles = {title.lower() for title in asyncio.run(db.map_titles())}
        assert any("substratecad" in title or "fabrication-aware cad" in title for title in map_titles)
        assert any("physical signal integrity" in title or "interconnect" in title for title in map_titles)
        assert any("analog compute" in title or "compute-in-memory" in title for title in map_titles)
        assert not any(_garbage_title(title) for title in map_titles)

        labels = asyncio.run(db.concept_labels())
        _assert_has(labels, "substratecad")
        _assert_has(labels, "geometry kernel", "geometry/cad kernel")
        _assert_has(labels, "substrate object model", "layers/features/vias/traces/materials")
        _assert_has(labels, "fabrication/process constraints", "fabrication process constraints")
        _assert_has(labels, "electrical/physical constraints")
        _assert_has(labels, "pcb trace impedance")
        _assert_has(labels, "soc interconnects", "package substrate interconnect")
        _assert_has(labels, "analog compute")
        _assert_has(labels, "compute-in-memory")
        _assert_has(labels, "adc/dac overhead")

        edges = asyncio.run(db.edges())
        assert _edge_exists(edges, "fabrication/process constraints", "substratecad", "constrains")
        assert _edge_exists(edges, "pcb trace impedance", "physical signal integrity", "instance_of")
        assert _edge_exists(edges, "package substrate interconnect", "physical signal integrity", "instance_of")
        assert _edge_exists(edges, "adc/dac overhead", "analog compute", "constrains")
        assert _edge_exists(edges, "adc/dac overhead", "compute-in-memory", "constrains")

        questions = asyncio.run(db.questions())
        question_text = "\n".join(question["question"].lower() for question in questions)
        assert "does substrate mean pcb" in question_text or "what kind of substrate" in question_text
        assert "conversion overhead erase" in question_text or "adc/dac" in question_text
        assert "pcb controlled impedance" in question_text or "physical constraints transfer" in question_text

        bridges = asyncio.run(db.bridges())
        bridge_text = "\n".join(f"{bridge['from_label']} {bridge['to_label']} {bridge['reason']}".lower() for bridge in bridges)
        for term in ["pcb trace impedance", "package substrate", "soc physical", "physical signal integrity"]:
            assert term in bridge_text

        for table in ["concept_nodes", "relation_edges", "claims", "open_questions"]:
            rows = asyncio.run(db.rows_with_provenance(table))
            assert rows, f"{table} should have rows"
            for row in rows:
                provenance = row["provenance"]
                assert provenance, f"{table} row lacks provenance: {row}"
                assert all(item.get("session_id") and item.get("turn_id") for item in provenance)

        statuses = asyncio.run(db.statuses())
        assert "user_asserted" in statuses or "user_stated" in statuses
        assert "assistant_inferred" in statuses
        assert "speculative" in statuses
        source_needs = asyncio.run(repo.list_research_tasks(workspace_id))
        assert source_needs
        assert "source_needed" in {task["status"] for task in source_needs}

        bad_claims = asyncio.run(db.source_backed_claims_without_sources())
        assert not bad_claims

        overview = client.get("/api/learn/overview").json()
        assert overview["current_frame"]["project"].startswith("Build substrateCAD")
        assert overview["concepts"]
        assert overview["bridges"]
        assert overview["tensions"]
        assert overview["source_needs"]
        assert any(concept["contributors"] for concept in overview["concepts"])

        textbook = client.get("/api/learn/textbook").json()
        rendered = "\n".join(section["body"] + "\n" + "\n".join(section["bullets"]) for section in textbook["sections"])
        assert "fabrication-aware CAD" in rendered
        assert "conversion/control overhead" in rendered
        assert "Analog computing is a type of computing" not in rendered

        for query in ["substrateCAD", "ADC", "physical signal integrity"]:
            results = client.get("/api/search", params={"q": query}).json()
            assert any(results[group] for group in ["chats", "turns", "concepts", "questions", "bridges"])


def _create_chat(client: TestClient, title: str) -> dict[str, Any]:
    response = client.post("/api/sessions", json={"title": title})
    assert response.status_code == 200
    return response.json()


def _post_turn(client: TestClient, session_id: str, content: str) -> dict[str, Any]:
    response = client.post(f"/api/sessions/{session_id}/turns", json={"content": content})
    assert response.status_code == 200, response.text
    return response.json()


def _assert_has(labels: set[str], *candidates: str) -> None:
    assert any(candidate.lower() in labels for candidate in candidates), f"missing one of {candidates}; got {sorted(labels)}"


def _edge_exists(edges: list[dict[str, Any]], from_label: str, to_label: str, relation_type: str) -> bool:
    return any(
        edge["from_label"].lower() == from_label.lower()
        and edge["to_label"].lower() == to_label.lower()
        and edge["relation_type"] == relation_type
        for edge in edges
    )


def _garbage_title(title: str) -> bool:
    garbage = ["extract exchange only", "current user message", "recent dialogue", "discussion reply", "post-turn extraction"]
    return any(item in title for item in garbage)


class DbEvidence:
    def __init__(self, repo: Repository, workspace_id: str):
        self.repo = repo
        self.workspace_id = workspace_id

    async def map_titles(self) -> list[str]:
        rows = await self.repo.db.fetchall("select title from topic_maps where workspace_id = ?", (self.workspace_id,))
        return [row["title"] for row in rows]

    async def concept_labels(self) -> set[str]:
        rows = await self.repo.db.fetchall("select label from concept_nodes where workspace_id = ?", (self.workspace_id,))
        return {row["label"].lower() for row in rows}

    async def edges(self) -> list[dict[str, Any]]:
        return await self.repo.db.fetchall(
            """
            select e.*, nf.label as from_label, nt.label as to_label
            from relation_edges e
            join concept_nodes nf on nf.id = e.from_node_id
            join concept_nodes nt on nt.id = e.to_node_id
            where e.workspace_id = ?
            """,
            (self.workspace_id,),
        )

    async def questions(self) -> list[dict[str, Any]]:
        return await self.repo.db.fetchall("select * from open_questions where workspace_id = ?", (self.workspace_id,))

    async def bridges(self) -> list[dict[str, Any]]:
        return await self.repo.db.fetchall(
            """
            select b.*, nf.label as from_label, nt.label as to_label
            from latent_bridges b
            join concept_nodes nf on nf.id = b.from_node_id
            join concept_nodes nt on nt.id = b.to_node_id
            where b.workspace_id = ?
            """,
            (self.workspace_id,),
        )

    async def rows_with_provenance(self, table: str) -> list[dict[str, Any]]:
        rows = await self.repo.db.fetchall(f"select id, provenance_json from {table} where workspace_id = ?", (self.workspace_id,))
        return [{"id": row["id"], "provenance": _loads(row["provenance_json"])} for row in rows]

    async def statuses(self) -> set[str]:
        rows = []
        for table in ["concept_nodes", "relation_edges", "claims"]:
            rows.extend(await self.repo.db.fetchall(f"select epistemic_status from {table} where workspace_id = ?", (self.workspace_id,)))
        return {row["epistemic_status"] for row in rows}

    async def source_backed_claims_without_sources(self) -> list[dict[str, Any]]:
        return await self.repo.db.fetchall(
            "select * from claims where workspace_id = ? and epistemic_status = 'source_backed' and source_ids_json = '[]'",
            (self.workspace_id,),
        )


def _loads(value: str) -> list[dict[str, Any]]:
    import json

    parsed = json.loads(value)
    return parsed if isinstance(parsed, list) else []


class ContractFixtureLlmAdapter(LlmAdapter):
    provider_name = "contract_fixture"
    supports_web_search = False
    supports_schema_output = True

    async def complete_text(self, request: LlmTextRequest) -> LlmTextResult:
        return LlmTextResult(text=self._reply(request.prompt), provider_name=self.provider_name)

    async def complete_json(self, request: LlmJsonRequest, schema: dict[str, Any] | None = None) -> LlmJsonResult:
        if request.task == "discussion_reply":
            data = {"message": self._reply(request.prompt), "response_mode": "discuss", "source_ids_used": [], "suggested_followups": [], "uncertainty_notes": [], "should_research_more": False}
        elif request.task == "post_turn_extraction":
            data = {"topics": [], "claims": [], "node_candidates": [], "edge_candidates": [], "open_questions": [], "tensions": [], "analogies": [], "latent_bridges": [], "source_needs": [], "forbidden_user_state_claims": [], "notes": "Contract fixture leaves structured extraction to deterministic technical extractor."}
        else:
            data = {}
        return LlmJsonResult(data=data, provider_name=self.provider_name)

    async def healthcheck(self) -> LlmHealth:
        return LlmHealth(provider_name=self.provider_name, available=True, message="contract fixture")

    def _reply(self, prompt: str) -> str:
        message = prompt.split("Current user message:", 1)[-1].strip().lower()
        if "substratecad" in message:
            return "For substrateCAD from first principles, first clarify whether substrate means PCB, IC/package substrate, or a broader fabrication-aware CAD system. The foundation stack is geometry/CAD kernel, substrate object model, materials/layers/vias/features, fabrication/process constraints, electrical/physical constraints, simulation/verification, and manufacturability rules."
        if "pcb trace impedance" in message:
            return "That relation is plausible but tentative: PCB trace impedance, package substrate interconnect, and SoC interconnect all involve physical signal integrity through constrained geometry and material stacks. The bridge should stay suggested until sources and sharper constraints validate where the analogy holds or breaks."
        if "analog compute" in message or "compute-in-memory" in message:
            return "The central tension is system-level overhead. Analog compute or compute-in-memory can make local MAC-like work cheap, but ADC/DAC conversion, control, precision, noise, and calibration overhead can erase the benefit."
        return "I will keep the response compact and preserve the learning structure in the background."
