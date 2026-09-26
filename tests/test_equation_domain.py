"""Independent numerical and synthetic-seed fixtures; no study execution."""
import copy
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from artificial_scientist import equation_domain as d
from artificial_scientist import equation_discovery as ed


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.config = d.fixed_config()

    def test_triangular_covariance_and_whitening(self):
        # R=[[2,1],[0,3]] implies inverse Gram [[5/18,-1/18],[-1/18,1/9]].
        v = d.predictive_covariance([[2., 1.], [0., 3.]], [[1., 0.], [0., 1.]], 1.)
        for actual, expected in zip([v[0][0], v[0][1], v[1][1]], [23/18, -1/18, 10/9]):
            self.assertAlmostEqual(actual, expected, places=14)
        lower = d.cholesky([[4., 2.], [2., 3.]])
        self.assertEqual(lower[0][0], 2.)
        self.assertAlmostEqual(lower[1][1], math.sqrt(2))
        self.assertAlmostEqual(d.quadratic_form(lower, [2., 3.]), 3.)
        with self.assertRaises(ArithmeticError):
            d.cholesky([[1., 2.], [2., 1.]])
        with self.assertRaises(ArithmeticError):
            d.training_r([ed.basis(0., 0.)]*24)

    def test_qr_matches_gram_matrix(self):
        prepared = d.prepare_design(7, self.config)
        design = prepared['design']
        r = d.training_r(design)
        for i in range(6):
            for j in range(6):
                self.assertAlmostEqual(sum(row[i]*row[j] for row in design), sum(row[i]*row[j] for row in r), places=12)

    def test_central_tail_and_independent_power_references(self):
        self.assertEqual(d.log_survival(0.), 0.)
        self.assertEqual(d.log_survival(-1e-12), 0.)
        with self.assertRaises(ArithmeticError):
            d.log_survival(-1e-5)
        # At Q=2, direct finite rational sum times e^-1.
        self.assertAlmostEqual(math.exp(d.log_survival(2.)), math.exp(-1)*sum(1/math.factorial(k) for k in range(8)), places=14)
        critical = d.critical_value()
        self.assertAlmostEqual(critical, 26.29622760486423952627, delta=1e-12)
        for noncentrality, expected in [(0., .05), (1., .07406486167760769397),
                                      (10., .44607785423605570499), (30., .96158288118242562139)]:
            self.assertAlmostEqual(d.theoretical_power(noncentrality, critical), expected, delta=1e-12)
        values = [d.theoretical_power(x, critical) for x in (0., 1., 10., 30., 100., 1000.)]
        self.assertEqual(values, sorted(values))
        self.assertAlmostEqual(d.gamma_cdf_integer(1, 2.), 1-math.exp(-2), places=14)
        with self.assertRaises(ArithmeticError):
            d.theoretical_power(-1.)

    def test_paired_domains_budget_and_frozen_predictions(self):
        audits = d.audit_streams(11, self.config)
        for local, wide in zip(audits['local'], audits['wide']):
            self.assertEqual(wide, (2*local[0], 2*local[1], local[2]))
        prepared = d.prepare_design(7, self.config)
        world = ed.world_catalog(7, ed.fixed_config())['affine']
        first = d.episode_record(7, 'affine', world, prepared, self.config, d.critical_value())
        changed = copy.deepcopy(prepared)
        changed['arms']['local']['data'] = [(x, u, 10.) for x, u, _ in changed['arms']['local']['data']]
        second = d.episode_record(7, 'affine', world, changed, self.config, d.critical_value())
        self.assertEqual(first['fitted'], second['fitted'])
        self.assertEqual(first['arms']['local']['predictions'], second['arms']['local']['predictions'])
        self.assertNotEqual(first['arms']['local']['q'], second['arms']['local']['q'])
        self.assertEqual(first['unique_observations'], len(first['training'])+sum(len(a['observations']) for a in first['arms'].values()))
        self.assertEqual(first['unique_observations'], 56)
        self.assertEqual(first['observations_per_arm'], 40)
        for arm in d.ARMS:
            self.assertLess(first['arms'][arm]['evaluator_only']['noncentrality'], 1e-20)
            self.assertAlmostEqual(first['arms'][arm]['variance_trace']-first['arms'][arm]['coefficient_variance_trace'], .04)

    def test_control_equality_and_noiseless_noncentrality(self):
        prepared = d.prepare_design(11, self.config)
        worlds = ed.world_catalog(11, ed.fixed_config())
        rows = [d.episode_record(11, name, worlds[name], prepared, self.config, d.critical_value()) for name in d.CONTROLS]
        d.assert_controls(rows, self.config)
        rows[-1]['arms']['local']['q'] += .1
        with self.assertRaises(ArithmeticError):
            d.assert_controls(rows, self.config)
        world = dict(kind='cubic')
        one = d.episode_record(11, 'cubic', world, prepared, self.config, d.critical_value())
        changed = copy.deepcopy(prepared)
        changed['training'] = [(x, u, error+1.) for x, u, error in changed['training']]
        two = d.episode_record(11, 'cubic', world, changed, self.config, d.critical_value())
        self.assertNotEqual(one['fitted']['coefficients'], two['fitted']['coefficients'])
        for arm in d.ARMS:
            self.assertEqual(one['arms'][arm]['evaluator_only'], two['arms'][arm]['evaluator_only'])

    def test_full_grid_all_gates_and_quantiles(self):
        cells = [dict(world=w, arm=a, rule='uncertainty', rejections=4 if w in d.CONTROLS else (20 if a == 'local' else 32))
                 for w in d.WORLDS for a in d.ARMS]
        summary = dict(completed_keys=[[s, w] for s in self.config['seeds'] for w in d.WORLDS], cells=cells, control_equality_checked=True)
        self.assertTrue(d.decision(summary, self.config, True)['passed'])
        for w in d.CONTROLS:
            for a in d.ARMS:
                altered = copy.deepcopy(summary)
                next(c for c in altered['cells'] if c['world'] == w and c['arm'] == a)['rejections'] = 5
                self.assertFalse(d.decision(altered, self.config, True)['passed'])
        for w in ('exponential', 'cubic'):
            altered = copy.deepcopy(summary)
            next(c for c in altered['cells'] if c['world'] == w and c['arm'] == 'wide')['rejections'] = 31
            self.assertFalse(d.decision(altered, self.config, True)['passed'])
        for keys in (summary['completed_keys'][:-1], summary['completed_keys']+[summary['completed_keys'][0]]):
            self.assertFalse(d.decision(dict(summary, completed_keys=keys), self.config, True)['passed'])
        self.assertFalse(d.decision(summary, self.config, False)['passed'])
        self.assertEqual(d.quantiles([0., 1., 2., 3.]), [0., .75, 1.5, 2.25, 3.])

    def test_review_fixes_power_label_bound_and_failed_control_run(self):
        prepared = d.prepare_design(7, self.config)
        worlds = ed.world_catalog(7, ed.fixed_config())
        world = worlds['affine']
        episode = d.episode_record(7, 'affine', world, prepared, self.config, d.critical_value())
        summary = d.summarize([episode], self.config)
        self.assertFalse(summary['control_equality_checked'])
        for cell in summary['cells']:
            self.assertIn('mean_uncertainty_rule_theoretical_power', cell)
            self.assertNotIn('mean_theoretical_power', cell)
        # All sampling is replaced with seed7 fixtures; the runner's smoke label is not sampled.
        with tempfile.TemporaryDirectory(dir=d.ROOT/'results/runs', prefix='equation_domain_fixture_') as directory:
            parent = Path(directory)
            config_path = parent/'config.json'
            config_path.write_text(json.dumps(self.config))
            output = parent/'fresh'
            def fixture_record(seed, name, world, prepared, config, critical):
                record = copy.deepcopy(episode)
                record.update(seed=7, world=name)
                return record
            with patch.object(d, 'output_scope', return_value=output), \
                 patch.object(ed, 'world_catalog', return_value=worlds), \
                 patch.object(d, 'prepare_design', return_value=prepared), \
                 patch.object(d, 'episode_record', side_effect=fixture_record), \
                 patch.object(d, 'assert_controls', side_effect=ArithmeticError('forced control mismatch')):
                with self.assertRaisesRegex(ArithmeticError, 'forced control mismatch'):
                    d.run(config_path, output, smoke=True)
            metadata = json.loads((output/'metadata.json').read_text())
            saved_summary = json.loads((output/'summary.json').read_text())
            result = json.loads((output/'decision.json').read_text())
            self.assertEqual(metadata['status'], 'failed_partial')
            self.assertEqual(metadata['verified_control_seeds'], [])
            self.assertFalse(saved_summary['control_equality_checked'])
            self.assertFalse(result['complete'])
            self.assertFalse(result['passed'])
            self.assertFalse(metadata['resource_go'])
            # The shape137 positive series has decreasing ratios bounded above by z/138.
            z = metadata['critical_value']/2
            first = math.exp(-z+137*math.log(z)-math.lgamma(138))
            geometric_upper_bound = first/(1-z/138)
            self.assertGreaterEqual(metadata['omitted_mixture_cdf_bound'], geometric_upper_bound)
            self.assertEqual(metadata['omitted_mixture_cdf_bound'], 8.28e-88)

    def test_smoke_scope_hashes_and_two_resource_limits(self):
        with tempfile.TemporaryDirectory(dir=d.ROOT/'results/runs', prefix='equation_domain_fixture_') as directory:
            path = Path(directory)
            for name in ('config.json', 'episodes.jsonl', 'summary.json', 'decision.json'):
                (path/name).write_text('{}\n')
            meta = dict(status='completed', mode='smoke', completed_episodes=6, sources_unchanged=True,
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
                self.fail('fixture metadata did not stabilize')
            save()
            d.verify_smoke(path, 'c', {'a':'b'}, self.config)
            with self.assertRaises(FileExistsError):
                d.output_scope(path)
            with self.assertRaises(ValueError):
                d.output_scope(d.ROOT/'wrong')
            meta['elapsed_seconds'] = 2.
            save()
            with self.assertRaises(RuntimeError):
                d.verify_smoke(path, 'c', {'a':'b'}, self.config)
            meta['elapsed_seconds'] = .01
            save()
            with self.assertRaises(RuntimeError):
                d.verify_smoke(path, 'c', {'a':'b'}, dict(self.config, smoke_projection_limit_bytes=1))
            with self.assertRaises(ValueError):
                d.verify_smoke(path, 'changed', {'a':'b'}, self.config)
            (path/'summary.json').write_text('tampered')
            with self.assertRaises(ValueError):
                d.verify_smoke(path, 'c', {'a':'b'}, self.config)


if __name__ == '__main__':
    unittest.main()
