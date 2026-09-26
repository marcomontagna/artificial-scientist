"""Public tool semantics and evaluator-world invariants; no learner runs."""
from dataclasses import FrozenInstanceError, fields
import math
import unittest

from artificial_scientist.lab_api import Action, Observation, Transition
from artificial_scientist.lab_world import make_world


class PublicToolsTest(unittest.TestCase):
    def test_public_records_are_frozen_and_have_no_hidden_channels(self):
        self.assertEqual([f.name for f in fields(Observation)], ['tick', 'x', 'y'])
        a = Action('push', angle=math.pi, magnitude=0.5)
        self.assertEqual(a.cost, 1)
        with self.assertRaises(FrozenInstanceError):
            a.kind = 'reset'
        o = Observation(0, 0., 0.)
        self.assertEqual(Transition(o, a, o).action, a)

    def test_reject_invalid_arguments(self):
        bad = [dict(kind='teleport'), dict(kind='wait', ticks=0),
               dict(kind='wait', ticks=9), dict(kind='wait', ticks=True),
               dict(kind='observe', ticks=2), dict(kind='push', magnitude=-.1),
               dict(kind='push', magnitude=1.1), dict(kind='push', magnitude=True),
               dict(kind='push', angle=float('nan')),
               dict(kind='push', magnitude=float('inf')),
               dict(kind='reset', magnitude=.1)]
        for args in bad:
            with self.subTest(args=args), self.assertRaises(ValueError):
                Action(**args)
        self.assertEqual(Action('reset').cost, 8)
        self.assertEqual(Action('wait', ticks=8).cost, 8)

    def test_determinism_and_initial_not_a_free_repeated_sensor(self):
        for variant in ('development', 'challenge', 'noise'):
            a, b = make_world(7, variant), make_world(7, variant)
            self.assertIs(a.initial, a.initial)
            self.assertEqual(a.initial, b.initial)
            for action in (Action('push', magnitude=1), Action('wait', ticks=3),
                           Action('reset'), Action('observe')):
                self.assertEqual(a.step(action), b.step(action))
            self.assertEqual(a.consumed, 13)

    def test_wait_is_same_timeline_as_individual_observations(self):
        for variant in ('development', 'challenge', 'noise'):
            a, b = make_world(11, variant), make_world(11, variant)
            push = Action('push', angle=.8, magnitude=.6)
            a.step(push); b.step(push)
            batched = a.step(Action('wait', ticks=8))
            for _ in range(8):
                single = b.step(Action('observe'))
            self.assertEqual(batched, single)
            self.assertEqual(a.consumed, b.consumed)

    def test_reset_rehomes_without_rewinding_noise_or_law(self):
        for variant in ('development', 'challenge', 'noise'):
            moving, idle = make_world(7, variant), make_world(7, variant)
            moving.step(Action('push', magnitude=1))
            idle.step(Action('observe'))
            a = moving.step(Action('reset')); b = idle.step(Action('reset'))
            self.assertEqual(a, b)
            self.assertEqual(a.tick, 9)
            self.assertNotEqual((a.x, a.y), (moving.initial.x, moving.initial.y))
            self.assertEqual(moving.step(Action('push', angle=.5, magnitude=.5)),
                             idle.step(Action('push', angle=.5, magnitude=.5)))

    def test_budget_and_invalid_step_leave_state_unchanged(self):
        a, b = make_world(11), make_world(11)
        with self.assertRaises(ValueError):
            a.step({'kind': 'push'})
        self.assertEqual(a.consumed, 0)
        for _ in range(9):
            a.step(Action('wait', ticks=8)); b.step(Action('wait', ticks=8))
        a.step(Action('wait', ticks=7)); b.step(Action('wait', ticks=7))
        with self.assertRaises(ValueError):
            a.step(Action('reset'))
        self.assertEqual(a.consumed, 79)
        self.assertEqual(a.step(Action('observe')), b.step(Action('observe')))
        with self.assertRaises(ValueError):
            a.step(Action('observe'))
        self.assertEqual(a.consumed, 80)

    def test_action_effect_persistence_and_noise_control(self):
        for variant in ('development', 'challenge'):
            pushed, idle = make_world(7, variant), make_world(7, variant)
            p = pushed.step(Action('push', magnitude=1)); q = idle.step(Action('observe'))
            first = p.x-q.x
            self.assertGreater(first, 0)
            p = pushed.step(Action('observe')); q = idle.step(Action('observe'))
            self.assertGreater(p.x-q.x, first)
        pushed, idle = make_world(7, 'noise'), make_world(7, 'noise')
        self.assertEqual(pushed.step(Action('push', magnitude=1)), idle.step(Action('observe')))

    def test_evaluator_inputs_validated(self):
        with self.assertRaises(ValueError):
            make_world(True)
        with self.assertRaises(ValueError):
            make_world(7, 'unknown')


if __name__ == '__main__':
    unittest.main()
