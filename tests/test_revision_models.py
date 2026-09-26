import json
import math
import time
import unittest
from artificial_scientist.lab_api import Action,Observation,Transition
from artificial_scientist import revision_models as m


class VectorTests(unittest.TestCase):
    def history(self):
        history=[]
        before=Observation(0,0.,0.)
        vel=(0.,0.)
        for i in range(24):
            action=Action('push',angle=(i%4)*math.pi/2,magnitude=.3 if i%3 else 1.)
            push=(action.magnitude*math.cos(action.angle),action.magnitude*math.sin(action.angle))
            delta=(.6*vel[0]+.8*push[0],.2*vel[1]+.5*push[1])
            after=Observation(i+1,before.x+delta[0],before.y+delta[1])
            history.append(Transition(before,action,after))
            before,vel=after,delta
        return history

    def test_safety_budget_and_roundtrip(self):
        for term in ('hidden_world',('eval','p'),('mul','p'),('__import__','p')):
            with self.assertRaises(ValueError):
                m.VectorModel((term,),True,(1.,))
        with self.assertRaises(ValueError):
            m.VectorModel(m.VARIABLES[:5],True,(0.,)*5)
        with self.assertRaises(ValueError):
            m.VectorModel(('p',),True,(float('nan'),))
        term='p'
        for _ in range(14):
            term=('abs',term)
        with self.assertRaises(ValueError):
            m.nodes(term)
        model=m.VectorModel(('v',('mul','p','other_p')),False,((.2,.3),(.4,.5)))
        restored=m.VectorModel.from_snapshot(json.loads(json.dumps(model.snapshot())))
        self.assertEqual(model.snapshot(),restored.snapshot())
        self.assertEqual(model.parameter_count,4)

    def test_cross_axis_simultaneous_reset_wait_lag(self):
        model=m.VectorModel(('other_p',),True,(1.,))
        self.assertEqual(model.predict_tape(Observation(0,1.,2.),[],[Action('observe')]),[(3.,3.)])
        self.assertEqual(model.predict_tape(Observation(0,1.,2.),[],[Action('wait',ticks=2)]),[(6.,6.)])
        self.assertEqual(model.predict_tape(Observation(0,1.,2.),[],[Action('reset'),Action('observe')]),[(0.,0.),(0.,0.)])
        lag=m.VectorModel(('lag_u',),True,(1.,))
        tape=lag.predict_tape(Observation(0,0.,0.),[],[Action('push',magnitude=1.),Action('observe'),Action('observe')])
        self.assertEqual(tape,[(0.,0.),(1.,0.),(1.,0.)])
        self.assertEqual(lag.predict_tape(Observation(0,0.,0.),[],[Action('push',magnitude=1.),Action('wait',ticks=2)]),[(0.,0.),(1.,0.)])

    def test_paired_eligibility_own_and_other_inputs(self):
        history=self.history()
        pairs=m.training_rows(history)
        self.assertEqual(len(pairs),24)
        for x,y in pairs:
            self.assertEqual(x[0]['other_p'],y[0]['p'])
            self.assertEqual(x[0]['other_v'],y[0]['v'])
            self.assertEqual(x[0]['other_u'],y[0]['u'])
        a=Observation(0,0.,0.); b=Observation(3,1.,0.); c=Observation(4,2.,0.); d=Observation(5,3.,0.)
        special=[Transition(a,Action('wait',ticks=3),b),Transition(b,Action('observe'),c),Transition(c,Action('observe'),d)]
        self.assertEqual(len(m.training_rows(special)),1)

    def test_fit_shared_nesting_collinear_zero_and_reference(self):
        history=self.history()
        shared=m.fit_model(dict(terms=('v','u'),shared=True),history)
        untied=m.fit_model(dict(terms=('v','u'),shared=False),history)
        for got,expected in zip(untied.coefficients,((.6,.8),(.2,.5))):
            for x,y in zip(got,expected):
                self.assertAlmostEqual(x,y,places=3)
        def error(model):
            rows=(model.coefficients,model.coefficients) if model.shared else model.coefficients
            return sum((sum(c*m.value(t,inputs) for c,t in zip(rows[a],model.terms))-target)**2 for pair in m.training_rows(history) for a,(inputs,target) in enumerate(pair))
        self.assertLess(error(untied),error(shared))
        zero=m.fit_model(dict(terms=(),shared=False),[])
        self.assertEqual(zero.coefficients,((),()))
        collinear=m.fit_model(dict(terms=('one',('abs','one')),shared=True),history)
        self.assertTrue(all(math.isfinite(c) for c in collinear.coefficients))
        reference=m.linear_reference(history)
        self.assertEqual(reference.parameter_count,18)
        self.assertEqual(len(reference.terms),9)
        with self.assertRaises(ValueError):
            m.VectorModel.from_snapshot(reference.snapshot())

    def test_proposal_family_counts_and_deadline(self):
        history=self.history()
        incumbent=m.fit_model(dict(terms=('v','u'),shared=True),history)
        models,audit=m.propose(incumbent,history)
        self.assertLessEqual(len(models),3)
        self.assertTrue(all(not model.shared for model in models))
        self.assertEqual(audit['candidate_fits'],1+7+len(m.nonlinear_menu()))
        self.assertEqual(sum(f['candidates'] for f in audit['families']),audit['candidate_fits'])
        self.assertGreater(audit['feature_evaluations'],audit['candidate_fits'])
        self.assertEqual(audit['training_pairs'],24)
        self.assertEqual(len({model.id for model in models}),len(models))
        self.assertTrue(all(model.terms[:2]==incumbent.terms for model in models))
        with self.assertRaises(TimeoutError):
            m.propose(incumbent,history,deadline=time.process_time()-1)
        with self.assertRaises(TimeoutError):
            m.fit_model(incumbent,history,deadline=time.process_time()-1)




