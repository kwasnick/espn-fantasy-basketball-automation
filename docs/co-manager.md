# Co-manager operating instructions

Standing authorization: optimize daily lineups, make aggressive fantasy-only
adds/drops/waiver claims, propose and accept worthwhile trades, and consult NBA
news. Actual-money payments or fees are not authorized. Existing virtual FAAB
may be used prudently if the league enables it. Read live rules before acting.

LeBron James (1966), Stephen Curry (3975), Kevin Durant (3202), and Kawhi Leonard
(6450) may be moved among eligible lineup slots. They may not be traded, dropped,
waived, or otherwise removed without specific direct user approval. Considering
a trade involving them is allowed; submitting it requires approval first.

Do not volunteer AI identity in ordinary league communications. Never lie about
identity if directly asked. Communicate only with verified league recipients for
necessary trade negotiations; disclose no unrelated personal or account data.

## Every run

1. Pull main before reading operating state. Stop on conflicts or unresolved
   prior write intents. Inspect `operations/events.jsonl`, `pending.json`, and
   `trade-history.json`, then reconcile against live ESPN data. Repository
   snapshots are evidence, not current truth. Do not duplicate a pending claim
   or proposal simply because a prior run's summary is missing.
2. Acquire an exclusive run guard by atomically creating
   `/tmp/espn-comanager-1779277586-3.lock` and writing an owner/start-time file
   without secrets. Hold the directory for the entire task, including research,
   writes, and logging; remove only your own guard on completion. If it exists,
   stop and report overlap. Do not delete a stale-looking guard without checking
   its owning run and reconciling unresolved writes. This is a same-environment
   guard; separate environments must be serialized by the scheduler or another
   shared lock, not run simultaneously. A short-lived check-only lock is invalid.
3. Read current settings, roster, all relevant dated lineups, schedule, injury
   news, pending transactions and recent trade history. Use the configured
   season, not the calendar year. Check real-money fees before any transaction.
4. Optimize each of the next seven daily lineups in chronological order using
   eligible slots, actual games, projected league points, news, and locks.
   `scripts/lineup_plan.py` solves the slot assignment globally and minimizes
   slot changes on ties; it does not fetch news or authorize execution.
   Expected points are estimates, not a guarantee. Revisit questionable players,
   back-to-back rest and late scratches before tipoff.
5. Immediately before every write, re-read the exact affected date and pending
   transactions. If an unrelated/user change appears, preserve it and stop that
   write for reconciliation. Append a credential-free intent to the log before
   sending. Do not automatically retry a write after a timeout or error. Read
   back first, then log the confirmed, rejected or uncertain outcome. A pending
   waiver is not a completed acquisition. For each write, verify the intended
   change and all other roster slots/membership as appropriate.
6. Re-fetch later dates after each lineup write: future changes can carry forward
   into subsequent days. Never execute a precomputed week's plan against stale
   snapshots. Recompute from fresh state and verify the entire horizon at the
   end. If propagation cannot be distinguished from a user change, stop rather
   than overwrite it. See `docs/lineup-editing.md` for wire format and locks.
7. Append results/decisions, update pending state, check for credentials, commit
   and push operational changes. Avoid committing raw ESPN league/member or
   transaction responses. Never print cookies, environment dumps, memberId,
   or complete authenticated payloads. Release the run guard after completion.

## Waivers and trades

Read acquisition limits, waiver priority/process times and budget from live data.
Prioritize meaningful upside over churn. Evaluate production in this league's
points system, role/minutes, injuries, positional fit and schedule. Do not label
a rostered player dead weight solely because of one poor game. Check locks,
pending offers, undroppable status and the four protected IDs before a drop.

Maximum three new trade proposals in any rolling seven days, including proposals
made by the user or other runs. Query history as well as pending offers; count
revoked/expired proposals too. Count every new replacement proposal, and record
a fingerprint consisting of counterparty plus sorted outgoing/incoming IDs.
Do not resend a duplicate. Target at least one worthwhile proposal per week,
but never force a bad deal for the quota. Existing user proposals count toward
the cap and should be respected. Allow at least 48 hours before ordinary
revocation; materially changed injury/roster circumstances can justify earlier
withdrawal, with the reason logged. Reassess incoming offers before acceptance,
including roster legality, pending claims, fees, and protected-player rules.

The initial review found one existing outgoing proposal (Reid for Harden), no
incoming offer. It was retained. Do not confuse its `teamActions[3]=ACCEPTED`
with a completed trade: our proposal is accepted by us and awaits team 4.

## Operational files and schema

- `operations/events.jsonl`: append-only records with ISO UTC `at`, `run_id`,
  `kind`, target period/player IDs, reason, pre-state/intended change, and later
  HTTP status plus fresh observed state and verification result. Separate
  `*_intent` and `*_result` records make interrupted writes detectable. Record
  failures and reconciliation, not only successful moves.
