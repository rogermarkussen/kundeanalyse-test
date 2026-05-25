#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

rm -rf dist
mkdir -p dist

uv run marimo export html-wasm customer_churn_demo.py \
  -o dist/kundeanalyse_marimo_app.html \
  --mode run \
  --no-show-code \
  --execute \
  --force

cp dist/kundeanalyse_marimo_app.html dist/index.html
rm -f dist/CLAUDE.md dist/AGENTS.md dist/agents.md

echo "Built GitHub Pages app in: $ROOT/dist"
