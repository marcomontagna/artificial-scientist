"""Independent algebra and synthetic fixtures; no smoke or study sampling."""
import copy
import hashlib
import inspect
import json
import math
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from artificial_scientist import equation_confirmation as ec
from artificial_scientist import equation_discovery as ed


class ConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.config = ec.fixed_config()

    def fixture(self):
        axis = [-1., -1/3, 1/3, 1.]
        audit = [(x,u,1+2*x) for x in axis for u in axis]
        candidate = dict(support=[0,1],coefficients=[1.,2.,0.,0.,0.,0.])
        return candidate,audit

    def test_null_mle_and_log_ratio_have_independent_closed_form(self):
        candidate,audit = self.fixture()
        result = ec.term_evidence(candidate,audit,sigma=1.)
        null = result['terms'][1]['null_fit']
        # x is orthogonal to all five remaining columns on this symmetric product grid.
        expected_sse = 4*sum(x*x for x,u,y in audit)
        self.assertAlmostEqual(null['sse'],expected_sse,places=11)
        self.assertEqual(null['support'],[0,2,3,4,5])
        self.assertAlmostEqual(null['coefficients'][0],1.,places=12)
        for j in (1,2,3,4,5):
            self.assertAlmostEqual(null['coefficients'][j],0.,places=12)
        log_density = lambda predicted: sum(-.5*math.log(2*math.pi)-.5*(y-p)**2 for (_,_,y),p in zip(audit,predicted))
        q = [ed.predict(candidate['coefficients'],x,u) for x,u,_ in audit]
        p = [ed.predict(null['coefficients'],x,u) for x,u,_ in audit]
        self.assertAlmostEqual(result['terms'][1]['log_e'],log_density(q)-log_density(p),places=12)
        self.assertAlmostEqual(result['terms'][1]['log_e'],expected_sse/2,places=12)
        self.assertTrue(all(t['log_e'] <= 1e-8 for t in result['terms'] if t['term_index'] not in candidate['support']))

    def test_audit_null_maximizes_likelihood_and_full_five_terms_used(self):
        rng = random.Random(11)
        audit = [(rng.uniform(-1,1),rng.uniform(-1,1),rng.gauss(0,.1)) for _ in range(16)]
        candidate = dict(support=[],coefficients=[0.]*6)
        evidence = ec.term_evidence(candidate,audit)
        for j,t in enumerate(evidence['terms']):
            self.assertEqual(t['null_fit']['support'],[k for k in range(6) if k!=j])
            fixed = [.3,-.2,.4,.1,-.15,.08]
            fixed[j] = 0.
            fixed_sse = sum((y-ed.predict(fixed,x,u))**2 for x,u,y in audit)
            self.assertLessEqual(t['null_fit']['sse'],fixed_sse+1e-12)
            residuals = [y-ed.predict(t['null_fit']['coefficients'],x,u) for x,u,y in audit]
            for k in t['null_fit']['support']:
                self.assertAlmostEqual(sum(ed.basis(x,u)[k]*r for (x,u,y),r in zip(audit,residuals)),0.,places=12)
            self.assertLessEqual(t['log_e'],1e-8)
        before = copy.deepcopy((candidate,audit))
        ec.term_evidence(candidate,audit)
        self.assertEqual((candidate,audit),before)
        with patch.object(ed,'least_squares',return_value=dict(sse=1e6)):
            with self.assertRaisesRegex(ArithmeticError,'nonselected'):
                ec.term_evidence(candidate,audit)
        with self.assertRaises(ArithmeticError):
            ec.term_evidence(candidate,[(0.,0.,1.)]*16)

    def test_threshold_claim_sets_and_noise_outside_semantics(self):
        threshold = math.log(120)
        evidence = {'terms':[dict(log_e=-1.) for _ in range(6)]}
        evidence['terms'][0]['log_e'] = threshold
        evidence['terms'][2]['log_e'] = threshold-1e-12
        original = copy.deepcopy(evidence)
        claims = ec.reporting_claims([0,2],evidence,True)
        self.assertEqual(claims,dict(raw=[0,2],adequacy_only=[0,2],confirmed=[0],combined=[0]))
        self.assertEqual(ec.reporting_claims([0,2],evidence,False)['confirmed'],[0])
        self.assertEqual(ec.reporting_claims([0,2],evidence,False)['combined'],[])
        self.assertEqual(evidence,original)
        noise = ec.claim_metrics([],[])
        self.assertTrue(noise['exact_match'])
        self.assertIsNone(noise['all_true_terms_claimed'])
        self.assertIsNone(noise['true_term_recall'])
        self.assertTrue(ec.claim_metrics([1],[])['any_false_term'])
        self.assertTrue(all(v is None for v in ec.claim_metrics([0,1],None).values()))
        metrics = ec.claim_metrics([0,1],[0,2])
        self.assertTrue(metrics['any_false_term'])
        self.assertEqual(metrics['true_term_recall'],.5)
        self.assertFalse(metrics['all_true_terms_claimed'])

    def test_audit_cannot_refit_candidate_or_change_predictions(self):
        streams = ed.shared_streams(7,self.config)
        worlds = ed.world_catalog(7,self.config)
        first = ec.episode_record(7,'affine',worlds['affine'],streams,self.config)
        changed = copy.deepcopy(streams)
        changed['audit'] = [(x,u,n+1.) for x,u,n in changed['audit']]
        second = ec.episode_record(7,'affine',worlds['affine'],changed,self.config)
        for method in ed.METHODS:
            self.assertEqual(first['methods'][method]['coefficients'],second['methods'][method]['coefficients'])
            self.assertEqual(first['methods'][method]['audit_predictions'],second['methods'][method]['audit_predictions'])
        self.assertNotEqual(first['confirmation']['candidate_audit_sse'],second['confirmation']['candidate_audit_sse'])
        self.assertEqual(first['confirmation']['audit_predictions'],first['methods']['sparse']['audit_predictions'])
        self.assertEqual(list(inspect.signature(ec.term_evidence).parameters),
                         ['candidate','audit','sigma','rank_tolerance','violation_tolerance'])
        for name in ('noise_only','sine'):
            row = ec.episode_record(11,name,ed.world_catalog(11,self.config)[name],ed.shared_streams(11,self.config),self.config)
            if name == 'noise_only':
                self.assertIsNone(row['confirmation']['all_true_terms_confirmed'])
            else:
                self.assertIsNone(row['confirmation']['claim_metrics']['confirmed']['any_false_term'])
                self.assertIn('no validity guarantee',row['confirmation']['flag_interpretation'])

    def synthetic_summary(self):
        return dict(completed_keys=[[s,w] for s in self.config['seeds'] for w in ed.WORLDS],
                    cells=[dict(world=w,strategies={'confirmed':{'any_false_term':{'count':5}}},
                                confirmation_rate_among_selected_true=.8) for w in ec.IN_CLASS])

    def test_complete_screen_separates_validity_pause_from_power_shortfall(self):
        summary = self.synthetic_summary()
        self.assertTrue(ec.decision(summary,self.config,True)['diagnostic_screen_pass'])
        lower_power = copy.deepcopy(summary)
        lower_power['cells'][0]['confirmation_rate_among_selected_true'] = .79
        decision = ec.decision(lower_power,self.config,True)
        self.assertFalse(decision['diagnostic_screen_pass'])
        self.assertFalse(decision['pause_stage3_pending_diagnosis'])
        lower_power['cells'][0]['confirmation_rate_among_selected_true'] = None
        self.assertFalse(ec.decision(lower_power,self.config,True)['diagnostic_screen_pass'])
        for i in range(3):
            failed = copy.deepcopy(summary)
            failed['cells'][i]['strategies']['confirmed']['any_false_term']['count'] = 6
            self.assertTrue(ec.decision(failed,self.config,True)['pause_stage3_pending_diagnosis'])
        for keys in [summary['completed_keys'][:-1],summary['completed_keys']+[summary['completed_keys'][0]]]:
            result = ec.decision(dict(summary,completed_keys=keys),self.config,True)
            self.assertFalse(result['complete'])
            self.assertFalse(result['diagnostic_screen_pass'])
        self.assertFalse(ec.decision(summary,self.config,False)['diagnostic_screen_pass'])

    def test_summary_conditional_power_not_overall_recall(self):
        # Synthetic claims isolate missed selection from successful confirmation.
        c = dict(claim_sets={s:[0] for s in ec.STRATEGIES},
                 claim_metrics={s:ec.claim_metrics([0],[0,1]) for s in ec.STRATEGIES},
                 true_term_count=2,selected_true_terms=1,confirmed_true_terms=1,
                 all_true_terms_confirmed=False,adequate=True,unsupported_candidate_terms=0,
                 all_selected_terms_supported_and_locally_adequate=True,flag_interpretation='fixture',evidence_seconds=0.)
        rows = [dict(seed=7,world='affine',confirmation=c)]
        with patch.object(ed,'summarize',return_value={}):
            cell = ec.summarize(rows,self.config)['cells'][0]
        self.assertEqual(cell['selection_recall'],.5)
        self.assertEqual(cell['confirmation_rate_among_selected_true'],1.)
        self.assertEqual(cell['overall_true_term_recall'],.5)
        self.assertEqual(cell['all_true_terms_confirmed']['count'],0)

    def test_fixed_config_helpers_and_smoke_provenance(self):
        ec.validate_config(self.config)
        with self.assertRaises(ValueError):
            ec.validate_config(dict(self.config,e_threshold=60))
        hashes = ec.source_hashes()
        self.assertIn('artificial_scientist/equation_discovery.py',hashes)
        self.assertIn('artificial_scientist/run.py',hashes)
        with tempfile.TemporaryDirectory(dir=ec.ROOT/'results/runs',prefix='equation_confirmation_fixture_') as d:
            path = Path(d)
            for name in ['config.json','episodes.jsonl','summary.json','decision.json']:
                (path/name).write_text('{}\n')
            meta = dict(status='completed',mode='smoke',completed_episodes=5,sources_unchanged=True,
                        source_sha256={'a':'b'},config_sha256='c',elapsed_seconds=.01,artifact_bytes=0,
                        artifact_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in path.iterdir()})
            def save():
                for _ in range(20):
                    text=json.dumps(meta)
                    size=sum(p.stat().st_size for p in path.iterdir() if p.name!='metadata.json')+len(text.encode())
                    if size==meta['artifact_bytes']:
                        (path/'metadata.json').write_text(text)
                        return
                    meta['artifact_bytes']=size
                self.fail('fixture byte count did not stabilize')
            save()
            evidence=ec.verify_smoke(path,'c',{'a':'b'},self.config)
            self.assertAlmostEqual(evidence['projected_full_seconds'],1.5)
            with self.assertRaises(FileExistsError): ec.output_scope(path)
            with self.assertRaises(ValueError): ec.output_scope(ec.ROOT/'bad')
            with self.assertRaises(ValueError): ec.verify_smoke(path,'wrong',{'a':'b'},self.config)
            meta['elapsed_seconds']=.5
            save()
            with self.assertRaises(RuntimeError): ec.verify_smoke(path,'c',{'a':'b'},self.config)
            meta['elapsed_seconds']=.01
            save()
            with self.assertRaises(RuntimeError): ec.verify_smoke(path,'c',{'a':'b'},dict(self.config,smoke_projection_limit_bytes=1))
            (path/'summary.json').write_text('tampered')
            with self.assertRaises(ValueError): ec.verify_smoke(path,'c',{'a':'b'},self.config)

    def test_numerical_failure_preserves_partial_no_study_sampling(self):
        with tempfile.TemporaryDirectory(dir=ec.ROOT/'results/runs',prefix='equation_confirmation_fixture_') as d:
            path=Path(d); output=path/'fresh'; cfg=path/'config.json'
            cfg.write_text(json.dumps(self.config))
            fixture_worlds=ed.world_catalog(7,self.config)
            fixture_streams=ed.shared_streams(7,self.config)
            with patch.object(ec,'output_scope',return_value=output), \
                 patch.object(ed,'world_catalog',return_value=fixture_worlds), \
                 patch.object(ed,'shared_streams',return_value=fixture_streams), \
                 patch.object(ec,'term_evidence',side_effect=ArithmeticError('forced fixture null failure')):
                with self.assertRaises(ArithmeticError): ec.run(cfg,output,smoke=True)
            meta=json.loads((output/'metadata.json').read_text())
            result=json.loads((output/'decision.json').read_text())
            self.assertEqual(meta['status'],'failed_partial')
            self.assertEqual(meta['completed_episodes'],0)
            self.assertFalse(result['diagnostic_screen_pass'])
            self.assertTrue(result['pause_stage3_pending_diagnosis'])


if __name__ == '__main__':
    unittest.main()
