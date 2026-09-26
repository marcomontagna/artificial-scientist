import unittest
from unittest.mock import patch
from artificial_scientist.lab_api import Observation
from artificial_scientist.revision_agent import RevisionInvestigator
from artificial_scientist.revision_models import VectorModel


class RevisionAgentTests(unittest.TestCase):
    def step(self, agent, position=(0.0,0.0)):
        plan=agent.plan(80-2*agent.steps)
        tick=agent.observation.tick
        outcomes=[Observation(tick+i,*position) for i in (1,2)]
        return plan,agent.accept(outcomes)

    def test_initial_prefix_shared_across_policies_and_no_alias(self):
        agents=[RevisionInvestigator(Observation(0,0,0),p,7) for p in ('active','random','coverage','no-revision')]
        for _ in range(6):
            plans=[self.step(a)[0] for a in agents]
            self.assertTrue(all(p==plans[0] for p in plans))
        a=agents[0];p=a.plan(68);p['chosen']=99
        self.assertNotEqual(a.pending['chosen'],99)
        with self.assertRaises(RuntimeError):a.plan(68)

    def test_freeze_through_checks_and_adoption_before_refit(self):
        a=RevisionInvestigator(Observation(0,0,0))
        bad=VectorModel(('one',),True,(1.0,));good=VectorModel(('one',),True,(0.0,))
        # Distinct structures with known frozen predictions.
        good=VectorModel(('v',),True,(0.0,))
        a.incumbent=bad;a.steps=6
        a.cycle={'id':0,'models':[bad,good],'snapshots':[bad.snapshot(),good.snapshot()],
                 'trigger':{},'audit':{},'losses':{bad.id:[],good.id:[]},'check_steps':[]}
        with patch('artificial_scientist.revision_agent.fit_model',side_effect=lambda m,h,deadline,audit:m) as fit:
            for _ in range(3):
                self.step(a);self.assertEqual(fit.call_count,0)
            _,result=self.step(a);self.assertEqual(fit.call_count,1)
        self.assertTrue(result['revision']['accepted'])
        self.assertTrue(result['revision']['decision_before_refit'])
        self.assertEqual(a.incumbent.id,good.id)

    def test_no_revision_skips_proposer_even_with_repeated_failure(self):
        a=RevisionInvestigator(Observation(0,0,0),'no-revision')
        with patch('artificial_scientist.revision_agent.propose') as proposer:
            for k in range(10):self.step(a,(100*(-1)**k,100))
        proposer.assert_not_called();self.assertFalse(a.cycles)

    def test_timing_rejection_is_atomic_and_budget_guard(self):
        a=RevisionInvestigator(Observation(0,0,0));a.plan(80)
        with self.assertRaises(ValueError):a.accept([Observation(1,0,0),Observation(3,0,0)])
        self.assertEqual(a.history,[]);self.assertEqual(a.steps,0)
        a.pending=None
        with self.assertRaises(ValueError):a.plan(1)

    def test_rejection_keeps_incumbent(self):
        a=RevisionInvestigator(Observation(0,0,0));a.steps=6
        old=VectorModel(('v',),True,(0.0,));worse=VectorModel(('one',),True,(1.0,));a.incumbent=old
        a.cycle={'id':0,'models':[old,worse],'snapshots':[old.snapshot(),worse.snapshot()],
                 'trigger':{},'audit':{},'losses':{old.id:[],worse.id:[]},'check_steps':[]}
        for _ in range(4):self.step(a)
        self.assertFalse(a.cycles[0]['accepted']);self.assertEqual(a.incumbent.id,old.id)

    def test_actual_trigger_uses_completed_history_and_freezes_new_candidates(self):
        a=RevisionInvestigator(Observation(0,0,0))
        alternative=VectorModel(('one',),True,(1.0,))
        with patch('artificial_scientist.revision_agent.fit_model',side_effect=lambda m,h,deadline,audit:m), patch('artificial_scientist.revision_agent.propose',return_value=([alternative],{'candidate_fits':1,'feature_evaluations':2})) as proposer:
            for i in range(6):self.step(a,(100*(-1)**i,100*(-1)**i))
        proposer.assert_called_once()
        self.assertIsNotNone(a.cycle)
        self.assertEqual(a.cycle['trigger']['history_length'],12)
        self.assertEqual(a.cycle['trigger']['after_step'],5)
        self.assertEqual(a.plan(68)['phase'],'check')

    def test_proposal_timeout_keeps_evidence_and_partial_work(self):
        a=RevisionInvestigator(Observation(0,0,0))
        def timeout(m,h,deadline,audit):
            audit.update(candidate_fits=2,feature_evaluations=17)
            raise TimeoutError('injected proposal timeout')
        with patch('artificial_scientist.revision_agent.fit_model',side_effect=lambda m,h,deadline,audit:m), patch('artificial_scientist.revision_agent.propose',side_effect=timeout):
            for i in range(6):plan,result=self.step(a,(100*(-1)**i,100*(-1)**i))
        self.assertIn('incomplete',result)
        self.assertTrue(result['losses'])
        self.assertEqual(result['revision']['trigger']['history_length'],12)
        self.assertEqual(result['revision']['proposal_audit']['candidate_fits'],2)
        self.assertEqual(a.work['candidate_fits'],2)
        self.assertEqual(a.work['feature_evaluations'],17)
        self.assertIsNone(a.pending)

    def test_post_adoption_timeout_preserves_decision_and_refit_attempt(self):
        a=RevisionInvestigator(Observation(0,0,0));a.steps=6
        bad=VectorModel(('one',),True,(1.,));good=VectorModel(('v',),True,(0.,));a.incumbent=bad
        a.cycle={'id':0,'models':[bad,good],'snapshots':[bad.snapshot(),good.snapshot()],
                 'trigger':{},'audit':{},'losses':{bad.id:[],good.id:[]},'check_steps':[]}
        for _ in range(3):self.step(a)
        def timeout(m,h,deadline,audit):
            audit.update(candidate_fits=1,feature_evaluations=7)
            raise TimeoutError('injected refit timeout')
        with patch('artificial_scientist.revision_agent.fit_model',side_effect=timeout):plan,result=self.step(a)
        self.assertTrue(result['revision']['accepted']);self.assertIn('incomplete',result)
        self.assertEqual(a.incumbent.id,good.id);self.assertEqual(a.work['refits'],1)
        self.assertEqual(a.work['feature_evaluations'],7);self.assertIsNone(a.pending)

    def test_cooldown_cycle_limit_and_end_budget_use_actual_trigger(self):
        a=RevisionInvestigator(Observation(0,0,0))
        alternative=VectorModel(('one',),True,(10.,))
        def candidates(m,h,deadline,audit):
            audit.update(candidate_fits=1,feature_evaluations=2)
            return [alternative],audit
        with patch('artificial_scientist.revision_agent.fit_model',side_effect=lambda m,h,deadline,audit:m), patch('artificial_scientist.revision_agent.propose',side_effect=candidates) as proposer:
            for i in range(40):self.step(a,(100*(-1)**i,100*(-1)**i))
        self.assertEqual(len(a.cycles),2);self.assertEqual(proposer.call_count,2)
        self.assertGreaterEqual(a.cycles[1]['trigger']['after_step']-max(a.cycles[0]['check_steps']),6)
        b=RevisionInvestigator(Observation(72,0,0));b.steps=36;b.recent=[100]*5
        with patch('artificial_scientist.revision_agent.propose') as proposer,patch('artificial_scientist.revision_agent.fit_model',side_effect=lambda m,h,deadline,audit:m):
            self.step(b,(100,100))
        proposer.assert_not_called()
