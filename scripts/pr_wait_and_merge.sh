#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <pr-number-or-url>" >&2
  exit 2
fi

PR_REF="$1"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is required for this workflow." >&2
  exit 1
fi

gh pr checks "$PR_REF" --watch

# Best-effort approval (GitHub blocks self-approval). Non-fatal.
if ! gh pr review "$PR_REF" --approve -b "Auto-approval: all CI checks passed." >/dev/null 2>&1; then
  true
fi

gh pr merge "$PR_REF" --merge --delete-branch
