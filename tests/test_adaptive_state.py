import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from artificial_scientist.adaptive_state import (
    AdaptiveContext, SparsePredictor, SparseMixture, diagnostic, run, simulate)
from artificial_scientist.sequence_worlds import ContextPredictor

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'experiments/adaptive_state_v1.json').read_text())


class FixedExpert:
    def __init__(self, p, lag):
        self.p, self.lags = p, (1, lag)
    def predict(self):
        return self.p
    def update(self, outcome):
        pass
    def storage(self):
        return 10


class AdaptiveStateTests(unittest.TestCase):
    def test_sparse_context_ignores_intervening_bits(self):
        a, b = SparsePredictor((1, 4)), SparsePredictor((1, 4))
        a.history.extend([0, 1, 1, 1])
        b.history.extend([0, 0, 0, 1])
        self.assertEqual(a.context(), (1, 0))
        self.assertEqual(a.context(), b.context())
        b.history[0] = 1
        self.assertNotEqual(a.context(), b.context())
        self.assertEqual(SparsePredictor((1, 4)).context(), (-1, -1))

    def test_trigger_full_window_next_prediction_tie_and_once(self):
        m = AdaptiveContext(window=4, every=2, threshold=1)
        m.models = [FixedExpert(.5, 1)] + [FixedExpert(.9, k) for k in range(2, 6)]
        for _ in range(3):
            self.assertEqual(m.predict(), .5)
            self.assertIsNone(m.update(1))
        self.assertEqual(m.predict(), .5)  # fourth outcome still uses base
        event = m.update(1)
        self.assertEqual(event['observed_tick'], 3)
        self.assertEqual(event['effective_tick'], 4)
        self.assertEqual(event['selected_lag'], 2)
        self.assertAlmostEqual(event['window_gain'], 4 * math.log(1.8))
        self.assertEqual(m.predict(), .9)
        for _ in range(20):
            self.assertIsNone(m.update(1))
        self.assertTrue(all(len(g) == 4 for g in m.gains))
        self.assertEqual(m.storage(), 50 + 16 + 7)

    def test_strict_threshold_and_preupdate_evidence(self):
        m = AdaptiveContext(window=4, every=2, threshold=0)
        m.models = [FixedExpert(.5, k) for k in range(1, 6)]
        for _ in range(4):
            self.assertIsNone(m.update(1))
        self.assertEqual(m.active, 0)  # gain == threshold must not activate
        real = AdaptiveContext(window=4, every=2)
        ps = [model.predict() for model in real.models]
        real.update(1)
        for gain, p in zip(real.gains, ps[1:]):
            self.assertAlmostEqual(gain[-1], math.log(p / ps[0]))

    def test_monitor_only_exact_base_and_total_storage(self):
        base, monitor = ContextPredictor(1), AdaptiveContext(enabled=False)
        for y in [0, 1, 0, 0, 1, 1, 1] * 40:
            self.assertEqual(base.predict(), monitor.predict())
            self.assertEqual(monitor.storage(), sum(m.storage() for m in monitor.models) + 512 + 7)
            base.update(y)
            self.assertIsNone(monitor.update(y))
        self.assertEqual(monitor.active, 0)
        self.assertGreater(monitor.checks, 0)

    def test_prefix_causality_and_repeatable_predict(self):
        a = AdaptiveContext(window=8, every=4, threshold=.1)
        for y in [1, 0, 1, 1] * 10:
            before = copy.deepcopy(a.__dict__)
            self.assertEqual(a.predict(), a.predict())
            self.assertEqual(a.observed, before['observed'])
            a.update(y)
        b = copy.deepcopy(a)
        self.assertEqual(a.predict(), b.predict())
        # Only past outcomes are in the API; future continuation cannot change the current prediction.
        current = a.predict()
        a.update(0)
        b.update(1)
        self.assertTrue(0 < current < 1)

    def test_pairing_prefix_and_monitor_ablation_in_runner(self):
        config = dict(CONFIG, steps=32, change_at=16, seeds=[0], check_every=8, gain_window=8)
        rows, summary, events, timings = simulate(config)
        again, summary2, events2, _ = simulate(config)
        self.assertEqual((rows, summary, events), (again, summary2, events2))
        self.assertEqual(len(rows), 32 * 4 * 6)
        by = {(r['condition'], r['tick'], r['baseline']): r for r in rows}
        for t in range(32):
            for c in ('stable', 'parameter', 'noise', 'structural'):
                self.assertEqual(by[c,t,'monitor_only']['probability'], by[c,t,'order1']['probability'])
                self.assertEqual(len({r['outcome'] for r in rows if r['tick']==t and r['condition']==c}), 1)
                if t < 16:
                    self.assertEqual(by[c,t,'adaptive']['probability'], by['stable',t,'adaptive']['probability'])
        self.assertEqual(len(timings), 24)
        self.assertTrue(all(r['probability'] == .5 for r in rows if r['tick']==0))

    def test_sparse_mixture_normalization_and_all_components(self):
        m = SparseMixture()
        for y in [1,0,0,1] * 10:
            m.update(y)
            self.assertAlmostEqual(sum(m.weights), 1)
            self.assertEqual(m.storage(), 5 + sum(x.storage() for x in m.models))

    def test_scope_provenance_and_reserved_seeds(self):
        small = dict(CONFIG, steps=32, change_at=16, seeds=[0], check_every=8)
        with self.assertRaises(ValueError):
            simulate(dict(small, seeds=[1000]))
        with self.assertRaises(ValueError):
            simulate(dict(small, gain_window=100000))
        with tempfile.TemporaryDirectory(dir=ROOT / 'results') as tmp:
            p = Path(tmp)
            config = p / 'config.json'
            config.write_text(json.dumps(small))
            run(config, p/'out')
            meta = json.loads((p/'out/metadata.json').read_text())
            self.assertIn('artificial_scientist/adaptive_state.py', meta['source_sha256'])
            self.assertEqual(len(meta['predictions_sha256']), 64)
            with self.assertRaises(FileExistsError):
                run(config, p/'out')
            with self.assertRaises(ValueError):
                run(config, ROOT.parent/'outside')
