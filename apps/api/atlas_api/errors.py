from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


@dataclass
class AppError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: dict[str, Any] | None = None


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found", details: dict[str, Any] | None = None):
        super().__init__("not_found", message, 404, details)


class ValidationAppError(AppError):
    def __init__(self, message: str = "Validation failed", details: dict[str, Any] | None = None):
        super().__init__("validation_error", message, 422, details)


class AuthRequiredError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__("auth_required", message, 401)


class LlmUnavailableError(AppError):
    def __init__(self, message: str = "LLM provider unavailable", details: dict[str, Any] | None = None):
        super().__init__("llm_unavailable", message, 503, details)


class PatchValidationFailedError(AppError):
    def __init__(self, message: str = "Patch validation failed", details: dict[str, Any] | None = None):
        super().__init__("patch_validation_failed", message, 422, details)


def error_payload(exc: AppError, request_id: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "error": {
            "code": exc.code,
            "message": exc.message,
        }
    }
    if exc.details:
        payload["error"]["details"] = exc.details
    if request_id:
        payload["error"]["request_id"] = request_id
    return payload


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(exc, getattr(request.state, "request_id", None)),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        payload = AppError("internal", "Internal server error", 500, {"type": type(exc).__name__})
        return JSONResponse(
            status_code=500,
            content=error_payload(payload, getattr(request.state, "request_id", None)),
        )

