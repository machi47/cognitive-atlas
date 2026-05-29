from __future__ import annotations

import os
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Research Partner"
    host: str = Field(default="127.0.0.1", alias="ATLAS_HOST")
    port: int = Field(default=8787, alias="ATLAS_PORT")
    data_dir: Path = Field(default=Path("./data"), alias="ATLAS_DATA_DIR")
    llm_provider: str = Field(default="codex", alias="ATLAS_LLM_PROVIDER")
    codex_bin: str = Field(default="codex", alias="ATLAS_CODEX_BIN")
    codex_model_discuss: str = Field(default="gpt-5.5", alias="ATLAS_CODEX_MODEL_DISCUSS")
    codex_model_extract: str = Field(default="gpt-5.5", alias="ATLAS_CODEX_MODEL_EXTRACT")
    codex_model_route: str = Field(default="gpt-5.5", alias="ATLAS_CODEX_MODEL_ROUTE")
    codex_model_research: str = Field(default="gpt-5.5", alias="ATLAS_CODEX_MODEL_RESEARCH")
    codex_reasoning_discuss: str = Field(default="medium", alias="ATLAS_CODEX_REASONING_DISCUSS")
    codex_reasoning_extract: str = Field(default="high", alias="ATLAS_CODEX_REASONING_EXTRACT")
    codex_reasoning_route: str = Field(default="low", alias="ATLAS_CODEX_REASONING_ROUTE")
    codex_reasoning_research: str = Field(default="high", alias="ATLAS_CODEX_REASONING_RESEARCH")
    codex_live_search: bool = Field(default=False, alias="ATLAS_CODEX_LIVE_SEARCH")
    codex_timeout_seconds: int = Field(default=180, alias="ATLAS_CODEX_TIMEOUT_SECONDS")
    app_access_token: str = Field(default="", alias="APP_ACCESS_TOKEN")
    debug: bool = Field(default=False, alias="ATLAS_DEBUG")
    store_llm_prompts: bool = Field(default=False, alias="ATLAS_STORE_LLM_PROMPTS")
    allow_fake_for_tests: bool = Field(default=False, alias="ATLAS_ALLOW_FAKE_FOR_TESTS")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    cors_origins: str = Field(default="http://127.0.0.1:5173,http://localhost:5173", alias="ATLAS_CORS_ORIGINS")

    @property
    def database_path(self) -> Path:
        return self.data_dir / "cognitive_atlas.db"

    @property
    def artifacts_dir(self) -> Path:
        return self.data_dir / "artifacts"

    @property
    def exports_dir(self) -> Path:
        return self.data_dir / "exports"

    @property
    def codex_runs_dir(self) -> Path:
        return self.data_dir / "codex_runs"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def require_token(self) -> bool:
        return bool(self.app_access_token)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def ensure_dirs(self) -> None:
        for path in [
            self.data_dir,
            self.artifacts_dir,
            self.exports_dir,
            self.data_dir / "imports",
            self.codex_runs_dir,
            self.logs_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def public_config(self, provider_health: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "llm_provider": self.llm_provider,
            "debug": self.debug,
            "require_token": self.require_token,
            "data_dir": str(self.data_dir),
            "provider_health": provider_health or {},
        }


def _settings_from_toml() -> dict[str, Any]:
    path = Path(os.environ.get("ATLAS_CONFIG", "atlas.config.toml"))
    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    flattened: dict[str, Any] = {}
    if server := data.get("server", {}):
        flattened["ATLAS_HOST"] = server.get("host", "127.0.0.1")
        flattened["ATLAS_PORT"] = server.get("port", 8787)
    if data_section := data.get("data", {}):
        flattened["ATLAS_DATA_DIR"] = data_section.get("dir", "./data")
    if llm := data.get("llm", {}):
        flattened["ATLAS_LLM_PROVIDER"] = llm.get("provider", "fake")
        flattened["ATLAS_CODEX_BIN"] = llm.get("codex_bin", "codex")
        flattened["ATLAS_CODEX_LIVE_SEARCH"] = llm.get("codex_live_search", False)
        flattened["ATLAS_CODEX_TIMEOUT_SECONDS"] = llm.get("codex_timeout_seconds", 180)
    if security := data.get("security", {}):
        flattened["APP_ACCESS_TOKEN"] = security.get("app_access_token", "")
    if debug := data.get("debug", {}):
        flattened["ATLAS_DEBUG"] = debug.get("enabled", False)
        flattened["ATLAS_STORE_LLM_PROMPTS"] = debug.get("store_llm_prompts", False)
    return {key: value for key, value in flattened.items() if key not in os.environ}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    for key, value in _settings_from_toml().items():
        os.environ.setdefault(key, str(value).lower() if isinstance(value, bool) else str(value))
    settings = Settings()
    settings.ensure_dirs()
    return settings
