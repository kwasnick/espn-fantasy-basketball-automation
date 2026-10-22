import unittest

from scripts.lineup_payload import build_lineup_payload


class PayloadTests(unittest.TestCase):
    def setUp(self):
        self.league = {
            'scoringPeriodId': 3,
            'status': {'latestScoringPeriod': 2, 'finalScoringPeriod': 167},
            'draftDetail': {'drafted': True},
            'settings': {'rosterSettings': {'isBenchUnlimited': True,
                                          'lineupSlotCounts': {'11': 3, '12': 3}}},
            'teams': [{'id': 3, 'isTransactionLocked': False, 'roster': {'entries': [
                {'playerId': 5041935, 'lineupSlotId': 11,
                 'playerPoolEntry': {'lineupLocked': False,
                                     'player': {'eligibleSlots': [11, 12]}}}
            ]}}],
        }

    def build(self, moves=None):
        return build_lineup_payload(self.league, 3, moves or {5041935: 12}, 'test-only')

    def test_future_uses_future_roster(self):
        payload = self.build()
        self.assertEqual(payload['type'], 'FUTURE_ROSTER')
        self.assertEqual(payload['scoringPeriodId'], 3)
        self.assertEqual(payload['items'], [{'playerId': 5041935, 'type': 'LINEUP',
                                            'fromLineupSlotId': 11, 'toLineupSlotId': 12}])

    def test_current_uses_roster(self):
        self.league['scoringPeriodId'] = 2
        self.assertEqual(self.build()['type'], 'ROSTER')

    def test_past_refused(self):
        self.league['scoringPeriodId'] = 1
        with self.assertRaises(ValueError): self.build()

    def test_locked_refused(self):
        self.league['teams'][0]['roster']['entries'][0]['playerPoolEntry']['lineupLocked'] = True
        with self.assertRaises(ValueError): self.build()

    def test_protected_refused(self):
        with self.assertRaises(ValueError): self.build({1966: 12})

    def test_ineligible_refused(self):
        with self.assertRaises(ValueError): self.build({5041935: 4})

    def test_full_bench_refused(self):
        settings = self.league['settings']['rosterSettings']
        settings['isBenchUnlimited'] = False
        settings['lineupSlotCounts']['12'] = 0
        with self.assertRaises(ValueError): self.build()


if __name__ == '__main__':
    unittest.main()
