from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

from atlas_api.config import Settings
from atlas_api.errors import LlmMalformedOutputError, LlmProviderFailedError, LlmUnauthenticatedError, LlmUnavailableError
from atlas_api.llm.base import LlmAdapter
from atlas_api.models.llm import LlmHealth, LlmJsonRequest, LlmJsonResult, LlmTextRequest, LlmTextResult
from atlas_api.util.ids import new_id


class CodexCliAdapter(LlmAdapter):
    provider_name = "codex"
    supports_web_search = True
    supports_schema_output = True

    def __init__(self, settings: Settings):
        self.settings = settings

    async def healthcheck(self) -> LlmHealth:
        if not shutil.which(self.settings.codex_bin):
            return LlmHealth(provider_name=self.provider_name, available=False, message="Codex CLI not found; app still works in fake mode")
        try:
            proc = await asyncio.create_subprocess_exec(
                self.settings.codex_bin,
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5)
            if proc.returncode == 0:
                return LlmHealth(provider_name=self.provider_name, available=True, message="Codex CLI ready", details={"version": stdout.decode().strip()})
            return LlmHealth(provider_name=self.provider_name, available=False, message="Codex CLI returned an error", details={"stderr": stderr.decode(errors="replace")})
        except Exception as exc:
            return LlmHealth(provider_name=self.provider_name, available=False, message="Codex CLI healthcheck failed", details={"error": str(exc)})

    async def complete_text(self, request: LlmTextRequest) -> LlmTextResult:
        run = await self._run_codex(request.prompt, request.task, request.model, request.reasoning_effort, None)
        self._raise_for_failed_run(run)
        return LlmTextResult(text=run.get("message", ""), provider_name=self.provider_name, raw=run)

    async def complete_json(self, request: LlmJsonRequest, schema: dict[str, Any] | None = None) -> LlmJsonResult:
        run = await self._run_codex(request.prompt, request.task, request.model, request.reasoning_effort, schema)
        self._raise_for_failed_run(run)
        message = run.get("message", "")
        data = run.get("json")
        if data is None:
            data = self._extract_json(message)
        if not isinstance(data, dict):
            raise LlmMalformedOutputError(
                "Codex CLI returned malformed JSON for a structured task",
                {"provider": "Codex CLI", "task": request.task, "run_id": run.get("run_id"), "message_summary": message[:1200]},
            )
        return LlmJsonResult(data=data, provider_name=self.provider_name, raw=run)

    async def _run_codex(
        self,
        prompt: str,
        task: str,
        model: str | None,
        reasoning_effort: str | None,
        schema: dict[str, Any] | None,
    ) -> dict[str, Any]:
        health = await self.healthcheck()
        if not health.available:
            raise LlmUnavailableError(
                health.message,
                {
                    "provider": "Codex CLI",
                    "reason": health.message,
                    "next_commands": ["codex --version", "codex login"],
                    **health.details,
                },
            )
        run_id = new_id("codexrun")
        run_dir = self.settings.codex_runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = run_dir / "prompt.md"
        schema_path: Path | None = None
        if self.settings.store_llm_prompts:
            prompt_path.write_text(prompt, encoding="utf-8")
        else:
            prompt_path.write_text("[prompt storage disabled]\n", encoding="utf-8")
        args = [
            self.settings.codex_bin,
            "exec",
            "--skip-git-repo-check",
            "--json",
            "--sandbox",
            "read-only",
            "--cd",
            str(Path.cwd()),
            "--model",
            model or self._model_for_task(task),
            "-c",
            f"model_reasoning_effort={reasoning_effort or self._reasoning_for_task(task)}",
        ]
        if schema:
            schema_path = run_dir / "schema.json"
            schema_path.write_text(json.dumps(schema), encoding="utf-8")
            args.extend(["--output-schema", str(schema_path)])
        if self.settings.codex_live_search and "research" in task.lower():
            args.append("--search")
        output_path = run_dir / "last_message.txt"
        args.extend(["--output-last-message", str(output_path), "-"])
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(prompt.encode("utf-8")), timeout=self.settings.codex_timeout_seconds)
            stdout_text = stdout.decode(errors="replace")
            stderr_text = stderr.decode(errors="replace")
            (run_dir / "stdout.jsonl").write_text(stdout_text, encoding="utf-8")
            (run_dir / "stderr.log").write_text(stderr_text, encoding="utf-8")
            message, parsed_json = self._parse_json_stream(stdout_text)
            if output_path.exists():
                file_message = output_path.read_text(encoding="utf-8")
                if file_message.strip():
                    message = file_message.strip()
            return {
                "run_id": run_id,
                "returncode": proc.returncode,
                "message": message,
                "json": parsed_json,
                "stderr_tail": stderr_text[-2000:],
            }
        except asyncio.TimeoutError:
            return {"run_id": run_id, "returncode": None, "message": "", "error": "timeout"}
        except Exception as exc:
            return {"run_id": run_id, "returncode": None, "message": "", "error": str(exc)}

    def _raise_for_failed_run(self, run: dict[str, Any]) -> None:
        if run.get("error") == "timeout":
            raise LlmProviderFailedError(
                "Codex CLI timed out",
                {"provider": "Codex CLI", "reason": "timeout", "run_id": run.get("run_id"), "next_commands": ["codex --version", "codex login"]},
            )
        if run.get("error"):
            raise LlmProviderFailedError(
                "Codex CLI failed",
                {"provider": "Codex CLI", "reason": run.get("error"), "run_id": run.get("run_id"), "next_commands": ["codex --version", "codex login"]},
            )
        returncode = run.get("returncode")
        if returncode not in (0, None):
            stderr = str(run.get("stderr_tail", ""))
            lower = stderr.lower()
            details = {
                "provider": "Codex CLI",
                "returncode": returncode,
                "stderr_summary": stderr[-1200:],
                "run_id": run.get("run_id"),
                "next_commands": ["codex --version", "codex login"],
            }
            if "auth" in lower or "login" in lower or "unauthorized" in lower:
                raise LlmUnauthenticatedError("Codex CLI is not authenticated", details)
            raise LlmProviderFailedError("Codex CLI exited with a nonzero status", details)

    def _model_for_task(self, task: str) -> str:
        task_lower = task.lower()
        if "extract" in task_lower:
            return self.settings.codex_model_extract
        if "route" in task_lower:
            return self.settings.codex_model_route
        if "research" in task_lower:
            return self.settings.codex_model_research
        return self.settings.codex_model_discuss

    def _reasoning_for_task(self, task: str) -> str:
        task_lower = task.lower()
        if "extract" in task_lower:
            return self.settings.codex_reasoning_extract
        if "route" in task_lower:
            return self.settings.codex_reasoning_route
        if "research" in task_lower:
            return self.settings.codex_reasoning_research
        return self.settings.codex_reasoning_discuss

    def _parse_json_stream(self, stdout_text: str) -> tuple[str, dict[str, Any] | None]:
        last_message = ""
        parsed_json = None
        for line in stdout_text.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = event.get("message") or event.get("text") or event.get("content")
            if isinstance(text, str):
                last_message = text
            if isinstance(event.get("output"), dict):
                parsed_json = event["output"]
            if event.get("type") in {"agent_message", "message"} and isinstance(event.get("data"), str):
                last_message = event["data"]
        if not last_message:
            last_message = stdout_text.strip()
        return last_message, parsed_json

    def _extract_json(self, text: str) -> dict[str, Any] | None:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
