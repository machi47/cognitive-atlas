# Learning Chat

Learning Chat is a private, local-first conversation-centered learning kernel. It is for messy associative thinking: the main chat stays compact and readable while the backend extracts topics, claims, source needs, open questions, map patches, and provenance into optional memory/debug surfaces.

It is not a generic notes app, chatbot wrapper, public service, or graph-first knowledge toy.

## Quick Start

```sh
./scripts/install.sh
./scripts/dev.sh
```

- API: `http://127.0.0.1:8787`
- Vite app: `http://127.0.0.1:5173`
- Default LLM provider: Codex CLI

## Production Local

```sh
./scripts/build.sh
./scripts/run_api.sh
```

The FastAPI backend serves the built frontend if `apps/web/dist` exists.

## Tailscale

Run the app on localhost, then expose it privately:

```sh
./scripts/tailscale_serve.sh
tailscale serve localhost:8787
```

Do not use Funnel for this app.

## Codex CLI Adapter

Codex mode is the default runtime:

```sh
./scripts/run_api.sh
```

If Codex is missing, unauthenticated, times out, exits nonzero, or returns malformed structured output, the turn fails with a structured error. The app does not fabricate an assistant answer.

Fake mode is reserved for tests:

```sh
ATLAS_LLM_PROVIDER=fake ATLAS_ALLOW_FAKE_FOR_TESTS=true ./scripts/smoke_test.sh
```

## Environment

Copy `.env.example` to `.env` if you want local overrides. Important values:

- `ATLAS_DATA_DIR=./data`
- `ATLAS_LLM_PROVIDER=codex|openai|fake`
- `ATLAS_ALLOW_FAKE_FOR_TESTS=false`
- `APP_ACCESS_TOKEN=` optional bearer gate
- `ATLAS_DEBUG=false`
- `ATLAS_STORE_LLM_PROMPTS=false`

## Data

Runtime state lives under `./data` and is gitignored. Back up the database with:

```sh
./scripts/backup.sh
```

## Tests

```sh
./scripts/test.sh
./scripts/smoke_test.sh
```

## GitHub

After verification:

```sh
./scripts/create_github_repo.sh
```
