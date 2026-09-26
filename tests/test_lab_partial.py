import itertools
import unittest
from unittest.mock import patch
from artificial_scientist.lab_guided import guided_propose
from artificial_scientist.lab_models import Model, fit


def fixture(extra=0., collinear=False, constant=False):
    evidence, rows = [], []
    base_terms = ('one',) if constant else (('v','u') if collinear else ('u',))
    for step,(u,v) in enumerate(itertools.product((-1.,0.,1.),repeat=2)):
        if collinear:v=2*u
        inputs=dict(u=u,v=v,p=0.,lag_u=0.,one=1.)
        residual=(2+extra)*u+.3*v+(1. if constant else 0.)
        for axis in ('x','y'):
            evidence.append(dict(step=step,axis=axis,inputs=inputs,model_id='+'.join(base_terms) if not constant else '1',
                coefficient_version=[0.]*len(base_terms),prediction=0.,observed=residual,residual=residual,incumbent_epoch=1))
            rows.append((inputs,residual))
    base=Model(base_terms,tuple(0. for _ in base_terms))
    return evidence,rows,base


class PartialTest(unittest.TestCase):
    def run_screen(self,extra=0.,partial=True,**kwargs):
        evidence,rows,base=fixture(extra,**kwargs);audit={}
        new,_=guided_propose(rows,{base.id},base,evidence,audit=audit,partial=partial)
        return audit,new

    def test_conditions_away_existing_signal_without_target_feature_quota(self):
        raw,_=self.run_screen(partial=False)
        conditioned,new=self.run_screen()
        scores=lambda a:{r['feature']:r['score'] for r in a['diagnosis']['associations'] if r['axis']=='x'}
        self.assertGreater(scores(raw)['u'],scores(raw)['v'])
        self.assertAlmostEqual(scores(conditioned)['u'],0.)
        self.assertAlmostEqual(scores(conditioned)['v'],1.)
        self.assertIn('v+u',[m.id for m in new])
        for r in conditioned['diagnosis']['associations']:
            old=next(o for o in raw['diagnosis']['associations'] if o['axis']==r['axis'] and o['feature']==r['feature'])
            self.assertEqual(r['raw_score'],old['score'])

    def test_partial_scores_invariant_to_extra_incumbent_component(self):
        a,_=self.run_screen(extra=0.)
        b,_=self.run_screen(extra=3.)
        for ra,rb in zip(a['diagnosis']['associations'],b['diagnosis']['associations']):
            if ra['feature']!='1':
                self.assertAlmostEqual(ra['score'],rb['score'],places=10)

    def test_constant_and_collinear_span_do_not_create_signal(self):
        a,_=self.run_screen(collinear=True)
        self.assertTrue(all(abs(r['score'])<1e-8 for r in a['diagnosis']['associations']))
        b,_=self.run_screen(constant=True)
        self.assertTrue(all(r['score']==0 for r in b['diagnosis']['associations'] if r['feature']=='1'))

    def test_accounting_and_fit_cap(self):
        records,rows,base=fixture();audit={}
        with patch('artificial_scientist.lab_guided.fit',wraps=fit) as spy:
            guided_propose(rows,{base.id},base,records,audit=audit,partial=True)
        self.assertEqual(audit['candidate_fits'],spy.call_count)
        self.assertLessEqual(spy.call_count,8)
        self.assertEqual(audit['feature_evaluations'],20*len(records))
        self.assertEqual(audit['projection_feature_evaluations'],2*len(records))
        self.assertGreater(audit['projection_calls'],0)
        original,_=self.run_screen(partial=False)
        self.assertEqual(original['projection_calls'],0)
        self.assertEqual(original['projection_feature_evaluations'],0)


if __name__=='__main__':unittest.main()
