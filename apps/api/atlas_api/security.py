from __future__ import annotations

from fastapi import Header

from atlas_api.config import Settings
from atlas_api.errors import AuthRequiredError


async def require_access(settings: Settings, authorization: str | None = Header(default=None)) -> None:
    if not settings.require_token:
        return
    expected = f"Bearer {settings.app_access_token}"
    if authorization != expected:
        raise AuthRequiredError()

