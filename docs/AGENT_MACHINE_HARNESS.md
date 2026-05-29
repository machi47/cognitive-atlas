# Agent Machine Harness

This repo is meant to run as its own private service on a machine that already has the user's Codex OAuth login. It should not depend on an agent session staying alive.

## Pull And Start

```sh
git clone https://github.com/machi47/cognitive-atlas.git
cd cognitive-atlas
./scripts/run_standalone.sh
```

By default this serves on:

```text
http://0.0.0.0:8788
```

Use the agent machine's LAN or tailnet IP for the phone URL:

```text
http://<agent-machine-ip>:8788
```

## Requirements

- Python 3.12+
- Node plus `pnpm`, or Node/npm fallback
- Codex CLI installed
- `codex login status` works on the machine

No OpenAI API key is required for the default Codex runtime.

## Runtime Data

Runtime state is local and gitignored:

```text
data/cognitive_atlas.db
data/logs/
data/codex_runs/
data/artifacts/
data/exports/
```

Do not commit or upload those files. They contain chats, learning topology, model run traces, and local artifacts.

## Useful Environment Overrides

```sh
ATLAS_HOST=0.0.0.0
ATLAS_PORT=8788
ATLAS_DATA_DIR=./data
ATLAS_LLM_PROVIDER=codex
ATLAS_ALLOW_FAKE_FOR_TESTS=false
ATLAS_DEBUG=false
ATLAS_STORE_LLM_PROMPTS=false
```

Optional bearer gate:

```sh
APP_ACCESS_TOKEN=<local-secret> ./scripts/run_standalone.sh
```

## Private Tailnet

If the machine uses Tailscale, keep the app private to the tailnet. Do not use Funnel.

```sh
./scripts/run_standalone.sh
tailscale serve localhost:8788
```

## Health Checks

```sh
curl http://127.0.0.1:8788/api/health
curl http://127.0.0.1:8788/api/learn/overview
```

The health response should report the Codex provider as available. If it does not, run:

```sh
codex login status
codex login
```
