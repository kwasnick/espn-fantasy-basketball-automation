#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

# uv is included in this workspace's base runtime.
if ! command -v uv >/dev/null 2>&1; then
  echo "Install uv (https://docs.astral.sh/uv/getting-started/installation/) before running setup." >&2
  exit 1
fi

uv python install "$(cat .python-version)"
uv venv --allow-existing --python "$(cat .python-version)" .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python --version
.venv/bin/python -c 'from espn_api.basketball import League; print("ESPN basketball client ready")'
