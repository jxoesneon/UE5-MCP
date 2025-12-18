#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="${VENV_DIR:-.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python"

"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install pre-commit ruff mypy pytest

"$VENV_PY" -m compileall scripts modules >/dev/null

"$VENV_PY" scripts/check_docs_contract.py

"$VENV_PY" -m ruff check .

"$VENV_PY" -m mypy \
  modules/mcp_protocol/src \
  modules/mcp_core/src \
  modules/mcp_cli/src \
  modules/mcp_target_blender/src \
  modules/mcp_target_ue5/src

PYTHONPATH=modules/mcp_protocol/src:modules/mcp_core/src:modules/mcp_cli/src:modules/mcp_target_blender/src:modules/mcp_target_ue5/src \
  "$VENV_PY" -m pytest

if command -v npx >/dev/null 2>&1; then
  npx --yes markdownlint-cli2@0.20.0 "**/*.md" "#node_modules" "#venv" "#.venv"
else
  echo "npx is not installed. Install Node.js/npm to run markdownlint." >&2
  exit 1
fi

"$VENV_PY" -m pre_commit run --all-files
