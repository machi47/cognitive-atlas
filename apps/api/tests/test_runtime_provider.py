import pytest

from atlas_api.config import get_settings
from atlas_api.llm.codex_cli_adapter import CodexCliAdapter
from atlas_api.llm.fake_adapter import FakeLlmAdapter
from atlas_api.main import _select_adapter


@pytest.mark.asyncio
async def test_fake_provider_requires_explicit_test_flag(monkeypatch):
    monkeypatch.setenv("ATLAS_LLM_PROVIDER", "fake")
    monkeypatch.setenv("ATLAS_ALLOW_FAKE_FOR_TESTS", "false")
    get_settings.cache_clear()
    adapter = await _select_adapter(get_settings())
    assert isinstance(adapter, CodexCliAdapter)
    assert not isinstance(adapter, FakeLlmAdapter)


@pytest.mark.asyncio
async def test_fake_provider_allowed_for_tests(monkeypatch):
    monkeypatch.setenv("ATLAS_LLM_PROVIDER", "fake")
    monkeypatch.setenv("ATLAS_ALLOW_FAKE_FOR_TESTS", "true")
    get_settings.cache_clear()
    adapter = await _select_adapter(get_settings())
    assert isinstance(adapter, FakeLlmAdapter)

