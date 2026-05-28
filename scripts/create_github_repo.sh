#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init
fi

if ! git diff --cached --quiet || ! git diff --quiet || [ -z "$(git log --oneline 2>/dev/null || true)" ]; then
  git add .
  git commit -m "Initial cognitive atlas implementation" || true
fi

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  if git remote get-url origin >/dev/null 2>&1; then
    git push -u origin HEAD
  else
    gh repo create cognitive-atlas --private --source=. --remote=origin --push
  fi
else
  echo "gh auth unavailable. Run: gh repo create cognitive-atlas --private --source=. --remote=origin --push"
fi

