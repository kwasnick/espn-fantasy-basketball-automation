"""Pure daily points-lineup optimizer. No network or write operations.

Maximizes supplied per-player daily expected points, breaking ties by fewest
slot changes. Fixes locked/pending players and existing IR assignments. The
caller supplies news-adjusted values and verified IR candidates explicitly.
"""
from functools import lru_cache


def plan_lineup(league, team_id, expected_points, ir_ids=()):
    team = next(t for t in league['teams'] if t['id'] == team_id)
    entries = team['roster']['entries']
    settings = league['settings']['rosterSettings']
    capacities = {int(k): v for k, v in settings['lineupSlotCounts'].items() if v}
    if settings.get('isBenchUnlimited'):
        capacities[12] = len(entries)
    slot_ids = tuple(sorted(capacities))
    initial = tuple(capacities[s] for s in slot_ids)

    @lru_cache(None)
    def solve(index, remaining):
        if index == len(entries):
            return (0.0, 0, ())
        e = entries[index]
        pid, old = e['playerId'], e['lineupSlotId']
        pool = e['playerPoolEntry']
        if pool.get('lineupLocked') is not False or e.get('pendingTransactionIds'):
            allowed = [old]
        elif pid in ir_ids:
            if pool['player'].get('injuryStatus') != 'OUT':
                raise ValueError('IR candidate is not OUT')
            allowed = [13]
        elif old == 13:
            allowed = [13]
        else:
            allowed = [s for s in pool['player']['eligibleSlots'] if s != 13]
        best = None
        for slot in slot_ids:
            j = slot_ids.index(slot)
            if slot not in allowed or remaining[j] <= 0:
                continue
            rest = list(remaining); rest[j] -= 1
            tail = solve(index + 1, tuple(rest))
            if tail is None:
                continue
            value = expected_points.get(pid, 0) if slot not in (12, 13) else 0
            candidate = (round(value + tail[0], 6), tail[1] - (slot != old), (slot,) + tail[2])
            if best is None or candidate[:2] > best[:2]:
                best = candidate
        return best

    result = solve(0, initial)
    if result is None:
        raise ValueError('No legal assignment under current locks/capacities')
    desired = {e['playerId']: s for e, s in zip(entries, result[2])}
    moves = {e['playerId']: desired[e['playerId']] for e in entries
             if desired[e['playerId']] != e['lineupSlotId']}
    return desired, moves, result[0]
