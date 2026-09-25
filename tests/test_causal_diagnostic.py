"""Synthetic fixtures only: no smoke seeds190..194 or study seeds200..399."""
import copy
import json
import math
import random
import unittest
from pathlib import Path
from unittest.mock import patch

from artificial_scientist import causal_diagnostic as diagnostic
from artificial_scientist.causal_feasibility import (
    ACTIONS, STATES, null_log_likelihood, supported,
)


def configuration():
    return json.loads((diagnostic.ROOT/'experiments/causal_diagnostic_v0.json').read_text())


class CausalDiagnosticTests(unittest.TestCase):
    def test_incremental_null_matches_independent_old_helper(self):
        rng = random.Random(11)
        histories = []
        histories.append([(a := rng.randrange(7), rng.choice(
            [y for y, state in enumerate(STATES) if supported(a, state)])) for _ in range(80)])
        boundary = next(w for w in diagnostic.world_catalog(7, configuration()) if w['name'] == 'null_boundary')
        histories.append([(a := tick % 7, diagnostic.inverse_cdf(boundary['probabilities'][a],
                          .1 if tick % 2 else .9, a)) for tick in range(80)])
        for history in histories:
            learner = diagnostic.NullMLE()
            counts = [[0]*8 for _ in ACTIONS]
            for a, y in history:
                counts[a][y] += 1
                self.assertAlmostEqual(learner.observe(a, y), null_log_likelihood(counts), delta=1e-9)
        self.assertEqual(len(diagnostic.PARENT_SETS), 12)
        self.assertEqual(len(diagnostic.GRAPH_SCORES), 25)

    def test_numerators_prequential_normalization_and_batch_identity(self):
        config = configuration()
        mixture = diagnostic.StructuredMixture(config)
        kt = diagnostic.KT(config['kt_prior'])
        history = [(0, 0), (1, 1), (0, 7), (2, 4), (5, 6), (6, 3), (3, 0)]
        for a, y in history:
            for model in (mixture, kt):
                for action in range(7):
                    self.assertAlmostEqual(sum(model.predictive(action, outcome)
                        for outcome, state in enumerate(STATES) if supported(action, state)), 1., places=12)
                previous, prediction = model.log_q, model.predictive(a, y)
                self.assertAlmostEqual(model.observe(a, y)-previous, math.log(prediction), places=12)
        marginal = math.fsum(math.prod(world[a][y] for a, y in history)
                             for world in mixture.tables)/len(mixture.tables)
        self.assertAlmostEqual(mixture.log_q, math.log(marginal), places=12)
        expected = 0.
        for a, row in enumerate(kt.counts):
            cells = [row[y] for y, state in enumerate(STATES) if supported(a, state)]
            expected += math.lgamma(len(cells)*.5)-math.lgamma(sum(cells)+len(cells)*.5)
            expected += sum(math.lgamma(c+.5)-math.lgamma(.5) for c in cells)
        self.assertAlmostEqual(kt.log_q, expected, places=12)

    def test_passive_evidence_nonpositive_on_every_fixture_prefix(self):
        rng = random.Random(7)
        for outcomes in ([0]*100, [0,7]*50, [rng.randrange(8) for _ in range(100)]):
            pair = diagnostic.DiagnosticPair(configuration())
            for outcome in outcomes:
                values = pair.observe(0, outcome)
                self.assertTrue(all(v <= 1e-9 for v in values.values()))

    def test_inverse_cdf_boundary_never_zero_or_impossible(self):
        config = configuration()
        boundary = next(w for w in diagnostic.world_catalog(7, config) if w['name'] == 'null_boundary')
        for a, row in enumerate(boundary['probabilities']):
            for u in (0., .25, .5, .75, math.nextafter(1., 0.)):
                y = diagnostic.inverse_cdf(row, u, a)
                self.assertGreater(row[y], 0.)
                self.assertTrue(supported(a, STATES[y]))
        # Positive support ends before the array; cumulative mass is slightly short.
        row = [.5, .5-1e-15, 0., 0., 0., 0., 0., 0.]
        self.assertEqual(diagnostic.inverse_cdf(row, math.nextafter(1., 0.), 1), 1)
        with self.assertRaises(ValueError):
            diagnostic.inverse_cdf([.125]*8, .5, 1)
        for uniform in (1., -1., math.nan):
            with self.assertRaises(ValueError):
                diagnostic.inverse_cdf([.125]*8, uniform, 0)

    def test_world_catalog_definition_support_and_seed_repeatability(self):
        config = configuration()
        worlds = diagnostic.world_catalog(7, config)
        self.assertEqual(len(worlds), 15)
        self.assertEqual(worlds, diagnostic.world_catalog(7, config))
        self.assertEqual(sum(w['null'] for w in worlds), 5)
        for world in worlds:
            for a, row in enumerate(world['probabilities']):
                self.assertAlmostEqual(sum(row), 1., places=12)
                self.assertTrue(all(p >= 0 and (supported(a, STATES[y]) or p == 0)
                                    for y, p in enumerate(row)))
        random_world = next(w for w in worlds if w['name'] == 'null_random')
        self.assertIn('cpts', random_world)
        self.assertIn('parents', random_world)
        stress = next(w for w in worlds if w['name'] == 'stress_biased_u')
        # Both paired marginals equal .2*.95 + .8*.05 = .23 passively.
        for variable in (0, 1):
            self.assertAlmostEqual(sum(p for state, p in zip(STATES, stress['probabilities'][0])
                                       if state[variable]), .23)

    def test_replay_rng_and_prefix_causality(self):
        config = configuration()
        config.update(steps=12, snapshots=[6,12], censor_cap=13)
        worlds = diagnostic.world_catalog(7, config)
        world = worlds[0]
        record = diagnostic.episode_record(world, 7, 'random7', config)
        self.assertEqual(record, diagnostic.episode_record(world, 7, 'random7', config))
        replay = diagnostic.replay_history(record['actions'], record['outcomes'], config)
        for name in diagnostic.NAMES:
            self.assertAlmostEqual(replay[-1][name], record['numerators'][name]['snapshots']['12'])
        prefix = diagnostic.replay_history(record['actions'][:6], record['outcomes'][:6], config)
        self.assertEqual(prefix, replay[:6])
        original = diagnostic.inverse_cdf
        uniforms = []
        def capture(row, u, action):
            uniforms.append(u)
            return original(row, u, action)
        with patch.object(diagnostic, 'inverse_cdf', side_effect=capture):
            first = list(diagnostic.sampled_history(world, 7, 'random7', config))
            second = list(diagnostic.sampled_history(worlds[-1], 7, 'roundrobin7', config))
        self.assertEqual(uniforms[:12], uniforms[12:])
        other = list(diagnostic.sampled_history(worlds[-1], 7, 'random7', config))
        self.assertEqual([a for a, _ in first], [a for a, _ in other])
        self.assertEqual([a for a, _ in second], [i%7 for i in range(12)])
        short = copy.deepcopy(config)
        short.update(steps=6, snapshots=[6], censor_cap=7)
        short_record = diagnostic.episode_record(world, 7, 'random7', short)
        self.assertEqual(short_record['outcomes'], record['outcomes'][:6])

    def test_censoring_wilson_and_incomplete_gate(self):
        config = configuration()
        z = config['wilson_z']
        self.assertLess(diagnostic.wilson(171,200,z)[0], .8)
        self.assertGreaterEqual(diagnostic.wilson(172,200,z)[0], .8)
        fixture = copy.deepcopy(config)
        fixture.update(steps=8, snapshots=[4,8], censor_cap=9, alpha=1e-100)
        fair = next(w for w in diagnostic.world_catalog(7, fixture) if w['name']=='null_fair')
        record = diagnostic.episode_record(fair, 7, 'roundrobin7', fixture)
        for metrics in record['numerators'].values():
            self.assertIsNone(metrics['first_alarm'])
            self.assertTrue(metrics['censored'])
            self.assertEqual(metrics['capped_time'], 9)
        summary = diagnostic.summarize([record], fixture)
        self.assertTrue(all(row['mean_capped_time']==9 and row['detections']['8']['count']==0 for row in summary))
        fake_primary = [dict(world=world, schedule=schedule, numerator=config['primary'], null=False,
            n=200, detections={'400':dict(count=200, rate=1., wilson=diagnostic.wilson(200,200,z))})
            for world in config['gate_worlds'] for schedule in config['schedules']]
        gate = diagnostic.study_gate([], fake_primary, config, completed=True)
        self.assertTrue(gate['primary_power_pass'])
        self.assertFalse(gate['complete'])
        self.assertFalse(gate['passed'])

    def test_support_scope_overwrite_and_missing_smoke_gate(self):
        for constructor in (diagnostic.NullMLE, diagnostic.KT,
                            lambda: diagnostic.StructuredMixture(configuration())):
            with self.assertRaises(ValueError):
                constructor().observe(1, 4)
        with self.assertRaises(ValueError):
            diagnostic.output_scope(diagnostic.ROOT/'causal_diagnostic_bad')
        valid = diagnostic.ROOT/'results/runs/causal_diagnostic_test_not_created'
        with patch.object(Path, 'exists', return_value=True):
            with self.assertRaises(FileExistsError):
                diagnostic.output_scope(valid)
        with self.assertRaisesRegex(ValueError, 'smoke-evidence'):
            diagnostic.run(diagnostic.ROOT/'experiments/causal_diagnostic_v0.json', valid)
        diagnostic.validate_config(configuration())
        changed = configuration()
        changed['gate_required_detections'] = 171
        with self.assertRaises(ValueError):
            diagnostic.validate_config(changed)


if __name__ == '__main__':
    unittest.main()
