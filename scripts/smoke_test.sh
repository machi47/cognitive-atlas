#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  ./scripts/install.sh
fi

source .venv/bin/activate
export ATLAS_DATA_DIR="${ATLAS_DATA_DIR:-./data/smoke}"
export ATLAS_LLM_PROVIDER=fake
export ATLAS_ALLOW_FAKE_FOR_TESTS=true
python -m atlas_api.db.migrate

uvicorn atlas_api.main:app --app-dir apps/api --host 127.0.0.1 --port 8787 >/tmp/cognitive-atlas-smoke.log 2>&1 &
PID=$!
cleanup() { kill "$PID" >/dev/null 2>&1 || true; }
trap cleanup EXIT

for _ in {1..30}; do
  if curl -sf http://127.0.0.1:8787/api/health >/dev/null; then
    break
  fi
  sleep 1
done

SESSION_JSON=$(curl -sf -X POST http://127.0.0.1:8787/api/sessions -H 'content-type: application/json' -d '{"title":"Smoke"}')
SESSION_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$SESSION_JSON")
TURN_JSON=$(curl -sf -X POST "http://127.0.0.1:8787/api/sessions/${SESSION_ID}/turns" -H 'content-type: application/json' -d '{"content":"I think analog compute and compute in memory are connected to SoC design because data movement kills you, but I also do not know whether ADC overhead makes the whole thing fake."}')
python -c 'import json,sys; data=json.load(sys.stdin); assert data["assistant_turn"]["content"]; assert data["artifacts_summary"]["patch_ids"]' <<<"$TURN_JSON"
curl -sf http://127.0.0.1:8787/api/atlas/tree >/dev/null
curl -sf 'http://127.0.0.1:8787/api/search?q=analog' >/dev/null
curl -sf "http://127.0.0.1:8787/api/export/session/${SESSION_ID}.md" >/dev/null
curl -sf http://127.0.0.1:8787/ >/dev/null

echo "Smoke test passed"
