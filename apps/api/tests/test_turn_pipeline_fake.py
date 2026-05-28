import pytest

from atlas_api.db.connection import Database
from atlas_api.db.migrations import run_migrations
from atlas_api.db.repositories import Repository
from atlas_api.llm.fake_adapter import FakeLlmAdapter
from atlas_api.models.turns import TurnCreate
from atlas_api.workers.pipeline import TurnPipeline


@pytest.mark.asyncio
async def test_fake_turn_pipeline_creates_artifact_and_map(tmp_path):
    db = Database(tmp_path / "atlas.db")
    await run_migrations(db)
    repo = Repository(db)
    workspace_id = await repo.ensure_default_workspace()
    session = await repo.create_session(workspace_id)
    response = await TurnPipeline(repo, FakeLlmAdapter()).process_turn(
        workspace_id,
        session.id,
        TurnCreate(content="I think analog compute and compute in memory are connected to SoC design because data movement kills you, but ADC overhead may erase the benefit."),
    )
    assert "data movement" in response.assistant_turn.content
    assert response.artifacts_summary.artifact_ids
    assert response.artifacts_summary.patch_ids
    tree = await repo.atlas_tree(workspace_id)
    assert any(item.title == "Analog Compute" for item in tree.uncategorized_maps)

