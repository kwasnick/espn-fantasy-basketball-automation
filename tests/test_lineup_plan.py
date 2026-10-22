import unittest
from scripts.lineup_plan import plan_lineup


def entry(pid, slot, eligible, locked=False):
    return {'playerId': pid, 'lineupSlotId': slot, 'playerPoolEntry': {
        'lineupLocked': locked, 'player': {'eligibleSlots': eligible, 'injuryStatus': 'ACTIVE'}}}


class PlannerTests(unittest.TestCase):
    def league(self, entries):
        return {'settings': {'rosterSettings': {'isBenchUnlimited': True,
                'lineupSlotCounts': {'0': 1, '4': 1, '11': 1, '12': 3}}},
                'teams': [{'id': 3, 'roster': {'entries': entries}}]}

    def test_global_assignment_frees_utility_for_center(self):
        d = self.league([entry(1, 11, [0, 11, 12]), entry(2, 4, [4, 11, 12]),
                         entry(3, 12, [4, 11, 12])])
        slots, _, score = plan_lineup(d, 3, {1: 40, 2: 35, 3: 30})
        self.assertEqual(slots, {1: 0, 2: 4, 3: 11})
        self.assertEqual(score, 105)

    def test_locked_player_cannot_be_reassigned(self):
        d = self.league([entry(1, 11, [0, 11, 12], True),
                         entry(2, 4, [4, 11, 12]), entry(3, 12, [4, 11, 12])])
        slots, _, score = plan_lineup(d, 3, {1: 40, 2: 35, 3: 30})
        self.assertEqual(slots[1], 11)
        self.assertEqual(slots[3], 12)
        self.assertEqual(score, 75)

    def test_equal_scores_preserve_existing_slots(self):
        d = self.league([entry(1, 11, [0, 11, 12])])
        _, moves, _ = plan_lineup(d, 3, {1: 0})
        self.assertEqual(moves, {})


if __name__ == '__main__':
    unittest.main()
