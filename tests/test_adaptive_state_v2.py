import json
import math
import tempfile
import unittest
from pathlib import Path
from artificial_scientist.adaptive_state_v2 import (
    CONDITIONS, MatchedMixture, ReversibleContext, bank, diagnostic, generate, run, simulate)
from artificial_scientist.sequence_worlds import generate as old_generate

ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'experiments/adaptive_state_v2.json').read_text())


class Expert:
    def __init__(self,p,lags):self.p,self.lags=p,lags
    def predict(self):return self.p
    def update(self,y):pass
    def storage(self):return 10


class ReversibleTests(unittest.TestCase):
    def controlled(self):
        m=ReversibleContext(window=4,every=2,threshold=1)
        m.models=[Expert(.5,(1,)),Expert(.5,(1,))]+[Expert(.9,(1,k)) for k in range(2,6)]
        return m

    def test_expand_then_contract_and_next_tick(self):
        m=self.controlled()
        for _ in range(3):self.assertIsNone(m.update(1))
        self.assertEqual(m.predict(),.5)
        e=m.update(1)
        self.assertEqual((e['kind'],e['effective_tick'],e['selected_expert']),('expand',4,2))
        self.assertEqual(m.predict(),.9)
        m.update(0);e=m.update(0)
        self.assertEqual(e['kind'],'contract')
        self.assertEqual(e['effective_tick'],6)
        self.assertEqual(m.active,0)
        self.assertEqual(m.predict(),.5)

    def test_fast_simple_blocks_sparse_and_can_swap(self):
        m=self.controlled();m.models[1].p=.95
        for _ in range(3):self.assertIsNone(m.update(1))
        e=m.update(1)
        self.assertEqual((e['kind'],m.active),('speed',1))
        for _ in range(4):m.update(0)
        self.assertEqual(m.active,0)

    def test_strict_threshold_ties_and_preupdate_losses(self):
        m=self.controlled();m.threshold=0
        for expert in m.models:expert.p=.5
        for _ in range(4):self.assertIsNone(m.update(1))
        self.assertEqual(m.active,0)
        m=ReversibleContext(window=4,every=2)
        ps=[x.predict() for x in m.models];m.update(1)
        for losses,p in zip(m.losses,ps):self.assertEqual(losses[-1],-math.log(p))

    def test_bank_identity_mixture_and_storage(self):
        m=ReversibleContext();mix=MatchedMixture()
        self.assertEqual([(x.lags,x.discount) for x in m.models],[(x.lags,x.discount) for x in mix.models])
        for y in [1,0,1,1,0]*30:
            m.update(y);mix.update(y)
            self.assertAlmostEqual(sum(mix.weights),1)
            self.assertEqual(m.storage(),sum(x.storage() for x in m.models)+768+6)
            self.assertEqual(mix.storage(),sum(x.storage() for x in mix.models)+6)
            self.assertTrue(all(len(x)<=128 for x in m.losses))

    def test_balanced_worlds_old_equivalence_and_prefix(self):
        for seed in range(5):
            prior,lag=old_generate(seed,'structural',120,60)
            self.assertEqual(prior,generate(seed,'structural'+str(lag),120,60)[0])
            for condition in CONDITIONS:
                stream,actual=generate(seed,condition,120,60)
                self.assertEqual(stream[:60],generate(seed,'stable',120,60)[0][:60])
                if condition in ('stable','parameter','noise'):
                    self.assertEqual(stream,old_generate(seed,condition,120,60)[0])
                else:self.assertEqual(actual,int(condition[-1]))

    def test_replay_causality_and_paired_streams(self):
        c=dict(CONFIG,steps=32,change_at=16,seeds=[0],gain_window=8,check_every=8)
        a=simulate(c);b=simulate(c)
        self.assertEqual(a[:3],b[:3]);self.assertEqual(a[4],b[4])
        self.assertEqual(len(a[0]),32*42)
        for tick in range(32):
            for cond in CONDITIONS:
                rows=[r for r in a[0] if r['tick']==tick and r['condition']==cond]
                self.assertEqual(len({r['outcome'] for r in rows}),1)
                if tick==0:
                    for r in rows:self.assertAlmostEqual(r['probability'],.5)
                if tick<16:
                    p=next(r['probability'] for r in rows if r['baseline']=='v2')
                    stable=next(r['probability'] for r in a[0] if r['tick']==tick and r['condition']=='stable' and r['baseline']=='v2')
                    self.assertEqual(p,stable)
        self.assertEqual(len(a[4]),14)
        self.assertTrue(all(0<=d['correct_fraction_after']<=1 for d in a[4] if d['correct_fraction_after'] is not None))

    def test_scope_and_bounds(self):
        c=dict(CONFIG,steps=32,change_at=16,seeds=[0],check_every=8)
        for changed in [dict(seeds=[1000]),dict(fast_discount=0),dict(steps=10000,seeds=list(range(20)))]:
            with self.assertRaises(ValueError):simulate(dict(c,**changed))
        with tempfile.TemporaryDirectory(dir=ROOT/'results') as tmp:
            p=Path(tmp);f=p/'config.json';f.write_text(json.dumps(c))
            run(f,p/'out')
            meta=json.loads((p/'out/metadata.json').read_text())
            self.assertIn('artificial_scientist/adaptive_state_v2.py',meta['source_sha256'])
            self.assertTrue((p/'out/decisions.json').exists())
            with self.assertRaises(FileExistsError):run(f,p/'out')
            with self.assertRaises(ValueError):run(f,ROOT.parent/'outside')