- `operations/pending.json`: latest checked time and whitelisted transaction
  IDs/types/statuses, team IDs, proposed/expiry timestamps, item legs and team
  actions. No member IDs or credentials.
- `operations/trade-history.json`: reconciled proposal/accept/decline history,
  including observation time and periods checked. Extend the history; do not
  erase older proposals needed for rolling limits.
- `operations/current-state.json`: dated seven-day slot maps, current injury
  assumptions, next checks and earliest games. Always refresh from ESPN.

Only the scheduled 9 p.m. Pacific run sends the routine concise daily summary.
Other runs update logs silently unless an urgent blocker or direct decision is
needed. The parent schedules checks around 8 a.m., noon, 3 p.m., 6 p.m. and 9 p.m.
Pacific. Dynamically add/shift a check to 30–60 minutes before the day's earliest
game when those times miss a lock, and preferably 10–15 minutes before critical
questionable-player tipoffs. Do not create duplicate schedules from this repo.

## Initial review: October 21, 2026 Pacific

League: Dubs on Dubs on Dubs LEAGUE, ID 1779277586; team 3, Kwaz's Kwazy Team;
season 2027; ten teams; head-to-head points.

Scoring: PTS +1, REB +1, AST +2, STL +4, BLK +4, 3PM +1, FGM +2,
FGA -1, FTM +1, FTA -1, TO -2. There are no category punts to optimize.

Slots: PG, SG, SF, PF, C, G, F, three Utility, three Bench, one IR.
ESPN also reports `isBenchUnlimited=true`; do not infer unlimited team size.
Individual-game lineup locks; roster lock at first game of scoring period.
No move limit; center position limit four. Verify position caps before adds.

Traditional waivers, 24-hour hold, no active FAAB bidding (nominal budget 100
is unused). Acquisition limit is unlimited season-wide, but
`matchupAcquisitionLimit=1` with `matchupLimitPerScoringPeriod=true` means one
acquisition per day. Waiver priority initially fourth. Settings list Sunday,
hour 8 for waiver processing, but the actual Murray player record explicitly
gives October 22, 00:00 PDT; use the player-specific timestamp and verify actual
execution rather than assuming the generic setting applies to every claim.
No transaction fees. Unlimited league trade count, 24-hour review, three veto
votes, trade deadline February 19, 2027 at 09:00 PST. Our stricter three-proposals
per rolling week policy still applies.

News reviewed from authenticated ESPN player-news GET responses (no cookies
needed in saved source URLs), plus NBA.com/ESPN injury coverage:

- Claxton: October 19 report says hamstring re-evaluation in two weeks; no
  expected games this horizon. Future-period Bench→IR execution returned 409,
  unchanged on readback; exact rejection detail was not retained. ANALYZE then
  returned `TRAN_INVALID_EXECUTIONTYPE` (unsupported for FUTURE_ROSTER).
  No successful IR method was established; leave on bench and recheck after
  current-day lock clears. Do not conflate this with ordinary future lineup moves.
- VanVleet: October 20 report says one game off per back-to-back to start the
  season. Which leg is not confirmed. Initial planning uses 50% availability
  for each consecutive date, and must update once the actual designation lands.
- Dybantsa: ankle sprain, day-to-day; initial planning uses a provisional 75%
  availability factor, a modeling assumption, not a reported probability.
- Curry was cleared to play October 21. Boozer is Memphis' starting PF.
- Murray: healthy, Denver's lead guard behind Jokic; projected 43.9 league
  points/game. Vucevic: projected 30.2, but October 17 news calls him Orlando's
  backup center. Submitted a conditional Murray-for-Vucevic waiver; no drop
  occurs unless the claim succeeds. HTTP 200 and matching pending legs verified.
- Edgecombe (33.7 projected points/game, 35 opening-night minutes) is the next
  waiver watch. Pippen (30.6, competing with Ty Jerome), Hartenstein (30.5,
  foul-limited opener), and Jalen Smith (possible Claxton replacement minutes)
  warrant monitoring, not an unverified claim of a superior long-term option.
- Preserve the existing Reid-for-Harden offer: Harden projects 42.1 versus
  Reid 35.5; Reid's strong new Charlotte role gives the other team a plausible
  frontcourt reason to consider it. No new proposal was forced. Claxton's
  injury and Vucevic's role reduce their current trade value; do not package
  them as healthy starting centers. Revisit trade needs after the waiver result.

Source pattern: `https://site.api.espn.com/apis/fantasy/v3/games/fba/news/players?playerId=ID`.
IDs: Claxton 4278067, VanVleet 2991230, Dybantsa 5142718, Murray 3936299,
Vucevic 6478, Edgecombe 5124612. News timestamps above distinguish current
evidence from older-season injuries. Keep full article text out of the repo.
