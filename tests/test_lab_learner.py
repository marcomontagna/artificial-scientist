import ast
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from artificial_scientist.lab_api import Action, Observation, Transition
from artificial_scientist.lab_agent import Investigator, digest
from artificial_scientist.lab_models import Model, complexity, fit, grammar, nodes, training_rows, velocity
from artificial_scientist.lab_run import evaluate, frozen_rollout, investigate


class LearnerTest(unittest.TestCase):
    def test_safe_language_and_size(self):
        for bad in ('__import__("os")', ('call', 'p'), ('mul', 'u'), ('abs', 'v', 'u')):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                Model((bad,), (1.,))
        with self.assertRaises(ValueError):
            Model(('v', 'u', 'p'), (1.,) * 3)
        with self.assertRaises(ValueError):
            Model(('v',), (float('nan'),))
        self.assertTrue(all(nodes(t) <= 4 for t in grammar()))
        m = Model(('p',), (10.,))
        x, y = m.predict(Observation(0, 999., 999.), None, Action('wait', ticks=8))
        self.assertTrue(math.isfinite(x) and abs(x) <= 1000)

    def test_wait_current_and_lag_input_timing(self):
        m = Model(('v', 'u'), (.5, 1.))
        start = Observation(0, 0., 0.)
        prev = Transition(Observation(-1, -2., 0.), Action('push', magnitude=1), start)
        self.assertEqual(m.predict(start, prev, Action('wait', ticks=2)), (1.5, 0.))
        lag = Model(('lag_u',), (1.,))
        self.assertEqual(lag.predict(start, prev, Action('wait', ticks=2)), (1., 0.))
        self.assertEqual(m.predict(start, prev, Action('reset')), (0., 0.))
        # Open-loop sequence retains predicted final velocity across a long wait.
        seq = (Action('push', magnitude=1), Action('wait', ticks=2), Action('observe'))
        self.assertAlmostEqual(frozen_rollout(m, start, seq)[-1]['x'], 1.875)

    def test_no_fit_rows_across_unobserved_wait_or_reset(self):
        a = Observation(0, 0., 0.); b = Observation(3, 3., 0.); c = Observation(4, 4., 0.)
        wait = Transition(a, Action('wait', ticks=3), b)
        after = Transition(b, Action('observe'), c)
        self.assertEqual(training_rows([wait, after]), [])
        reset = Transition(c, Action('reset'), Observation(12, .01, .02))
        self.assertEqual(training_rows([reset]), [])
        post = Transition(reset.after, Action('observe'), Observation(13, .03, .04))
        rows = training_rows([reset, post])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0]['v'], 0.)
        self.assertEqual(velocity(wait), (1., 0.))

    def test_fit_constants_and_boundary(self):
        rows = [(dict(v=float(i), u=float(j), lag_u=0., p=0., one=1.), .7*i+.3*j)
                for i in (-1, 0, 1) for j in (-1, 0, 1)]
        coeff = fit(('v', 'u'), rows)
        self.assertAlmostEqual(coeff[0], .7, places=4)
        self.assertAlmostEqual(coeff[1], .3, places=4)
        for filename in ('lab_agent.py', 'lab_models.py', 'lab_api.py'):
            tree = ast.parse((Path('artificial_scientist') / filename).read_text())
            imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
            self.assertFalse(any(name and ('world' in name or 'run' in name) for name in imports))
            self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ('eval', 'exec', '__import__') for n in ast.walk(tree)))

    def test_prediction_frozen_before_update_and_new_model_unvalidated(self):
        agent = Investigator(Observation(0, 0., 0.))
        for step in range(4):
            plan = agent.plan(80-step)
            frozen = copy.deepcopy(plan)
            expected_hash = digest(plan)
            action = Action(**plan['action'])
            errors, revision = agent.accept(action, Observation(step+1, .1*(step+1), -.03*step))
            self.assertEqual(plan, frozen)
            self.assertEqual(digest(plan), expected_hash)
            self.assertAlmostEqual(errors[0]['squared_error'], (.1*(step+1)-plan['predictions'][0]['x'])**2+(-.03*step-plan['predictions'][0]['y'])**2)
        self.assertTrue(revision['added'])
        self.assertTrue(all(m['validated_predictions'] == 0 and m['prequential_mse'] is None for m in revision['added']))
        self.assertTrue(revision['updated'])

    def test_resource_stop_and_journal_before_world_action(self):
        from artificial_scientist.lab_world import make_world
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'case'
            wrapped = make_world(16)
            original = wrapped.step
            def checked(action):
                records = (output / 'predictions_before_actions.jsonl').read_text().splitlines()
                latest = json.loads(records[-1])
                self.assertEqual(latest['prediction_hash'], digest(latest['plan']))
                return original(action)
            wrapped.step = checked
            with patch('artificial_scientist.lab_run.make_world', return_value=wrapped), patch('artificial_scientist.lab_run.evaluate', return_value={'test_only': True}):
                trace = investigate('development', 'active', 16, output, budget=4)
            self.assertEqual(trace['training_cost'], 4)
            self.assertEqual(trace['status'], 'budget_complete')
            self.assertEqual(len(trace['events']), 4)
            with self.assertRaises(FileExistsError):
                investigate('development', 'active', 16, output, budget=4)
        with self.assertRaises(ValueError):
            investigate('development', 'active', 16, 'unused', budget=81)

    def test_active_argmax_weighting_no_reproposal_and_surprise(self):
        agent = Investigator(Observation(0, .001, .001))
        seen = set(m.id for m in agent.models)
        had_surprise = False
        for step in range(11):
            plan = agent.plan(80-step)
            if step >= 4:
                self.assertEqual(plan['choice']['selected_score'], max(o['score'] for o in plan['choice']['options']))
            self.assertAlmostEqual(sum(p['weight'] for p in plan['predictions']), 1.)
            action = Action(**plan['action'])
            # Sudden unexplained displacement gives a deterministic surprise.
            coordinate = 100. if step == 6 else .05*step
            _, revision = agent.accept(action, Observation(agent.observation.tick+action.cost, coordinate, .02*step))
            for new in revision['added']:
                self.assertNotIn(new['id'], seen)
                seen.add(new['id'])
            had_surprise |= revision['surprise']
        self.assertTrue(had_surprise)
        self.assertGreaterEqual(agent.final_model().predictions, 3)
        # Bad old predictors get less influence than a well-performing one.
        agent.models = [Model((), (), [10.]*4, 4), Model(('v',), (.5,), [.001]*4, 4)]
        plan = agent.plan(80)
        self.assertLess(plan['predictions'][0]['weight'], plan['predictions'][1]['weight'])

    def test_timeout_keeps_revision_and_small_cap_keeps_partial_trace(self):
        agent = Investigator(Observation(0, 0., 0.))
        for step in range(4):
            plan = agent.plan(80-step)
            with patch('artificial_scientist.lab_agent.propose', side_effect=TimeoutError):
                errors, revision = agent.accept(Action(**plan['action']), Observation(step+1, .1*(step+1), .01*step))
        self.assertIn('incomplete', revision)
        self.assertTrue(revision['updated'])
        self.assertTrue(errors)
        with tempfile.TemporaryDirectory() as tmp, patch('artificial_scientist.lab_run.MAX_TRACE_BYTES', 8192):
            trace = investigate('development', 'active', 16, Path(tmp)/'small', budget=4)
            self.assertEqual(trace['status'], 'incomplete_trace_cap')
            self.assertEqual(trace['training_cost'], 0)
            size = sum(p.stat().st_size for p in (Path(tmp)/'small').iterdir())
            self.assertLessEqual(size, 8192)

    def test_evaluation_frozen_deterministic_and_does_not_mutate_models(self):
        import time
        m = Model(('v', 'u'), (.5, .3))
        before = copy.deepcopy(m.snapshot())
        rows = [(dict(v=1., u=.5, lag_u=0., p=0., one=1.), .4)]
        a = evaluate(m, rows, 'development', 31, time.process_time()+10)
        b = evaluate(m, rows, 'development', 31, time.process_time()+10)
        self.assertEqual(a, b)
        self.assertEqual(m.snapshot(), before)
        for record in a['records']:
            self.assertEqual(record['prediction_hash'], digest(record['predictions']))
            self.assertGreater(record['cost'], 8)
        self.assertEqual(set(a['mean_squared_position_error']), {'learned', 'linear', 'persistence', 'home'})


if __name__ == '__main__':
    unittest.main()
