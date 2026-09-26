import itertools
import math
import unittest
from unittest.mock import patch

from artificial_scientist.lab_agent import Investigator
from artificial_scientist.lab_api import Action, Observation
from artificial_scientist.lab_guided import guided_propose
from artificial_scientist.lab_models import Model, complexity, fit, grammar, program_id


def records_for(variable='u', model_id='zero'):
    records, rows = [], []
    for step, (v, u) in enumerate(itertools.product((-1., 0., 1.), repeat=2)):
        inputs = dict(v=v, u=u, p=0., lag_u=0., one=1.)
        residual = .4*inputs[variable]
        for axis in ('x', 'y'):
            records.append(dict(step=step, axis=axis, inputs=inputs, model_id=model_id,
                                coefficient_version=[], prediction=0., observed=residual, residual=residual))
            rows.append((inputs, residual))
    return records, rows


class GuidedTest(unittest.TestCase):
    def test_observations_determine_shortlist_before_at_most_eight_fits(self):
        features = []
        for variable in ('u', 'v'):
            records, rows = records_for(variable)
            audit = {}
            def checked_fit(terms, rows):
                self.assertIn(program_id(terms), audit['shortlist'])
                self.assertLessEqual(len(audit['shortlist']), 8)
                return fit(terms, rows)
            with patch('artificial_scientist.lab_guided.fit', side_effect=checked_fit) as spy:
                new, _ = guided_propose(rows, {'zero'}, Model((), ()), records, audit=audit)
            self.assertEqual(spy.call_count, audit['candidate_fits'])
            self.assertLessEqual(spy.call_count, 8)
            self.assertEqual(audit['feature_evaluations'], len(grammar())*len(records))
            self.assertEqual(audit['diagnosis']['selected_features'][0], variable)
            self.assertTrue(any(variable in m.terms for m in new))
            features.append(audit['shortlist'])
        self.assertNotEqual(features[0], features[1])

    def test_wrong_model_evidence_excluded_and_no_signal_uses_only_escape(self):
        records, rows = records_for('u', model_id='other_model')
        audit = {}
        guided_propose(rows, {'zero'}, Model((), ()), records, audit=audit)
        self.assertEqual(audit['diagnosis']['evidence'], [])
        self.assertEqual(audit['diagnosis']['selected_features'], [])
        self.assertEqual(audit['candidate_fits'], 1)
        self.assertEqual(audit['candidates'][0]['origin'], 'scheduled_escape')

    def test_feature_screen_finds_interaction_without_main_effect(self):
        records, rows = [], []
        for step, (v, u) in enumerate(itertools.product((-1., 1.), repeat=2)):
            inputs = dict(v=v, u=u, p=0., lag_u=0., one=1.)
            for axis in ('x','y'):
                records.append(dict(step=step, axis=axis, inputs=inputs, model_id='zero',
                                    coefficient_version=[], prediction=0., observed=v*u, residual=v*u))
                rows.append((inputs, v*u))
        atoms = grammar()
        catalogue = [c for n in (1,2) for c in itertools.combinations(atoms,n) if complexity(c)<=12]
        cursor = next(i for i,c in enumerate(catalogue) if c == (('mul','v','u'),))
        audit = {}
        new, _ = guided_propose(rows, {'zero'}, Model((),()), records, cursor, audit=audit)
        self.assertIn('(v*u)',audit['diagnosis']['selected_features'])
        supported = next(c for c in audit['candidates'] if c['model_id']=='(v*u)')
        self.assertEqual(supported['origin'],'residual_association')
        self.assertEqual(new[0].terms, (('mul','v','u'),))

    def test_chronology_origins_and_exclusion_after_wait(self):
        agent = Investigator(Observation(0, 0., 0.), proposal='guided')
        for step in range(9):
            plan = agent.plan(80-step)
            old_len = len(agent.residual_records)
            action = Action(**plan['action'])
            outcome = Observation(agent.observation.tick+action.cost, step*.04, math.sin(step)*.02)
            _, revision = agent.accept(action, outcome)
            for record in agent.residual_records[old_len:]:
                frozen = next(p for p in plan['predictions'] if p['model_id']==record['model_id'])
                self.assertEqual(record['prediction'], frozen[record['axis']])
                self.assertEqual(record['coefficient_version'], frozen['coefficients'])
                self.assertEqual(record['residual'], getattr(outcome,record['axis'])-record['prediction'])
            search = revision['search']
            self.assertLessEqual(search['candidate_fits'],8)
            if 'diagnosis' in search:
                self.assertTrue(all(r['step']<=step for r in search['diagnosis']['evidence']))
            for link in plan['choice']['hypothesis_links']:
                self.assertLess(link['proposed_after_step'],step)
                self.assertEqual(link['changes_active_choice'], link['action_without_model'] != plan['action'])
        self.assertGreater(agent.search_cost['candidate_fits'],0)
        self.assertTrue(agent.origins)
        # Force a legal planned wait, then a one-tick action: neither contributes
        # a fit residual because the prior interval is not a one-tick velocity.
        fresh = Investigator(Observation(0,0.,0.),proposal='guided')
        plan = fresh.plan(80)
        wait = Action('wait',ticks=3)
        fresh.pending['action'] = dict(kind='wait',angle=0.,magnitude=0.,ticks=3)
        fresh.accept(wait,Observation(3,.1,.1))
        plan = fresh.plan(77)
        fresh.accept(Action(**plan['action']),Observation(4,.2,.2))
        self.assertEqual(fresh.residual_records,[])

    def test_guided_timeout_preserves_partial_accounting_and_refits(self):
        records, rows = records_for('u')
        agent = Investigator(Observation(0,0.,0.),proposal='guided')
        def interrupted(*args, **kwargs):
            calls = [0]
            def stop_on_second(terms, fit_rows):
                calls[0] += 1
                if calls[0] == 2:
                    raise TimeoutError('injected after one fitted candidate')
                return fit(terms,fit_rows)
            with patch('artificial_scientist.lab_guided.fit', side_effect=stop_on_second):
                return guided_propose(rows,{'zero'},Model((),()),records,audit=kwargs['audit'])
        for step in range(4):
            plan = agent.plan(80-step)
            with patch('artificial_scientist.lab_agent.guided_propose',side_effect=interrupted):
                errors, revision = agent.accept(Action(**plan['action']),Observation(step+1,.1*(step+1),.01*step))
        self.assertIn('incomplete',revision)
        self.assertEqual(revision['search']['candidate_fits'],2)
        self.assertGreater(revision['search']['feature_evaluations'],0)
        self.assertEqual(agent.search_cost['candidate_fits'],2)
        self.assertTrue(revision['updated'])
        self.assertTrue(errors)

    def test_incumbent_switch_resets_residual_episode(self):
        agent = Investigator(Observation(0,0.,0.), proposal='guided')
        plan = agent.plan(80)
        agent.accept(Action(**plan['action']), Observation(1,.1,0.))
        self.assertTrue(agent.residual_records)
        old_epoch = agent.residual_epoch
        # Change the preferred structure using only its completed prediction
        # record; next prediction is still frozen before the next observation.
        agent.models[0].errors = [1.]*3
        agent.models[0].predictions = 3
        agent.models[1].errors = [.001]*3
        agent.models[1].predictions = 3
        plan = agent.plan(79)
        agent.accept(Action(**plan['action']), Observation(2,.15,0.))
        self.assertEqual(agent.residual_epoch,old_epoch+1)
        self.assertEqual({r['step'] for r in agent.residual_records},{1})
        self.assertEqual({r['model_id'] for r in agent.residual_records},{'v'})

    def test_guided_does_not_call_enumerator_and_default_preserved(self):
        self.assertEqual(Investigator(Observation(0,0.,0.)).proposal,'enumerate')
        agent = Investigator(Observation(0,0.,0.),proposal='guided')
        with patch('artificial_scientist.lab_agent.propose', side_effect=AssertionError('enumeration leaked')):
            for step in range(8):
                plan = agent.plan(80-step)
                action = Action(**plan['action'])
                agent.accept(action,Observation(agent.observation.tick+action.cost,.05*step,0.))


if __name__ == '__main__':
    unittest.main()
