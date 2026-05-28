# Learning Chat API

FastAPI backend for the local-first learning chat app. The default runtime provider is Codex CLI. The deterministic fake adapter is reserved for tests.

Run from the repo root:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e apps/api[dev]
python -m atlas_api.db.migrate
uvicorn atlas_api.main:app --host 127.0.0.1 --port 8787 --app-dir apps/api
```
