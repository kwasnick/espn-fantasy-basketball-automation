"""Build lineup-only ESPN transactions; performs no network calls.

See docs/lineup-editing.md before executing a payload. Never log the result:
memberId contains the authenticated user's SWID.
"""

PROTECTED_PLAYERS = {1966, 3975, 3202, 6450}


def build_lineup_payload(league, team_id, moves, member_id):
    """Use a fresh mRoster/mSettings response for the requested scoring period.

    moves maps player IDs to destination slot IDs. This conservative helper
    refuses protected players, locks, pending transactions and past periods.
    Caller must separately verify game timing and snapshot/read back changes.
    """
    period = league['scoringPeriodId']
    current = league['status']['latestScoringPeriod']
    if not current <= period <= league['status']['finalScoringPeriod']:
        raise ValueError('Scoring period is past or outside the season')
    if league.get('draftDetail', {}).get('drafted') is not True:
        raise ValueError('Only completed-draft leagues are supported')
    team = next(t for t in league['teams'] if t['id'] == team_id)
    if team.get('isTransactionLocked'):
        raise ValueError('Team transactions are locked')
    entries = {e['playerId']: e for e in team['roster']['entries']}
    if not moves:
        raise ValueError('No moves supplied')
    items = []
    for player_id, destination in moves.items():
        if player_id in PROTECTED_PLAYERS:
            raise ValueError('Protected player: stop for explicit user approval')
        entry = entries[player_id]
        pool = entry['playerPoolEntry']
        if pool.get('lineupLocked') is not False or entry.get('pendingTransactionIds'):
            raise ValueError('Player locked, lock unknown, or transaction pending')
        if destination not in pool['player']['eligibleSlots']:
            raise ValueError('Ineligible destination')
        if destination == entry['lineupSlotId']:
            raise ValueError('Move does not change slot')
        items.append({'playerId': player_id, 'type': 'LINEUP',
                      'fromLineupSlotId': entry['lineupSlotId'],
                      'toLineupSlotId': destination})
    settings = league['settings']['rosterSettings']
    counts = {}
    for player_id, entry in entries.items():
        slot = moves.get(player_id, entry['lineupSlotId'])
        counts[slot] = counts.get(slot, 0) + 1
    for slot, count in counts.items():
        if slot == 12 and settings.get('isBenchUnlimited'):
            continue
        if count > settings['lineupSlotCounts'].get(str(slot), 0):
            raise ValueError('Destination lineup exceeds slot capacity')
    return {'isLeagueManager': False, 'teamId': team_id,
            'type': 'FUTURE_ROSTER' if period > current else 'ROSTER',
            'memberId': member_id, 'scoringPeriodId': period,
            'executionType': 'EXECUTE', 'items': items}
