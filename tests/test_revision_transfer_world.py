"""Synthetic evaluator tests only. No learner, fitting, or study seed execution."""
import math
import unittest

from artificial_scientist.lab_api import Action
from artificial_scientist.revision_transfer_world import make_transfer_world


class TransferWorldTests(unittest.TestCase):
    def test_repeatability_and_wait_tick_equivalence(self):
        for variant in ('transfer_a','transfer_b'):
            a,b=make_transfer_world(7,variant),make_transfer_world(7,variant)
            self.assertEqual(a.initial,b.initial)
            self.assertIs(a.initial,a.initial)
            push=Action('push',angle=.61,magnitude=.8)
            self.assertEqual(a.step(push),b.step(push))
            for _ in range(2):
                batched=a.step(Action('wait',ticks=8))
                for _ in range(8):single=b.step(Action('observe'))
                self.assertEqual(batched,single)
            self.assertEqual(a.consumed,17)

    def test_reset_rehomes_hidden_memory_without_rewinding_noise(self):
        for variant in ('transfer_a','transfer_b'):
            a,b=make_transfer_world(7,variant),make_transfer_world(7,variant)
            a.step(Action('push',angle=.4,magnitude=1.));b.step(Action('observe'))
            reset=a.step(Action('reset'))
            self.assertEqual(reset,b.step(Action('reset')))
            self.assertEqual(reset.tick,9)
            self.assertNotEqual((reset.x,reset.y),(a.initial.x,a.initial.y))
            for _ in range(16):
                self.assertEqual(a.step(Action('observe')),b.step(Action('observe')))

    def test_atomic_budget_rejection_and_bounded_finite_dynamics(self):
        for variant in ('transfer_a','transfer_b'):
            a,b=make_transfer_world(7,variant),make_transfer_world(7,variant)
            with self.assertRaises(ValueError):a.step(None)
            for i in range(73):
                action=Action('push',angle=(i%5)*.73,magnitude=1.)
                self.assertEqual(a.step(action),b.step(action))
            with self.assertRaises(ValueError):a.step(Action('reset'))
            for _ in range(7):
                o=a.step(Action('observe'))
                self.assertEqual(o,b.step(Action('observe')))
                self.assertTrue(math.isfinite(o.x) and math.isfinite(o.y))
                self.assertLess(abs(o.x)+abs(o.y),1000.)
            self.assertEqual(a.consumed,80)
            with self.assertRaises(ValueError):a.step(Action('observe'))

    def test_simultaneous_vector_updates(self):
        a,b=make_transfer_world(7,'transfer_b'),make_transfer_world(7,'transfer_b')
        # Evaluator-only state fixture checks ordering, not learner performance.
        a._vx=1.;a._vy=2.
        p,q=a.step(Action('observe')),b.step(Action('observe'))
        self.assertAlmostEqual(p.x-q.x,.54+.16*2)
        self.assertAlmostEqual(p.y-q.y,.61*2-.12)

    def test_delay_reads_before_appending_current_input(self):
        for variant,ownlag,crosslag,owncoefficient,crosscoefficient in (
                ('transfer_a',3,6,.18,.17),('transfer_b',4,9,.24,.26)):
            a,b=make_transfer_world(7,variant),make_transfer_world(7,variant)
            a._inputs[-ownlag]=(1.,0.)
            a._inputs[-crosslag]=(1.,0.)
            p,q=a.step(Action('observe')),b.step(Action('observe'))
            self.assertAlmostEqual(p.x-q.x,owncoefficient)
            self.assertAlmostEqual(p.y-q.y,crosscoefficient)
            self.assertEqual(a._inputs[-1],(0.,0.))

    def test_factory_validation(self):
        for seed,variant in ((True,'transfer_a'),(7,None),(7,'control')):
            with self.assertRaises(ValueError):make_transfer_world(seed,variant)


if __name__=='__main__':unittest.main()
