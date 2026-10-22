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

# Daily lineup edits

Before lineup changes, read `docs/lineup-editing.md`. Future scoring periods
require `FUTURE_ROSTER`, not `ROSTER`. Use a fresh target-date snapshot, check
locks and game timing, and verify every change by readback. For reversible
tests, restore and independently compare all original roster slots. Never log
transaction payloads containing `memberId` (SWID).

# Co-manager runs

Read `docs/co-manager.md` and the operational logs before acting. Standing
authorization permits lineup placement of all players, including the four
protected stars; their roster-removal protection remains unchanged. Acquire
the run guard, preserve concurrent user moves, honor the rolling three-offer
limit and 48-hour response window, and log/verify every write. Only the scheduled
9 p.m. Pacific run sends the routine daily summary. No real-money fees.
