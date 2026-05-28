# FINAL_STATUS

Canonical contract: `docs/PROJECT_SPEC.md`.

## Current Status

- Status: v0 implementation complete and verified locally.
- First vertical slice: complete.
- Git commit: complete (`a3dbcaf`, initial implementation).
- GitHub push: complete (`https://github.com/machi47/cognitive-atlas`).

## Implemented Features

- Canonical project spec saved verbatim in `docs/PROJECT_SPEC.md`.
- Traceability ledger in `docs/IMPLEMENTATION_TRACE.md`.
- FastAPI backend with config, structured logging, optional bearer auth, CORS, migrations, SQLite WAL, FTS, and static frontend serving.
- Sessions API/UI: create, list, open, patch, archive, fork, and persistent turn history.
- Turn pipeline: intake, command/mode routing, topic route, research need detection, compact assistant reply, extraction artifact, patch build/validation/write, events, FTS update, atlas projection.
- Fake LLM adapter with deterministic analog-compute and agent-architecture seed behavior.
- Codex CLI adapter abstraction with healthcheck, async subprocess execution, schema file support, run logs, timeout handling, and graceful fallback.
- OpenAI Responses placeholder disabled by default.
- Map forest persistence: topic maps, nodes, edges, claims, open questions, analogies, latent bridges, patches, provenance.
- Source cards and best-effort OpenAlex/Crossref/arXiv broker, plus manual source endpoint.
- React/Vite frontend: quick capture, conversation, sticky composer, sessions, atlas tree, inspector, map impact, sources, search, settings.
- Mobile-first/PWA support: manifest, icon, generated service worker, compact chat header, composer-only bottom area, safe-area CSS, 16px inputs.
- Exports: session markdown, map markdown, atlas JSON.
- Learning-fit report and feedback endpoint.
- Deployment scripts/docs: dev, build, run, migrate, smoke, backup, Tailscale Serve, systemd.

## Verification Results

- `./scripts/test.sh`: passed.
  - Backend: 9 pytest tests passed.
  - Frontend: 2 Vitest tests passed.
- `./scripts/build.sh`: passed.
  - TypeScript compile passed.
  - Vite production build passed.
  - PWA service worker generated.
- `./scripts/smoke_test.sh`: passed.
  - Migrated smoke DB.
  - Created session.
  - Submitted analog-compute messy thought.
  - Verified compact assistant reply and patch id.
  - Fetched atlas tree, search, session export, and root frontend.
- Vite dev start check: passed at `http://127.0.0.1:5173`.

## How To Run Local Dev

```sh
./scripts/install.sh
./scripts/dev.sh
```

- API: `http://127.0.0.1:8787`
- Frontend dev: `http://127.0.0.1:5173`

## How To Run Production

```sh
./scripts/build.sh
./scripts/run_api.sh
```

Open `http://127.0.0.1:8787`.

## Tailscale Access

```sh
./scripts/tailscale_serve.sh
tailscale serve localhost:8787
```

The app binds to localhost by default. Do not use Funnel for this private app.

## Adapter Status

- Fake adapter: test-only; requires `ATLAS_ALLOW_FAKE_FOR_TESTS=true`.
- Codex CLI adapter: default runtime provider; model failures return structured errors and do not create fake assistant turns.
- OpenAI Responses adapter: placeholder only, disabled by default.

## Acceptance Criteria Status

1. From empty directory, repo is created: complete.
2. Backend starts: complete, smoke tested.
3. Frontend starts: complete, Vite start checked and production root served.
4. User can open app: complete.
5. User can create new session: complete.
6. User can submit messy thought: complete.
7. App returns compact assistant response: complete.
8. App stores raw user turn: complete.
9. App stores assistant turn: complete.
10. App creates artifacts: complete.
11. App updates atlas tree or no-op patch: complete.
12. User can open session history: complete.
13. User can create another unrelated session: complete.
14. Both sessions can touch overarching atlas: complete through shared workspace/maps.
15. Search works: complete.
16. Export works: complete.
17. App works with fake LLM adapter: complete for tests/fixtures only.
18. App attempts Codex adapter if configured: complete.
19. Missing Codex does not crash app: complete through fallback.
20. Mobile layout works at narrow width: implemented via responsive CSS; not browser-screenshot verified.
21. Desktop layout works wide: implemented via responsive CSS; build verified.
22. PWA manifest exists: complete.
23. Tailscale serve docs/scripts exist: complete.
24. Tests run: complete.
25. Git commit exists: complete.
26. GitHub push attempted when possible: complete.

## Known Limitations

- SSE is deferred; v0 uses polling/refetch and persisted events.
- Core pipeline runs synchronously for the first reply; queue abstraction exists for later background extraction/research.
- Source search is best-effort and only runs for explicit research/source/current/latest/citation requests to avoid latency and accidental fabricated research claims.
- The runtime no longer falls back to test-adapter answers.
- The mobile chat surface was corrected after screenshot review: no onboarding essay, no provider banner, no primary mode dropdown, no persistent bottom tab bar on the chat screen, and no assistant identity labeled as Atlas.
- Mobile/desktop layouts were build-verified, not screenshot-verified in Safari.
- Manual patch apply/reject/undo status endpoints exist, but full inverse-patch rollback is not implemented in v0.

## Next Steps

1. Run the app through a real mobile Safari PWA install check.
2. Add SSE or a persistent background queue when the synchronous vertical slice is stable.
3. Expand source-card provenance linking from source cards into individual claims.
4. Add richer map-detail frontend views for claims, timelines, and latent bridge decisions.
