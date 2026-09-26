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


if __name__=='__main__':
    unittest.main()
