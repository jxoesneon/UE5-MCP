#!/usr/bin/env bash
set -euo pipefail

python3 -m compileall scripts >/dev/null

python3 scripts/check_docs_contract.py

if ! command -v markdownlint-cli2 >/dev/null 2>&1; then
  echo "markdownlint-cli2 is not installed. Install it with: npm install --global markdownlint-cli2" >&2
  exit 1
fi

markdownlint-cli2 "**/*.md" "#node_modules"

if command -v pre-commit >/dev/null 2>&1; then
  pre-commit run --all-files
fi
