"""Synthetic fixtures only; no development-study seed sampling."""
import copy
import hashlib
import inspect
import json
import math
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from artificial_scientist import equation_discovery as ed


class EquationTests(unittest.TestCase):
    def setUp(self):
        self.config = ed.fixed_config()

    def observations(self):
        rng = random.Random(7)
        coefficients = [1., -.7, 0., 0., 1.2, 0.]
        sites = [(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(24)]
        return [(x, u, 1-.7*x+1.2*x*u) for x, u in sites], coefficients

    def test_qr_recovers_polynomial_and_independent_constant(self):
        data, true = self.observations()
        design = [ed.basis(x, u) for x, u, _ in data]
        result = ed.least_squares(design, [y for _, _, y in data], range(6))
        for actual, expected in zip(result['coefficients'], true):
            self.assertAlmostEqual(actual, expected, places=12)
        constant = ed.least_squares(design, [y for _, _, y in data], [0])
        self.assertAlmostEqual(constant['coefficients'][0], sum(y for _, _, y in data)/len(data), places=13)
        # Closed-form slope/intercept for asymmetric x values, not another QR implementation.
        xs, ys = [-2., -1., 1., 4.], [3., 1., 2., 8.]
        xm, ym = sum(xs)/4, sum(ys)/4
        slope = sum((x-xm)*(y-ym) for x, y in zip(xs, ys))/sum((x-xm)**2 for x in xs)
        linear = ed.least_squares([ed.basis(x, 0) for x in xs], ys, [0, 1])
        self.assertAlmostEqual(linear['coefficients'][1], slope)
        self.assertAlmostEqual(linear['coefficients'][0], ym-slope*xm)

    def test_overdetermined_noisy_residual_is_orthogonal(self):
        rng = random.Random(11)
        rows = [ed.basis(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(30)]
        outcomes = [1-.7*row[1]+.9*row[4]+rng.gauss(0, .1) for row in rows]
        fit = ed.least_squares(rows, outcomes, [0, 1, 4])
        residuals = [y-sum(a*b for a, b in zip(row, fit['coefficients'])) for row, y in zip(rows, outcomes)]
        self.assertGreater(fit['sse'], .01)
        for j in (0, 1, 4):
            self.assertAlmostEqual(sum(row[j]*r for row, r in zip(rows, residuals)), 0., places=12)
        # Perturbing any fitted coefficient must increase SSE by delta^2 times its column norm.
        for j in (0, 1, 4):
            changed = fit['coefficients'][:]
            changed[j] += .1
            altered_sse = sum((y-sum(a*b for a, b in zip(row, changed)))**2 for row, y in zip(rows, outcomes))
            self.assertAlmostEqual(altered_sse-fit['sse'], .01*sum(row[j]**2 for row in rows), places=12)

    def test_rank_failures_and_empty_model(self):
        design = [ed.basis(0, 0)]*4
        with self.assertRaises(ArithmeticError):
            ed.least_squares(design, [1.]*4, [1])
        with self.assertRaises(ArithmeticError):
            ed.least_squares([ed.basis(1, 1)]*4, [1.]*4, [0, 1])
        self.assertEqual(ed.least_squares(design, [1., 2., 3., 4.], [])['sse'], 30)
        with self.assertRaises(ArithmeticError):
            ed.fit_methods([(0., 0., 1.)]*24, self.config)
        committee = ed.fit_committee([(0., 0., 1.)]*24)
        self.assertEqual(len(committee['models'])+len(committee['skipped_supports']), 42)
        self.assertTrue(committee['skipped_supports'])

    def test_supports_weights_ties_and_formula(self):
        self.assertEqual(len(ed.supports()), 42)
        self.assertEqual([sum(any(j >= 3 for j in s) for s in ed.supports() if len(s) == k) for k in (1, 2, 3)], [3, 12, 19])
        data, _ = self.observations()
        committee = ed.fit_committee(data)
        self.assertEqual(committee['selected']['support'], [0, 1, 4])
        self.assertAlmostEqual(sum(m['weight'] for m in committee['models']), 1.)
        for model in committee['models']:
            self.assertAlmostEqual(model['score'], model['sse']/.05**2+len(model['support'])*math.log(24))
        model = committee['selected']
        for x, u in [(.2, -.3), (1.4, 1.1)]:
            self.assertAlmostEqual(eval(model['formula'], {'__builtins__': {}}, dict(x=x, u=u)), ed.predict(model['coefficients'], x, u))
        tied = [dict(score=1., complexity=2, support=[0, 1]), dict(score=1.+5e-13, complexity=1, support=[2]),
                dict(score=1.+4e-13, complexity=1, support=[1])]
        self.assertEqual(ed.select_model(tied)['support'], [1])

    def test_streams_world_generation_and_grids(self):
        for seed in (7, 11):
            streams = ed.shared_streams(seed, self.config)
            self.assertEqual(streams, ed.shared_streams(seed, self.config))
            self.assertEqual(len(streams['training']), 24)
            self.assertEqual(len(streams['audit']), 16)
            for i in range(0, 24, 2):
                self.assertEqual(streams['training'][i][:2], streams['training'][i+1][:2])
            # Independent draw-order check for affine coefficients and support-size sampling.
            rng = random.Random(9100001+seed)
            expected = [rng.choice([-1, 1])*rng.uniform(.5, 1.5) for _ in range(3)]
            worlds = ed.world_catalog(seed, self.config)
            self.assertEqual(worlds['affine']['coefficients'][:3], expected)
            self.assertEqual(len(worlds['sparse_quadratic']['support']), rng.choice([1, 2, 3]))
            self.assertTrue(any(j >= 3 for j in worlds['sparse_quadratic']['support']))
        grids = ed.query_grids()
        self.assertEqual(len(grids['interpolation']), 100)
        self.assertEqual(len(grids['extrapolation']), 56)
        self.assertTrue(all(max(abs(x), abs(u)) > 1 for x, u in grids['extrapolation']))

    def test_audit_is_after_fitting_and_cannot_change_fit(self):
        streams = ed.shared_streams(7, self.config)
        world = ed.world_catalog(7, self.config)['affine']
        before = copy.deepcopy(streams)
        first = ed.episode_record(7, 'affine', world, streams, self.config)
        changed = copy.deepcopy(streams)
        changed['audit'] = [(x, u, 100.) for x, u, _ in changed['audit']]
        second = ed.episode_record(7, 'affine', world, changed, self.config)
        self.assertEqual(streams, before)
        for method in ed.METHODS:
            self.assertEqual(first['methods'][method]['coefficients'], second['methods'][method]['coefficients'])
            self.assertNotEqual(first['methods'][method]['metrics']['audit_mse'], second['methods'][method]['metrics']['audit_mse'])
        self.assertEqual(list(inspect.signature(ed.fit_committee).parameters),
                         ['observations', 'sigma', 'max_terms', 'rank_tolerance', 'tie_tolerance'])
        self.assertFalse(ed.audit_predictions([0.]*16, [.1]*16, .05)['audit_rejected'])
        self.assertTrue(ed.audit_predictions([0.]*16, [.100001]*16, .05)['audit_rejected'])
        # Exact structural recovery and real-valued estimation error are different quantities.
        metrics = first['methods']['linear']['metrics']
        self.assertTrue(metrics['exact_support'])
        self.assertGreater(metrics['coefficient_rmse'], 0)
        self.assertFalse(metrics['false_inclusion'])

    def synthetic_summary(self):
        cells = []
        for world in ed.WORLDS:
            counts = dict(exact_support=14, false_inclusion=6, nonzero_selection=8,
                          audit_rejected=16 if world in ('sine', 'exponential') else 2)
            cells.append(dict(world=world, method='sparse', n=20,
                              proportions={key:dict(count=value) for key, value in counts.items()}))
        return dict(completed_keys=[[seed, world] for seed in self.config['seeds'] for world in ed.WORLDS], cells=cells)

    def test_gates_thresholds_completeness_and_wilson(self):
        summary = self.synthetic_summary()
        result = ed.decision(summary, self.config, True)
        self.assertTrue(result['recovery_pass'])
        self.assertTrue(result['adequacy_pass'])
        self.assertFalse(ed.decision(summary, self.config, False)['recovery_pass'])
        for index, key, value in [(0, 'exact_support', 13), (1, 'false_inclusion', 7), (4, 'nonzero_selection', 9)]:
            altered = copy.deepcopy(summary)
            altered['cells'][index]['proportions'][key]['count'] = value
            self.assertFalse(ed.decision(altered, self.config, True)['recovery_pass'])
        for index in range(5):
            altered = copy.deepcopy(summary)
            altered['cells'][index]['proportions']['audit_rejected']['count'] = 15 if index in (2, 3) else 3
            self.assertFalse(ed.decision(altered, self.config, True)['adequacy_pass'])
        for keys in [summary['completed_keys'][:-1], summary['completed_keys']+[summary['completed_keys'][0]]]:
            self.assertFalse(ed.decision(dict(summary, completed_keys=keys), self.config, True)['complete'])
        low, high = ed.wilson(10, 20)
        self.assertAlmostEqual(low+high, 1.)
        self.assertLess(low, .5)
        self.assertGreater(high, .5)

    def test_smoke_provenance_resource_and_scope(self):
        # Synthetic artifact fixture only: never run the smoke study in author tests.
        with tempfile.TemporaryDirectory(dir=ed.ROOT/'results/runs', prefix='equation_discovery_fixture_') as directory:
            path = Path(directory)
            for name in ('config.json', 'episodes.jsonl', 'summary.json', 'decision.json'):
                (path/name).write_text('{}\n')
            meta = dict(status='completed', mode='smoke', completed_episodes=5, sources_unchanged=True,
                        source_sha256={'a':'b'}, config_sha256='c', elapsed_seconds=.01,
                        artifact_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in path.iterdir()}, artifact_bytes=0)
            def save():
                for _ in range(20):
                    text = json.dumps(meta)
                    size = sum(p.stat().st_size for p in path.iterdir() if p.name != 'metadata.json')+len(text.encode())
                    if size == meta['artifact_bytes']:
                        (path/'metadata.json').write_text(text)
                        return
                    meta['artifact_bytes'] = size
                self.fail('metadata fixture failed to stabilize')
            save()
            ed.verify_smoke(path, 'c', {'a':'b'}, self.config)
            with self.assertRaises(FileExistsError):
                ed.output_scope(path)
            with self.assertRaises(ValueError):
                ed.output_scope(ed.ROOT/'wrong_place')
            meta['elapsed_seconds'] = 3.
            save()
            with self.assertRaises(RuntimeError):
                ed.verify_smoke(path, 'c', {'a':'b'}, self.config)
            meta['elapsed_seconds'] = .01
            save()
            with self.assertRaises(RuntimeError):
                ed.verify_smoke(path, 'c', {'a':'b'}, dict(self.config, smoke_projection_limit_bytes=1))
            with self.assertRaises(ValueError):
                ed.verify_smoke(path, 'changed', {'a':'b'}, self.config)
            (path/'summary.json').write_text('tampered')
            with self.assertRaises(ValueError):
                ed.verify_smoke(path, 'c', {'a':'b'}, self.config)

    def test_baseline_failure_preserves_partial_and_blocks_gates(self):
        # Patch sampling entirely: fixture streams/worlds use only synthetic seed7.
        with tempfile.TemporaryDirectory(dir=ed.ROOT/'results/runs', prefix='equation_discovery_fixture_') as temp:
            parent = Path(temp)
            output = parent/'fresh'
            config_path = parent/'config.json'
            config_path.write_text(json.dumps(self.config))
            with patch.object(ed, 'output_scope', return_value=output), \
                 patch.object(ed, 'world_catalog', return_value=ed.world_catalog(7, self.config)), \
                 patch.object(ed, 'shared_streams', return_value=dict(training=[(0., 0., 0.)]*24, audit=[(0., 0., 0.)]*16)):
                with self.assertRaises(ArithmeticError):
                    ed.run(config_path, output, smoke=True)
            meta = json.loads((output/'metadata.json').read_text())
            gates = json.loads((output/'decision.json').read_text())
            self.assertEqual(meta['status'], 'failed_partial')
            self.assertEqual(meta['completed_episodes'], 0)
            self.assertFalse(gates['recovery_pass'])
            self.assertFalse(gates['adequacy_pass'])


if __name__ == '__main__':
    unittest.main()
