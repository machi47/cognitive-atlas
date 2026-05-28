import pytest

from atlas_api.db.connection import Database
from atlas_api.db.migrations import run_migrations
from atlas_api.db.repositories import Repository
from atlas_api.llm.fake_adapter import FakeLlmAdapter
from atlas_api.models.turns import TurnCreate
from atlas_api.workers.pipeline import TurnPipeline


@pytest.mark.asyncio
async def test_substratecad_response_is_about_actual_user_goal(tmp_path):
    db = Database(tmp_path / "atlas.db")
    await run_migrations(db)
    repo = Repository(db)
    workspace_id = await repo.ensure_default_workspace()
    session = await repo.create_session(workspace_id)
    response = await TurnPipeline(repo, FakeLlmAdapter()).process_turn(
        workspace_id,
        session.id,
        TurnCreate(content="I want to learn everything I'd need to know to end up being able to build my own substrateCAD from first principles"),
    )
    text = response.assistant_turn.content
    lower = text.lower()
    assert "substratecad" in lower or "substrate" in lower
    assert any(term in lower for term in ["geometry", "cad", "fabrication", "materials", "process", "electrical", "layers"])
    assert "mode" not in lower
    assert "fake" not in lower
    assert "capture the messy thought" not in lower

