# Implementation Trace

This file maps the implementation back to [PROJECT_SPEC.md](PROJECT_SPEC.md), which is the canonical contract for this repository.

## Running Trace

| Spec section | Requirement area | Implementation status | Evidence |
| --- | --- | --- | --- |
| 0 | Conversation-centered learning kernel intent | Complete for v0 | App implements clean conversation plus hidden extraction/map residue. |
| 1 | Defaults | Complete | FastAPI, Pydantic v2, SQLite/FTS5, React/Vite, TanStack Query, Zustand, fake/Codex adapters, local data directory. |
| 3 | Clean conversation plane | Complete for v0 | `ConversationalAgent` returns compact reply; artifacts/patches stay in inspector/API. |
| 4 | Core turn pipeline | Complete for v0 | `TurnPipeline` runs intake, route, research detection, reply, extraction, validation, patch write, FTS/event persistence. |
| 5 | Map forest | Complete for v0 | Maps/nodes/edges/questions/bridges are persisted and projected as a tree. |
| 6 | Sessions | Complete for v0 | Create/list/get/patch/archive/fork/session turns implemented in API and UI. |
| 7 | Epistemic model | Complete for v0 | Claims/relations carry epistemic status, confidence, provenance, source ids. |
| 8 | Cross-domain importance | Complete for v0 | LatentBridge schema/model/table/writer/projection included, capped in map graph. |
| 9 | Response style | Complete for v0 | Fake adapter and discussion service produce compact no-table answers. |
| 10 | LLM adapter design | Complete for v0 | Fake, Codex CLI, and OpenAI placeholder adapters implement `LlmAdapter`. |
| 11 | Worker roles | Complete for v0 | Services are separate classes for intake, context, routing, research, sources, reply, extraction, patching, UI, export, learning fit. |
| 12 | Database schema | Complete | Migration creates requested tables, WAL, indexes, FTS tables. |
| 13 | API endpoints | Complete for v0 | Requested endpoint families exist; SSE is deferred in favor of polling. |
| 14 | Frontend UX | Complete for v0 | Desktop shell, mobile nav, quick capture, conversation, composer, atlas tree, inspector, sources, settings. |
| 15 | Learning fit | Complete for v0 | Feedback artifact endpoint and `/api/learning-fit/report` implemented. |
| 16 | Sources/research | Complete for v0 | Manual/source search endpoints plus OpenAlex/Crossref/arXiv best-effort broker; explicit research triggers only. |
| 17 | Context isolation | Complete for v0 | `ContextBroker` enforces bounded role packets; discussion context excludes whole atlas. |
| 18 | Structured schemas | Complete | JSON schema files and Pydantic models added. |
| 19 | Background processing | Partial by design | Core pipeline is synchronous for reliable v0; status artifacts/events and polling endpoints exist; queue abstraction included. |
| 20 | File structure | Complete | Repo follows requested monorepo layout. |
| 21 | Backend details | Complete for v0 | Config/env/TOML, DB manager, migration runner, structured logs, optional token auth, UTC IDs/timestamps. |
| 22 | Codex CLI adapter | Complete for v0 | Healthcheck, subprocess execution, schema file support, timeout, run logs, graceful fallback. |
| 23 | Worker prompts | Complete for v0 | Prompt templates and adapter instructions emphasize compact output, provenance, no fake beliefs. |
| 24 | UI details | Complete for v0 | Required shell/components implemented with safe-area mobile CSS and shortcuts. |
| 25 | PWA | Complete for v0 | Manifest, icon, install metadata, generated service worker. |
| 26 | Exports | Complete for v0 | Session markdown, map markdown, atlas JSON. |
| 27 | Testing | Complete | Backend pytest, Vitest, production build, smoke script pass. |
| 28 | Deployment | Complete for v0 | Dev/build/run/migrate/smoke/backup/Tailscale/systemd scripts and docs. |
| 29 | GitHub | Pending final step | Commit and push run after final status update. |
| 30 | Documentation | Complete for v0 | README and architecture/data/adapters/UI/deployment/learning-fit docs added. |
| 31 | Phases | Complete for v0 | First vertical slice prioritized and verified. |
| 32 | Acceptance criteria | Complete/partial noted | See FINAL_STATUS.md for criteria status. |
| 33 | Quality bar | Complete for v0 | Core loop is working and tested; not a frontend-only or backend-only sketch. |
| 34 | Initial seed behavior | Complete | Fake adapter creates analog compute and agent architecture seed behavior. |
| 35 | Schema examples | Complete | Schema files and models reflect requested shapes. |
| 36 | Example turn handling | Complete | Smoke test uses the analog compute/SoC/ADC overhead example. |
| 37 | Commands/scripts | Complete for v0 | Makefile targets and scripts added. |
| 38 | Error handling | Complete for v0 | AppError API shape and frontend error states added. |
| 39 | Performance | Complete for v0 | WAL, indexes, explicit FTS, bounded projections, TanStack Query caching. |
| 40 | Backups | Complete for v0 | `scripts/backup.sh` and restore docs included. |
| 41 | Security/privacy | Complete for v0 | `.env`, data, logs, Codex runs gitignored; prompt storage disabled by default; optional bearer token. |
| 42 | Final status | Complete | FINAL_STATUS.md updated with verification results. |
| 43 | Start implementation | Complete for v0 | Repo built from empty directory. |

## Implementation Decisions

- `docs/PROJECT_SPEC.md` is the source of truth. Any implementation shortcut must be recorded here and in `FINAL_STATUS.md`.
- Use `python3.12` explicitly because `/usr/bin/python3` is Python 3.9.6 on this machine.
- Use `pnpm` because it is installed.
- Use synchronous core pipeline in v0 for the first reply, with events/artifacts preserving worker state. This keeps the vertical slice reliable while leaving the queue abstraction in place.
- Default LLM provider is fake so the app works without keys or Codex auth at runtime. Codex CLI support remains available through the adapter.
- Do not run source searches for every frontier-looking turn in default discuss mode. The detector flags research need, but source broker runs only for explicit research/source/current/latest/citation requests to preserve latency and avoid fake claims that research happened.

## Completed Feature Ledger

- Canonical spec, implementation trace, and final status ledger were created before app code.
- Backend vertical slice is implemented and tested: session creation, turn submission, compact fake reply, artifact extraction, map patch validation/application, atlas tree update, search, exports.
- Frontend vertical slice is implemented and built: quick capture, sessions, conversation, composer, atlas tree, inspector, sources, search, settings, PWA/mobile shell.
- Verification passed: backend pytest, frontend Vitest, production build, smoke test, Vite dev server start check.
