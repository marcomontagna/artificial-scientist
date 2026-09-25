import itertools
import math
import unittest

from artificial_scientist.causal_feasibility import (
    ACTIONS, DAGS, STATES, SequentialDiagnostic, confounded_world, designs,
    fit_graph, graph_world, null_log_likelihood, project_world, supported, weighted_kl)


class CausalFeasibilityTests(unittest.TestCase):
    def test_graphs(self):
        self.assertEqual(len(DAGS), 25)
        self.assertEqual(len(set(DAGS)), 25)
        for graph in DAGS:
            self.assertTrue(any(all(order.index(p) < order.index(i)
                                    for i, parents in enumerate(graph) for p in parents)
                                for order in itertools.permutations(range(3))))

    def test_intervention_support_and_confounding(self):
        world = confounded_world((0, 1), .2)
        for a, row in enumerate(world):
            self.assertAlmostEqual(sum(row), 1.)
            self.assertEqual(sum(p > 0 for p in row), 8 if a == 0 else 4)
            self.assertTrue(all(supported(a, STATES[k]) or p == 0 for k, p in enumerate(row)))
        correlation = sum(p for y, p in zip(STATES, world[0]) if y[0] == y[1])
        self.assertAlmostEqual(correlation, .8**2+.2**2)
        for a in (1, 2):
            self.assertAlmostEqual(sum(p for y, p in zip(STATES, world[a]) if y[1]), .5)

    def test_zero_and_positive_separation(self):
        for noise in (.5, .2):
            world = confounded_world((0, 1), noise)
            for name, weights in designs((0, 1)).items():
                value = min(f['kl'] for f in project_world(world, weights))
                if noise == .5 or name in ('passive', 'privileged_pair_only'):
                    self.assertAlmostEqual(value, 0., places=10)
                else:
                    self.assertGreater(value, 1e-8)
        fork = graph_world(((), (0,), (0,)), [[.5], [.2, .8], [.2, .8]])
        for weights in designs((1, 2)).values():
            self.assertAlmostEqual(min(f['kl'] for f in project_world(fork, weights)), 0., places=10)

    def test_null_mle_passive_saturated(self):
        counts = [[0]*8 for _ in ACTIONS]
        counts[0] = [3, 0, 1, 0, 0, 2, 0, 1]
        n = sum(counts[0])
        expected = sum(c*math.log(c/n) for c in counts[0] if c)
        self.assertAlmostEqual(null_log_likelihood(counts), expected)
        # A manipulated root contributes no likelihood, even when values alternate.
        counts = [[0]*8 for _ in ACTIONS]
        counts[1][0], counts[2][4] = 3, 2
        self.assertAlmostEqual(fit_graph(counts, ((), (), ()))[1], 0.)

    def test_kt_closed_form_and_no_future_update(self):
        test = SequentialDiagnostic()
        history = [(0, 0), (1, 1), (0, 0), (1, 0), (2, 4)]
        first = test.predictive(0, 0)
        self.assertEqual(first, 1/8)
        self.assertEqual(sum(test.predictive(1, k) for k, y in enumerate(STATES) if supported(1, y)), 1.)
        for a, y in history:
            before = test.log_q
            p = test.predictive(a, y)
            test.observe(a, y)
            self.assertAlmostEqual(test.log_q-before, math.log(p))
        expected = 0.
        for a, row in enumerate(test.counts):
            cells = [row[k] for k, y in enumerate(STATES) if supported(a, y)]
            k = len(cells)
            expected += math.lgamma(k*.5)-math.lgamma(sum(cells)+k*.5)
            expected += sum(math.lgamma(c+.5)-math.lgamma(.5) for c in cells)
        self.assertAlmostEqual(test.log_q, expected)
        with self.assertRaises(ValueError):
            test.observe(1, 4)  # do(X0=0), but observed X0=1

    def test_pooled_projection_matches_closed_form(self):
        world = confounded_world((0, 1), .2)
        r = .8**2+.2**2
        def kl(p, q):
            return p*math.log(p/q)+(1-p)*math.log((1-p)/(1-q))
        for name, weights in designs((0, 1)).items():
            c, a = weights[0]+weights[5]+weights[6], weights[1]+weights[2]
            q = (c*r+a*.5)/(c+a)
            expected = c*kl(r, q)+a*kl(.5, q)
            self.assertAlmostEqual(min(f['kl'] for f in project_world(world, weights)), expected)
        weights = designs((0, 1))['privileged_passive_pair']
        counts = [[weights[a]*p for p in row] for a, row in enumerate(world)]
        graph = ((), (0,), ())
        cpts, _ = fit_graph(counts, graph)
        self.assertAlmostEqual(cpts[1][0], .44)
        self.assertAlmostEqual(cpts[1][1], .56)
        minimum = weighted_kl(world, graph_world(graph, cpts), weights)
        for cell in (0, 1):
            for delta in (-.1, .1):
                alternative = [list(row) for row in cpts]
                alternative[1][cell] += delta
                self.assertGreater(weighted_kl(world, graph_world(graph, alternative), weights), minimum)

    def test_post_update_scoring_is_not_normalized(self):
        for a in (0, 1):
            before, broken = 0., 0.
            for y, state in enumerate(STATES):
                if supported(a, state):
                    test = SequentialDiagnostic()
                    before += test.predictive(a, y)
                    test.observe(a, y)
                    broken += test.predictive(a, y)
            self.assertAlmostEqual(before, 1.)
            self.assertGreater(broken, 1.)  # scoring after seeing y is not a density

    def test_adaptive_short_history_likelihood_domination(self):
        for cpts in ([[.5], [.2, .8], [.2, .8]], [[0.], [0., 1.], [1., 0.]]):
            true = graph_world(((), (0,), (0,)), cpts)
            total = mean_e = mean_ratio = 0.
            def visit(history, prob, null_likelihood):
                nonlocal total, mean_e, mean_ratio
                test = SequentialDiagnostic()
                for a, y in history:
                    test.observe(a, y)
                if len(history) == 3:
                    value = math.exp(test.log_q-null_log_likelihood(test.counts))
                    ratio = math.exp(test.log_q)/null_likelihood
                    self.assertLessEqual(value, ratio+1e-12)
                    total += prob; mean_e += prob*value; mean_ratio += prob*ratio
                    return
                # Actions use only previous outcomes; no hidden model input.
                action = 0 if not history else 1+history[-1][1] % 6
                for y, p in enumerate(true[action]):
                    if p:
                        visit(history+[(action, y)], prob*p, null_likelihood*p)
            visit([], 1., 1.)
            self.assertAlmostEqual(total, 1.)
            self.assertLessEqual(mean_e, 1.+1e-12)
            self.assertLessEqual(mean_ratio, 1.+1e-12)
            if cpts[0][0] == .5:
                self.assertAlmostEqual(mean_ratio, 1.)


if __name__ == '__main__':
    unittest.main()
