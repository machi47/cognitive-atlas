# Research Partner

Research Partner is a local-first multi-conversation learning system.

The product model is:

```text
separate chats
→ shared evolving technical topology
→ source/question/tension/bridge ledger
→ conversation-derived Learn Workbench
→ selective retrieval back into future chats
```

Chats protect local train of thought. The Learn Workbench accumulates technical concepts, constraints, open questions, tensions, source needs, and bridge candidates across all chats.

## Standalone Agent Machine

Use this when the app should run as its own service on another machine with Codex OAuth already present.

```sh
git clone https://github.com/machi47/cognitive-atlas.git
cd cognitive-atlas
./scripts/run_standalone.sh
```

Default service URL:

```text
http://<agent-machine-ip>:8788
```

The standalone harness:

- installs Python and web dependencies if needed
- builds the web bundle
- runs database migrations
- starts FastAPI serving the app and API
- uses the local Codex CLI OAuth session
- keeps runtime data under gitignored `./data`
- refuses to run if Codex CLI is missing or logged out

See [Agent Machine Harness](docs/AGENT_MACHINE_HARNESS.md).

## Local Development

```sh
./scripts/install.sh
./scripts/dev.sh
```

Development URLs:

```text
API:  http://127.0.0.1:8787
Web:  http://127.0.0.1:5173
```

## Production Local

```sh
./scripts/build.sh
./scripts/run_api.sh
```

The API serves `apps/web/dist` directly when the bundle exists.

## Codex Runtime

Codex mode is the default runtime. It uses the local Codex CLI login, not an OpenAI API key.

```sh
codex login status
./scripts/run_standalone.sh
```

If Codex is missing, unauthenticated, times out, exits nonzero, or returns malformed structured output, the app returns a structured model error and preserves the user turn. It does not fabricate a runtime answer.

Fake mode is reserved for tests only:

```sh
ATLAS_LLM_PROVIDER=fake ATLAS_ALLOW_FAKE_FOR_TESTS=true ./scripts/smoke_test.sh
```

## Environment

Copy `.env.example` to `.env` for local overrides.

Important values:

```sh
ATLAS_DATA_DIR=./data
ATLAS_LLM_PROVIDER=codex
ATLAS_ALLOW_FAKE_FOR_TESTS=false
ATLAS_HOST=0.0.0.0
ATLAS_PORT=8788
APP_ACCESS_TOKEN=
ATLAS_DEBUG=false
ATLAS_STORE_LLM_PROMPTS=false
```

## Private Data

Runtime state is local and gitignored:

```text
data/cognitive_atlas.db
data/logs/
data/codex_runs/
data/artifacts/
data/exports/
```

Do not commit those files. They can contain chats, memories, source cards, model traces, and local artifacts.

Back up the runtime database with:

```sh
./scripts/backup.sh
```

## Verification

```sh
./scripts/prove_learning_loop.sh
./scripts/prove_real_codex_learning_turn.sh
.venv/bin/pytest apps/api/tests -q
pnpm --dir apps/web build
pnpm --dir apps/web test
```

## Tailnet

Keep the service private to your own network/tailnet. Do not use public Funnel for this app.

```sh
./scripts/run_standalone.sh
tailscale serve localhost:8788
```
