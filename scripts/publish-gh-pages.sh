#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This folder is not a git repository yet."
  echo "Run: git init && git remote add origin <github-repo-url>"
  exit 1
fi

remote_url="$(git remote get-url origin 2>/dev/null || true)"
if [[ -z "$remote_url" ]]; then
  echo "Missing git remote 'origin'."
  echo "Run: git remote add origin <github-repo-url>"
  exit 1
fi

"$ROOT/scripts/build-gh-pages.sh"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

cp -a dist/. "$tmpdir/"

(
  cd "$tmpdir"
  git init -q
  git checkout -q -b gh-pages
  git add .
  git commit -q -m "Deploy marimo app to GitHub Pages"
  git remote add origin "$remote_url"
  git push -f origin gh-pages
)

echo "Published dist/ to origin/gh-pages"