class HistoryOperatorTests(unittest.TestCase):
    def test_safe_bounds_and_nested_expression_roundtrip(self):
        for k in (0,17,-1,True,1.0,'2'):
            with self.subTest(k=k),self.assertRaises(ValueError):
                m.VectorModel((('lag','u',k),),True,(1.,))
        for t in (('lag','p',2),('lag','u'),('lag','u',2,3),('lag',('abs','u'),2)):
            with self.subTest(t=t),self.assertRaises(ValueError):m.nodes(t)
        term=('mul',('lag','other_u',16),('abs',('lag','u',3)))
        model=m.VectorModel((term,),False,((.5,),(.8,)))
        other=m.VectorModel.from_snapshot(json.loads(json.dumps(model.snapshot())))
        self.assertEqual(model.snapshot(),other.snapshot())
        self.assertIn('lag(other_u,16)',model.formula)
        self.assertIn('lag(u,3)',model.id)
        with self.assertRaises(ValueError):
            m.VectorModel(tuple(('lag','u',k) for k in range(1,6)),True,(0.,)*5)

    def test_every_delay_uses_transition_start_ticks_for_own_and_cross(self):
        for k in range(1,17):
            actions=[Action('push',magnitude=1.)]+[Action('observe')]*(k+1)
            for name,target in (('u',(1.,0.)),('other_u',(0.,1.))):
                model=m.VectorModel((('lag',name,k),),True,(1.,))
                tape=model.predict_tape(Observation(0,0.,0.),[],actions)
                self.assertEqual(tape[:k],[(0.,0.)]*k)
                self.assertEqual(tape[k:], [target,target])

    def test_wait_tick_memory_and_recorded_restart_equivalence(self):
        model=m.VectorModel((('lag','u',5),),True,(1.,))
        before=Observation(0,0.,0.)
        prefix=[Action('push',magnitude=1.),Action('wait',ticks=3)]
        history=[]
        for action in prefix:
            after=Observation(before.tick+action.cost,0.,0.)
            history.append(Transition(before,action,after));before=after
        suffix=[Action('observe'),Action('observe'),Action('wait',ticks=2)]
        full=model.predict_tape(Observation(0,0.,0.),[],prefix+suffix)
        restarted=model.predict_tape(before,history,suffix)
        self.assertEqual(restarted,full[len(prefix):])
        self.assertEqual(restarted,[(0.,0.),(1.,0.),(1.,0.)])
        for action in suffix[:2]:
            after=Observation(before.tick+1,0.,0.)
            history.append(Transition(before,action,after));before=after
        pairs=m.training_rows(history)
        # Wait and immediately following observation are excluded from fitting,
        # but their zero-input ticks still advance the lag buffer.
        self.assertEqual(len(pairs),2)
        self.assertEqual(m.value(('lag','u',5),pairs[-1][0][0]),1.)
        self.assertEqual(m.value(('lag','other_u',5),pairs[-1][1][0]),1.)

    def test_reset_and_cross_tape_isolation(self):
        model=m.VectorModel((('lag','u',4),),True,(1.,))
        start=Observation(0,0.,0.)
        history=[Transition(start,Action('push',magnitude=1.),Observation(1,0.,0.))]
        reset=Transition(history[-1].after,Action('reset'),Observation(9,0.,0.))
        future=[Action('wait',ticks=8),Action('observe')]
        self.assertEqual(model.predict_tape(reset.after,history+[reset],future),[(0.,0.)]*2)
        model.predict_tape(start,[],[Action('push',magnitude=1.),Action('wait',ticks=4)])
        self.assertEqual(model.predict_tape(start,[],future),[(0.,0.)]*2)
        self.assertEqual(model.predict_tape(history[-1].after,history,[Action('reset')]+future),[(0.,0.)]*3)

    def test_history_proposals_log_all_fits_without_extra_alternatives(self):
        history=VectorTests().history()
        incumbent=m.fit_model(dict(terms=('v','u'),shared=True),history)
        plain,pa=m.propose(incumbent,history)
        guided,ga=m.propose(incumbent,history,proposal_mode='history')
        self.assertLessEqual(len(guided),3)
        self.assertEqual(ga['candidate_fits'],pa['candidate_fits']+30)
        self.assertEqual(len(ga['candidate_scores']),ga['candidate_fits'])
        lagged=[r for r in ga['candidate_scores'] if any(isinstance(t,tuple) and t[0]=='lag' for t in r['terms'])]
        self.assertEqual(len(lagged),30)
        self.assertEqual({r['terms'][-1] for r in lagged},set(m.lag_menu()))
        self.assertNotIn('candidate_scores',pa)
        with self.assertRaises(ValueError):m.propose(incumbent,history,proposal_mode='unknown')

    def test_reference_cap_and_fitted_delay_on_synthetic_history(self):
        history=[];before=Observation(0,0.,0.);past=[]
        for i in range(32):
            action=Action('push',magnitude=.8 if i%5 in (0,2) else .2,angle=(i%3)*math.pi/2)
            impulse=m.old.impulse(action)
            old=past[-3] if len(past)>=3 else (0.,0.)
            after=Observation(i+1,before.x+.7*old[0],before.y+.4*old[1])
            history.append(Transition(before,action,after));before=after;past.append(impulse)
        fitted=m.fit_model(dict(terms=(('lag','u',3),),shared=False),history)
        self.assertAlmostEqual(fitted.coefficients[0][0],.7,places=3)
        self.assertAlmostEqual(fitted.coefficients[1][0],.4,places=3)
        reference=m.history_reference(history)
        self.assertEqual(len(reference.terms),39)
        self.assertEqual(reference.parameter_count,78)
        self.assertEqual(reference.fit_work['candidate_fits'],1)
        self.assertGreater(reference.fit_work['feature_evaluations'],0)
        restored=m.HistoryReference.from_snapshot(json.loads(json.dumps(reference.snapshot())))
        self.assertEqual(reference.snapshot(),restored.snapshot())
        with self.assertRaises(ValueError):m.VectorModel.from_snapshot(reference.snapshot())
        with self.assertRaises(ValueError):m.LinearReference.from_snapshot(reference.snapshot())
        with self.assertRaises(TimeoutError):m.history_reference(history,deadline=time.process_time()-1)


if __name__=='__main__':
    unittest.main()
