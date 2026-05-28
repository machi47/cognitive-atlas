# Cognitive Atlas API

FastAPI backend for the local-first Cognitive Atlas app. The default provider is the deterministic fake LLM adapter so the full vertical slice works without network credentials.

Run from the repo root:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e apps/api[dev]
python -m atlas_api.db.migrate
uvicorn atlas_api.main:app --host 127.0.0.1 --port 8787 --app-dir apps/api
```

