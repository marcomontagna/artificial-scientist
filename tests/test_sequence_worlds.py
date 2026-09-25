import json
import math
import tempfile
import unittest
from pathlib import Path

from artificial_scientist.sequence_worlds import (
    CONDITIONS, ContextPredictor, OrderMixture, generate, probability_one, run, simulate)


class SequenceWorldTests(unittest.TestCase):
    def test_shared_prefix_deterministic_replay_and_switch(self):
        for condition in CONDITIONS:
            stream, lag = generate(7, condition, 100, 50)
            self.assertEqual((stream, lag), generate(7, condition, 100, 50))
            self.assertEqual(stream[:50], generate(7, 'stable', 100, 50)[0][:50])
        # Reversed probability and a scripted RNG-independent rule boundary.
        self.assertAlmostEqual(probability_one([1]*5, 'parameter', False, 3), .8)
        self.assertAlmostEqual(probability_one([1]*5, 'parameter', True, 3), .2)

    def test_structural_requires_history(self):
        for lag in range(2, 6):
            a, b = [0]*5, [0]*5
            b[-lag] = 1
            self.assertEqual(a[-1], b[-1])
            self.assertAlmostEqual(probability_one(a, 'structural', True, lag), .2)
            self.assertAlmostEqual(probability_one(b, 'structural', True, lag), .8)
            for condition in ('stable', 'parameter', 'noise'):
                self.assertEqual(probability_one(a, condition, True, lag),
                                 probability_one(b, condition, True, lag))

    def test_data_discount_not_prior_and_preupdate_context(self):
        m = ContextPredictor(1, .5)
        m.update(1)  # sentinel context
        self.assertEqual(m.predict(), .5)  # unseen context (1,)
        m.update(1)
        self.assertAlmostEqual(m.predict(), 2/3)
        m.update(1)
        self.assertEqual(m.counts[(1,)], [1.5, 0.0])
        self.assertAlmostEqual(m.predict(), 2.5/3.5)

    def test_mixture_likelihood_update_and_all_storage(self):
        m = OrderMixture()
        for y in [0,1,1,0,0,0,1]*8:
            ps = [model.predict() for model in m.models]
            likelihood = [p if y else 1-p for p in ps]
            evidence = sum(w*p for w,p in zip(m.weights, likelihood))
            expected = [.99*w*p/evidence+.002 for w,p in zip(m.weights, likelihood)]
            m.update(y)
            for a,b in zip(m.weights, expected):
                self.assertAlmostEqual(a,b)
            self.assertAlmostEqual(sum(m.weights),1)
            self.assertEqual(m.storage(), 5+sum(x.storage() for x in m.models))

    def test_predictions_before_outcome_and_paired_streams(self):
        rows, _ = simulate({'steps': 20, 'change_at': 10, 'seeds': [0]})
        for condition in CONDITIONS:
            subset = [r for r in rows if r['condition']==condition]
            for row in subset[:3]:
                self.assertEqual(row['probability'], .5)
                self.assertAlmostEqual(row['log_loss'], math.log(2))
            for t in range(20):
                group = [r for r in subset if r['tick']==t]
                self.assertEqual(len({r['outcome'] for r in group}),1)
                self.assertEqual({r['phase'] for r in group}, {'before' if t<10 else 'after'})

    def test_reserve_test_seeds(self):
        with self.assertRaises(ValueError):
            simulate({'steps': 20, 'change_at': 10, 'seeds': [1000]})

    def test_artifacts_scope_and_overwrite(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root/'results') as tmp:
            tmp=Path(tmp)
            config=tmp/'config.json'
            config.write_text(json.dumps({'steps':20,'change_at':10,'seeds':[0]}))
            out=tmp/'output'
            run(config,out)
            self.assertTrue((out/'predictions.csv').exists())
            self.assertEqual(len(json.loads((out/'summary.json').read_text())),24)
            with self.assertRaises(FileExistsError):
                run(config,out)
            with self.assertRaises(ValueError):
                run(config,root.parent/'forbidden-output')
