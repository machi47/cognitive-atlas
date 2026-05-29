import pytest

from atlas_api.db.connection import Database
from atlas_api.db.migrations import run_migrations
from atlas_api.db.repositories import Repository
from atlas_api.errors import LlmUnavailableError
from atlas_api.llm.base import LlmAdapter
from atlas_api.llm.fake_adapter import FakeLlmAdapter
from atlas_api.models.llm import LlmHealth, LlmJsonRequest, LlmJsonResult, LlmTextRequest, LlmTextResult
from atlas_api.models.patches import NodeCandidate, PostTurnExtraction
from atlas_api.models.turns import TurnCreate
from atlas_api.services.learning_projection import LearningProjectionService, TextbookProjectionService
from atlas_api.services.context_broker import ContextBroker
from atlas_api.services.map_patch_builder import MapPatchBuilder
from atlas_api.workers.pipeline import TurnPipeline


async def _repo(tmp_path):
    db = Database(tmp_path / "atlas.db")
    await run_migrations(db)
    repo = Repository(db)
    workspace_id = await repo.ensure_default_workspace()
    return repo, workspace_id


@pytest.mark.asyncio
async def test_four_chat_demo_accumulates_global_learning_without_merging_chats(tmp_path):
    repo, workspace_id = await _repo(tmp_path)
    pipeline = TurnPipeline(repo, FakeLlmAdapter())
    prompts = [
        "I want to learn everything I'd need to know to build substrateCAD from first principles.",
        "PCB trace impedance feels related to SoC interconnects and package substrates because it is all physical signal integrity.",
        "SoC interconnects and package substrates seem like constrained physical communication through manufacturable layered media.",
        "I'm interested in analog compute and compute-in-memory, but I'm worried ADC/DAC overhead kills the benefit.",
    ]
    sessions = []
    for index, prompt in enumerate(prompts, start=1):
        session = await repo.create_session(workspace_id, f"Chat {index}")
        sessions.append(session)
        response = await pipeline.process_turn(workspace_id, session.id, TurnCreate(content=prompt))
        assert response.assistant_turn is not None
        assert response.artifacts_summary.artifact_ids
        assert response.artifacts_summary.patch_ids

    overview = await LearningProjectionService(repo).overview(workspace_id)
    labels = {concept["label"] for concept in overview["concepts"]}
    assert "substrateCAD" in labels
    assert "geometry kernel" in labels
    assert "fabrication/process constraints" in labels
    assert "PCB trace impedance" in labels
    assert "package substrate interconnect" in labels
    assert "SoC interconnects" in labels
    assert "physical signal integrity" in labels
    assert "analog compute" in labels
    assert "compute-in-memory" in labels
    assert "ADC/DAC overhead" in labels
    assert overview["project_goals"][0]["label"] == "substrateCAD"
    assert overview["current_frame"]["project"].startswith("Build substrateCAD")
    assert {"geometry kernel", "fabrication/process constraints"}.issubset(set(overview["current_frame"]["foundation_stack"]))
    assert any("conversion overhead" in tension["description"].lower() for tension in overview["tensions"])
    assert any("conversion overhead erase" in question["question"].lower() for question in overview["open_questions"])
    assert overview["source_needs"]

    bridge_text = "\n".join(f"{bridge['from_label']} -> {bridge['to_label']} {bridge['reason']}" for bridge in overview["bridges"])
    assert "PCB trace impedance -> SoC physical signaling constraints" in bridge_text
    assert "physical signal integrity -> substrateCAD" in bridge_text
    assert any(len(bridge["contributors"]) >= 1 for bridge in overview["bridges"])

    chat_turn_counts = [len(await repo.list_turns(session.id)) for session in sessions]
    assert chat_turn_counts == [2, 2, 2, 2]

    textbook = await TextbookProjectionService(repo).textbook(workspace_id)
    rendered = "\n".join([section["body"] + "\n" + "\n".join(section["bullets"]) for section in textbook["sections"]])
    assert "fabrication-aware CAD" in rendered
    assert "conversion/control overhead" in rendered
    assert "Analog computing is a type of computing" not in rendered

    search_substrate = await repo.search(workspace_id, "substrateCAD")
    assert search_substrate["chats"] or search_substrate["concepts"]
    search_adc = await repo.search(workspace_id, "ADC")
    assert search_adc["concepts"] or search_adc["questions"] or search_adc["bridges"]


@pytest.mark.asyncio
async def test_model_error_preserves_user_turn_without_assistant_turn(tmp_path):
    repo, workspace_id = await _repo(tmp_path)
    session = await repo.create_session(workspace_id)
    response = await TurnPipeline(repo, FailingDiscussionAdapter()).process_turn(
        workspace_id,
        session.id,
        TurnCreate(content="I want to learn substrateCAD from first principles."),
    )
    assert response.assistant_turn is None
    assert response.model_error
    turns = await repo.list_turns(session.id)
    assert [turn.role for turn in turns] == ["user"]
    assert response.artifacts_summary.artifact_ids


@pytest.mark.asyncio
async def test_bad_extraction_cannot_create_extract_exchange_only_map(tmp_path):
    repo, workspace_id = await _repo(tmp_path)
    session = await repo.create_session(workspace_id)
    turn = await repo.create_turn(session.id, "user", "hello", "hello", 1)
    patch = await MapPatchBuilder(repo).build(
        workspace_id,
        session.id,
        turn.id,
        PostTurnExtraction(
            topics=["Extract Exchange Only"],
            node_candidates=[NodeCandidate(label="Extract Exchange Only", confidence=0.4)],
        ),
    )
    assert patch.action == "no_op"


@pytest.mark.asyncio
async def test_operational_app_capability_extraction_does_not_create_learning_map(tmp_path):
    repo, workspace_id = await _repo(tmp_path)
    session = await repo.create_session(workspace_id)
    turn = await repo.create_turn(session.id, "user", "can you access my website?", "can you access my website?", 1)
    patch = await MapPatchBuilder(repo).build(
        workspace_id,
        session.id,
        turn.id,
        PostTurnExtraction(
            topics=["Web browsing/search capability"],
            node_candidates=[
                NodeCandidate(
                    label="Read-Only Environment",
                    description="The app cannot resolve websites in its current runtime.",
                    confidence=0.9,
                )
            ],
        ),
    )
    assert patch.action == "no_op"


def test_discussion_context_is_not_short_answer_budgeted():
    context = ContextBroker().build_discussion_context(
        "I want to learn substrateCAD by talking it through.",
        [],
        "discuss",
        "substrateCAD: geometry kernel, fabrication/process constraints",
    )
    assert "Research Partner" in context
    assert "high-bandwidth technical/physical research conversation partner" in context
    assert "tension testing" in context
    assert "Do not give a generic short answer" in context
    assert "Stay compact" not in context
    assert "Target response budget" not in context


class FailingDiscussionAdapter(LlmAdapter):
    provider_name = "failing"
    supports_web_search = False
    supports_schema_output = True

    async def complete_text(self, request: LlmTextRequest) -> LlmTextResult:
        raise LlmUnavailableError("Model unavailable for test", {"provider": "test"})

    async def complete_json(self, request: LlmJsonRequest, schema: dict | None = None) -> LlmJsonResult:
        raise LlmUnavailableError("Model unavailable for test", {"provider": "test"})

    async def healthcheck(self) -> LlmHealth:
        return LlmHealth(provider_name=self.provider_name, available=False, message="unavailable")
