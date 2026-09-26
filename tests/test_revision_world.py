"""Evaluator-only deterministic fixtures; no learners or study seeds."""
import math
import unittest

from artificial_scientist.lab_api import Action
from artificial_scientist.lab_world import make_world
from artificial_scientist.revision_world import make_revision_world


class RevisionWorldTest(unittest.TestCase):
    def test_control_is_frozen_development(self):
        a, b = make_revision_world(7), make_world(7, 'development')
        self.assertEqual(a.initial, b.initial)
        for action in (Action('push', angle=.4, magnitude=.8),
                       Action('wait', ticks=8), Action('reset'), Action('observe')):
            self.assertEqual(a.step(action), b.step(action))

    def test_variants_repeat_and_wait_batching_preserves_timeline(self):
        for variant in ('control', 'challenge', 'stress'):
            a, b = make_revision_world(11, variant), make_revision_world(11, variant)
            self.assertEqual(a.initial, b.initial)
            self.assertIs(a.initial, a.initial)
            self.assertEqual(a.step(Action('push', magnitude=1)), b.step(Action('push', magnitude=1)))
            for _ in range(2):
                after = a.step(Action('wait', ticks=8))
                for _ in range(8):
                    single = b.step(Action('observe'))
                self.assertEqual(after, single)
            self.assertEqual(a.consumed, 17)

    def test_reset_clears_all_physical_state_but_not_clock_or_noise(self):
        for variant in ('control', 'challenge', 'stress'):
            a, b = make_revision_world(7, variant), make_revision_world(7, variant)
            a.step(Action('push', magnitude=1)); b.step(Action('observe'))
            after = a.step(Action('reset'))
            self.assertEqual(after, b.step(Action('reset')))
            self.assertEqual(after.tick, 9)
            self.assertNotEqual((after.x, after.y), (a.initial.x, a.initial.y))
            for _ in range(13):
                self.assertEqual(a.step(Action('observe')), b.step(Action('observe')))

    def test_rejected_actions_and_overbudget_reset_are_atomic(self):
        for variant in ('control', 'challenge', 'stress'):
            a, b = make_revision_world(11, variant), make_revision_world(11, variant)
            with self.assertRaises(ValueError):
                a.step(None)
            for _ in range(9):
                a.step(Action('wait', ticks=8)); b.step(Action('wait', ticks=8))
            a.step(Action('push', magnitude=1)); b.step(Action('push', magnitude=1))
            with self.assertRaises(ValueError):
                a.step(Action('reset'))
            self.assertEqual(a.consumed, 73)
            for _ in range(7):
                self.assertEqual(a.step(Action('observe')), b.step(Action('observe')))
            with self.assertRaises(ValueError):
                a.step(Action('observe'))
            self.assertEqual(a.consumed, 80)

    def test_challenge_has_unobserved_cross_component_response(self):
        a, b = make_revision_world(7, 'challenge'), make_revision_world(7, 'challenge')
        a.step(Action('push', magnitude=1)); b.step(Action('observe'))
        p, q = a.step(Action('observe')), b.step(Action('observe'))
        self.assertAlmostEqual(p.y-q.y, .22*.38)
        self.assertAlmostEqual(p.x-q.x, .38*(1+.72))

    def test_delayed_stress_response_and_finite_full_budget(self):
        a, b = make_revision_world(7, 'stress'), make_revision_world(7, 'stress')
        a.step(Action('push', magnitude=1)); b.step(Action('observe'))
        for _ in range(10):
            p, q = a.step(Action('observe')), b.step(Action('observe'))
            self.assertAlmostEqual(p.y-q.y, 0)
        p, q = a.step(Action('observe')), b.step(Action('observe'))
        self.assertAlmostEqual(p.y-q.y, .22)
        for variant in ('control', 'challenge', 'stress'):
            world = make_revision_world(11, variant)
            for _ in range(80):
                o = world.step(Action('push', angle=.7, magnitude=1))
                self.assertTrue(math.isfinite(o.x) and math.isfinite(o.y))
                self.assertLess(abs(o.x)+abs(o.y), 500)

    def test_evaluator_parameters_validate(self):
        for seed, variant in ((True, 'control'), (7, 'unknown'), (7, None)):
            with self.assertRaises(ValueError):
                make_revision_world(seed, variant)


if __name__ == '__main__':
    unittest.main()
