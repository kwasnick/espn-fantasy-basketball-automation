# Workspace setup

At the beginning of work in a fresh environment, run `bash scripts/setup.sh`
from the repository root. It installs Python 3.12 and the pinned ESPN fantasy
basketball client into `.venv`, using the workspace's preinstalled `uv`.

Use `.venv/bin/python` for Python commands, or activate the environment with
`source .venv/bin/activate` in the current shell. Setup-script activation does
not carry over to later shells.

Read team identifiers from `espn.config.json`. Authenticate using `ESPN_S2` and
`SWID` from the environment; never print or commit their values.

# Untouchable players

Treat LeBron James, Stephen Curry, Kevin Durant, and Kawhi Leonard as
untouchable. Do not trade, drop, waive, or otherwise remove any of these
players from the team without explicit user approval for that action.
