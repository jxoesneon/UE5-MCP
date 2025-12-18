#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Install it with: brew install uv" >&2
  exit 1
fi

uv lock --check
uv sync --locked

uv run --locked python -m compileall scripts modules >/dev/null

uv run --locked python scripts/check_docs_contract.py

uv run --locked ruff check .

uv run --locked mypy \
  modules/mcp_protocol/src \
  modules/mcp_core/src \
  modules/mcp_cli/src \
  modules/mcp_target_blender/src \
  modules/mcp_target_ue5/src

PYTHONPATH=modules/mcp_protocol/src:modules/mcp_core/src:modules/mcp_cli/src:modules/mcp_target_blender/src:modules/mcp_target_ue5/src \
  uv run --locked pytest

if command -v npx >/dev/null 2>&1; then
  npx --yes markdownlint-cli2@0.20.0 "**/*.md" "#node_modules" "#venv" "#.venv"
else
  echo "npx is not installed. Install Node.js/npm to run markdownlint." >&2
  exit 1
fi

uv run --locked pre-commit run --all-files
