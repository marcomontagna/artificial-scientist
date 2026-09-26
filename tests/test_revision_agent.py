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


class ConfirmationRuleTests(unittest.TestCase):
    def agent(self, rule, models=None):
        a=RevisionInvestigator(Observation(0,0,0),check_rule=rule)
        models=models or [VectorModel(('v',),True,(1.,)),VectorModel(('one',),True,(0.,))]
        a.incumbent=models[0];a.steps=6
        a.cycle=dict(id=0,models=models,snapshots=[m.snapshot() for m in models],
                     trigger={},audit={},losses={m.id:[] for m in models},check_steps=[])
        return a

    def step(self,a,x=0.):
        plan=a.plan(80-2*a.steps);tick=a.observation.tick
        result=a.accept([Observation(tick+1,x,0.),Observation(tick+2,x,0.)])
        return plan,result

    @staticmethod
    def no_refit(model,history,deadline,audit):
        return model

    def test_fixed_suffix_actions_ignore_outcomes_and_frozen_tapes_are_sliced(self):
        a,b=self.agent('confirm_long'),self.agent('confirm_long')
        for _ in range(4):
            self.step(a);self.step(b)
        frozen=a.cycle['confirmation_plan']
        self.assertEqual(frozen,b.cycle['confirmation_plan'])
        self.assertEqual(len(frozen['actions']),8)
        self.assertEqual(len(frozen['experiment_indexes']),4)
        with patch('artificial_scientist.revision_agent.fit_model',side_effect=self.no_refit):
            for pair in range(4):
                pa,_=self.step(a,float(pair));pb,_=self.step(b,-100.*pair)
                self.assertEqual(pa['actions'],pb['actions'])
                self.assertEqual(pa['chosen'],frozen['experiment_indexes'][pair])
                self.assertEqual(pa['check_stage'],'confirmation')
                self.assertEqual(pa['prediction_origin'],'confirmation_start_frozen_tape')
                for p,source in zip(pa['predictions'],frozen['predictions']):
                    self.assertEqual(p['tape'],source['tape'][pair*2:pair*2+2])
                self.assertEqual(pa['predictions'],pb['predictions'])
        self.assertEqual(len(a.cycles),1)
        self.assertEqual(len(a.cycles[0]['position_losses'][a.cycles[0]['incumbent_id']]),16)

    def test_short_tapes_restart_but_full_plan_does_not_mutate(self):
        a=self.agent('confirm_short')
        for _ in range(4):self.step(a)
        frozen=a.cycle['confirmation_plan']
        self.step(a,10.)
        p=a.plan(80-2*a.steps)
        self.assertEqual(p['prediction_origin'],'current_observed_start')
        self.assertEqual(p['predictions'],p['options'][p['chosen']]['predictions'])
        self.assertNotEqual(p['predictions'][0]['tape'],frozen['predictions'][0]['tape'][2:4])
        p['confirmation_plan']['actions'].clear()
        self.assertEqual(len(a.pending['confirmation_plan']['actions']),8)
        self.assertEqual(len(frozen['actions']),8)

    def test_split_winner_cannot_swap_to_better_confirmation_alternative(self):
        old=VectorModel(('v',),True,(3.,))
        first=VectorModel(('one',),True,(0.,))
        other=VectorModel(('p',),True,(1.,))
        fixed={old.id:3.,first.id:0.,other.id:1.}
        def predict(m,o,h,actions):return [(fixed[m.id],0.) for _ in actions]
        outcomes={}
        with patch.object(VectorModel,'predict_tape',predict),patch('artificial_scientist.revision_agent.fit_model',side_effect=self.no_refit):
            for rule in ('pooled','confirm_short','confirm_long'):
                a=self.agent(rule,[old,first,other])
                for _ in range(4):self.step(a,0.)
                self.assertEqual(a.cycle['screening']['winner_id'],first.id)
                for _ in range(4):self.step(a,1.2)
                outcomes[rule]=a.cycles[0]
        self.assertEqual(outcomes['pooled']['best_alternative'],other.id)
        for rule in ('confirm_short','confirm_long'):
            self.assertEqual(outcomes[rule]['best_alternative'],first.id)
            self.assertTrue(outcomes[rule]['accepted'])

    def test_failed_screen_can_be_rescued_only_by_pooled(self):
        old=VectorModel(('v',),True,(1.,));new=VectorModel(('one',),True,(2.,))
        def predict(m,o,h,actions):return [(1. if m.id==old.id else 2.,0.) for _ in actions]
        with patch.object(VectorModel,'predict_tape',predict),patch('artificial_scientist.revision_agent.fit_model',side_effect=self.no_refit):
            for rule in ('pooled','confirm_short','confirm_long'):
                a=self.agent(rule,[old,new])
                for _ in range(4):self.step(a,1.2)
                self.assertFalse(a.cycle['screening']['passed'])
                for _ in range(3):
                    self.step(a,2.);self.assertEqual(a.cycles,[])
                    self.assertEqual(a.incumbent.id,old.id)
                self.step(a,2.)
                self.assertEqual(a.cycles[0]['accepted'],rule=='pooled')
                self.assertTrue(a.cycles[0]['confirmation_passed'])

    def test_nonoriginal_trigger_requires_sixteen_remaining_units(self):
        alternative=VectorModel(('one',),True,(10.,))
        for steps,expected in ((31,True),(32,False)):
            a=RevisionInvestigator(Observation(2*steps,0,0),check_rule='confirm_long')
            a.steps=steps;a.recent=[100]*5
            with patch('artificial_scientist.revision_agent.fit_model',side_effect=self.no_refit),patch('artificial_scientist.revision_agent.propose',return_value=([alternative],{})) as proposer:
                self.step(a,100.)
            self.assertEqual(proposer.called,expected)

    def test_confirmation_completion_timeout_preserves_final_decision(self):
        a=self.agent('confirm_long')
        for _ in range(7):self.step(a)
        def timeout(m,h,deadline,audit):
            audit.update(candidate_fits=1,feature_evaluations=7)
            raise TimeoutError('injected final refit')
        with patch('artificial_scientist.revision_agent.fit_model',side_effect=timeout):
            _,result=self.step(a)
        self.assertIn('incomplete',result)
        self.assertEqual(result['revision']['check_rule'],'confirm_long')
        self.assertEqual(len(result['revision']['check_steps']),8)
        self.assertEqual(len(a.cycles),1)
        self.assertEqual(a.work['refits'],1)
        self.assertIsNone(a.pending)

    def test_unknown_rule_rejected(self):
        with self.assertRaises(ValueError):
            RevisionInvestigator(Observation(0,0,0),check_rule='mystery')
