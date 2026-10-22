# ESPN daily lineup editing

Verified October 21, 2026 (America/Los_Angeles), against configured season 2027,
league 1779277586, team 3. Future-day editing **works**. The installed espn-api
1.0.1 client supplies reads but does not implement lineup writes.

## Endpoint and payload

POST to `https://lm-api-writes.fantasy.espn.com/apis/v3/games/fba/seasons/{seasonId}/segments/0/leagues/{leagueId}/transactions/`.
Authenticate with environment `ESPN_S2` as cookie `espn_s2` and `SWID` as cookie
`SWID`. The `memberId` field also uses SWID; never print or persist the payload
with that field populated. Send JSON, `X-Fantasy-Source: kona`, and ESPN Origin
and Referer headers. Do not use league-manager overrides.

Example shape (placeholder, not a credential):

```json
{
  "isLeagueManager": false,
  "teamId": 3,
  "type": "FUTURE_ROSTER",
  "memberId": "<SWID from environment; never log>",
  "scoringPeriodId": 3,
  "executionType": "EXECUTE",
  "items": [{
    "playerId": 5041935,
    "type": "LINEUP",
    "fromLineupSlotId": 11,
    "toLineupSlotId": 12
  }]
}
```

For a completed-draft league, choose `FUTURE_ROSTER` when the target period is
greater than `status.latestScoringPeriod`; choose `ROSTER` for the current
period. Set `scoringPeriodId` to the **target** period. Each item must carry
that player's actual prior slot on that date. A swap needs both player items.
Slot 11 is Utility and slot 12 is Bench for basketball.

`scripts/lineup_payload.py` implements this distinction and conservative
validation without sending requests. It requires `draftDetail.drafted=true`;
include `mDraftDetail` in reads if necessary. It does not authorize writes,
check game times, manage restoration, or replace the workflow below.

## Authoritative evidence

ESPN's basketball team page loaded this frontend bundle during investigation:
[ESPN main-c35771d3939c007a8afd.js](https://cdn1.espn.net/kona/449ae61ae2f5-1.520/_next/static/commons/main-c35771d3939c007a8afd.js).
In `static movePlayers`, the frontend starts with the current period and
`ROSTER`; when the selected period is later and drafting is not pre-start,
it switches to the selected period and `FUTURE_ROSTER`. Constants exported as
`v` and `p` map to `ROSTER` and `FUTURE_ROSTER`. `createTransaction` carries
`transactionScoringPeriodId` into wire field `scoringPeriodId`; the item
builder translates internal `fromSlotId`/`toSlotId` to
`fromLineupSlotId`/`toLineupSlotId`. `saveTransaction` posts to `/transactions/`.
The live successful test below confirms the relevant post-draft behavior.
This is inspected frontend behavior, not a versioned public API contract.

## Dates, locks, and safe execution

1. Read identifiers from `espn.config.json`; do not silently change season.
   Resolve dates from ESPN scoring-period metadata/pro-team schedules, not the
   UTC calendar alone. In this test, period 2 was October 21 and period 3 was
   Thursday October 22, 2026. The season ID is 2027, not calendar year 2026.
2. GET the read-host version of the league URL with `view=mRoster`,
   `view=mSettings`, `view=mTeam`, and explicit `scoringPeriodId`. Snapshot
   all player IDs and slots for the target date and adjacent dates. Future
   lineups can differ substantially from today's; never restore today's slots
   onto tomorrow. Save only necessary non-secret evidence.
3. Check team `isTransactionLocked`, each affected player's `lineupLocked`,
   pending transactions, eligibility, capacities and game timing for that
   specific period. Refuse unknown locks or an imminent tipoff. Here,
   `lineupLocktimeType` was `INDIVIDUAL_GAME`, `isBenchUnlimited` was true,
   and the first period-3 game was October 22 at 16:00 PDT. Boozer had no game
   that period. `rosterLocked` is distinct from `lineupLocked`: today's roster
   locks do not prove tomorrow's lineup is locked. Never bypass a lock.
4. Avoid the four protected players in AGENTS.md. Verify the fresh lineup
   still matches the snapshot immediately before sending a narrow LINEUP-only
   transaction. No ADD, DROP, WAIVER or TRADE items belong in a lineup test.
5. Send once with a bounded timeout and no automatic write retries. Freshly
   GET the target period; compare **all** slots against the intended state.
   On a timeout or uncertain response, read first. Reads may lag, so use bounded
   read retries; do not infer success merely from HTTP 200.
6. Restore using the observed slot as `fromLineupSlotId`, with the same correct
   transaction type and target period. Independently GET all slots again and
   compare them to the snapshot. Check adjacent periods as well. Prioritize
   restoration if anything fails, and explicitly report any remaining mismatch.

## Live verification and prior failure

The initial request used `ROSTER` with target period 3 while current period was
2. ESPN returned HTTP 409, `TRAN_INVALID_SCORINGPERIOD_NOT_CURRENT`, with
"Transaction type can only be executed in the current scoring period".
Readbacks confirmed no change. This rejects that transaction type/period
combination; it does **not** mean ESPN disallows future edits. A third-party
payload example that always uses ROSTER was insufficient for daily future moves.

After inspecting ESPN's own frontend, a single corrected test used
`FUTURE_ROSTER` for October 22 / period 3:

| Player | Before | Test, independently read | Restored, independently read |
| --- | --- | --- | --- |
| Cameron Boozer (5041935) | Utility (11) | Bench (12) | Utility (11) |

Both POSTs returned HTTP 200. All 13 target-period roster slots matched their
initial values after restoration; full slot maps for periods 2 and 4 were also
unchanged. Protected players were untouched. Test ran October 21, 23:01:06–
23:01:08 PDT (October 22, 06:01:06–06:01:08 UTC).
See `docs/lineup-test-2026-10-22.json` for credential-free slot comparisons.
This establishes the tested date and adjacent-date behavior; it is not a claim
that every season, league type, or arbitrarily distant future date was tested.

Run local regression tests (no network or mutations):
` .venv/bin/python -m unittest discover -s tests -v`.
