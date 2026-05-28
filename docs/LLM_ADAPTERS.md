# LLM Adapters

The API depends on the `LlmAdapter` interface:

- `complete_text`
- `complete_json`
- `healthcheck`
- provider capability flags

## Fake Adapter

The deterministic fake adapter is the default. It supports the complete vertical slice offline and seeds useful map behavior for analog compute and learning-agent architecture.

## Codex CLI Adapter

The Codex adapter runs `codex exec` asynchronously, writes local run logs under `data/codex_runs`, uses schemas when provided, and handles missing binaries, timeouts, and malformed output without crashing the app.

## OpenAI Responses Placeholder

The placeholder is disabled unless future work enables it explicitly. The app does not require API keys in v0.

Worker prompts emphasize compact replies, source honesty, provenance, and no inferred user beliefs.

