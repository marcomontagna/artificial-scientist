"""Synthetic7/11 fixtures for one immutable equation pipeline."""
import copy
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from artificial_scientist import equation_pipeline as p
from artificial_scientist import equation_discovery as ed
from artificial_scientist import equation_domain as d


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.config=p.fixed_config()

    def fixture(self,seed=7):
        world=p.world_catalog(seed)['strong_affine']
        shared=p.streams(seed,self.config)
        return {label:[(x,u,d.truth(world,x,u)+noise) for x,u,noise in rows] for label,rows in shared.items()}

    def test_all441_rng_keys_budgets_and_paired_weak_laws(self):
        self.assertEqual(len(p.stream_keys(self.config)),441)
        self.assertEqual(len(set(p.stream_keys(self.config))),441)
        collision=dict(self.config,a_noise_offset=self.config['a_input_offset']+2)
        with self.assertRaises(ValueError):
            p.stream_keys(collision)
        data=p.streams(7,self.config)
        self.assertEqual([len(data[k]) for k in ('a','b','c')],[24,24,16])
        self.assertNotEqual(data['a'],data['b'])
        for label in ('a','b'):
            for i in range(0,24,2):
                self.assertEqual(data[label][i][:2],data[label][i+1][:2])
                self.assertNotEqual(data[label][i][2],data[label][i+1][2])
        laws=p.world_catalog(11)
        for kind in ('affine','quadratic'):
            self.assertEqual(laws['weak_'+kind]['coefficients'],[.1*x for x in laws['strong_'+kind]['coefficients']])

    def test_independent_refit_allocation_and_c_immutability(self):
        data=self.fixture()
        candidates=p.fit_candidates(data['a'],data['b'])
        changed=p.fit_candidates(data['a'],[(x,u,y+.2) for x,u,y in data['b']])
        selected=candidates['selected_refit']
        self.assertEqual(selected['selection'],changed['selected_refit']['selection'])
        self.assertNotEqual(selected['equation']['coefficients'],changed['selected_refit']['equation']['coefficients'])
        self.assertEqual(selected['fit_observations'],24)
        self.assertEqual(candidates['fixed_full']['fit_observations'],48)
        self.assertEqual(candidates['pooled_bic']['fit_observations'],48)
        self.assertNotEqual(selected['selection']['chosen']['coefficients'],selected['equation']['coefficients'])
        before=copy.deepcopy(candidates)
        first=p.check_candidate(selected,data['c'],'selected_refit')
        second=p.check_candidate(selected,[(x,u,y+1) for x,u,y in data['c']],'selected_refit')
        self.assertEqual(candidates,before)
        self.assertEqual(first['predictions'],second['predictions'])
        self.assertEqual(first['candidate_sha256_before'],first['candidate_sha256_after'])
        self.assertNotEqual(first['adequacy']['q'],second['adequacy']['q'])
        pooled=p.check_candidate(candidates['pooled_bic'],data['c'],'pooled_bic')
        self.assertEqual(pooled['adequacy']['status'],'unavailable_post_selection')
        for key in ('q','log_p','p_value','rejected'):
            self.assertIsNone(pooled['adequacy'][key])
        self.assertIsNone(pooled['qualified_nonempty'])

    def test_selected_empty_full_covariance_and_term_statistic(self):
        data=self.fixture()
        design=[ed.basis(x,u) for x,u,_ in data['b']]
        audit=[ed.basis(x,u) for x,u,_ in data['c']]
        r=p.selected_r(design,[0])
        covariance=d.predictive_covariance(r,[[row[0]] for row in audit],.05)
        self.assertAlmostEqual(covariance[0][0],.05**2*(1+1/24))
        self.assertAlmostEqual(covariance[0][1],.05**2/24)
        empty=d.predictive_covariance([], [[] for _ in audit],.05)
        self.assertEqual(empty[0][1],0)
        self.assertEqual(empty[0][0],.05**2)
        full=p.selected_r(design,list(range(6)))
        self.assertEqual(full,d.training_r(design))
        fit=ed.least_squares(design,[y for _,_,y in data['b']],[])
        candidate=dict(equation=fit,fitted_design=design)
        result=p.check_candidate(candidate,data['c'],'selected_refit')
        self.assertFalse(result['qualified_nonempty'])
        self.assertEqual(result['confirmed_terms'],[])
        self.assertAlmostEqual(result['adequacy']['q'],sum(y*y for _,_,y in data['c'])/.05**2,places=8)
        for evidence in result['term_evidence']['terms']:
            null=ed.least_squares(audit,[y for _,_,y in data['c']],[j for j in range(6) if j!=evidence['term_index']])
            self.assertAlmostEqual(evidence['log_e'],(null['sse']-sum(y*y for _,_,y in data['c']))/(2*.05**2),places=8)
            self.assertLessEqual(evidence['log_e'],1e-8)
        with self.assertRaises(ArithmeticError):
            p.selected_r([ed.basis(0,0)]*24,[0,1])

    def test_controls_evaluator_denominators_and_qualification(self):
        laws=p.world_catalog(7)
        shared=p.streams(7,self.config)
        rows=[p.episode_record(7,w,laws[w],shared,self.config) for w in p.CONTROLS]
        p.assert_controls(rows,self.config)
        summary=p.summarize(rows,self.config,True)
        noise=next(c for c in summary['cells'] if c['world']=='noise_only' and c['pipeline']=='selected_refit')
        self.assertIsNone(noise['end_to_end_term_recall'])
        self.assertIsNone(noise['mean_recalls']['selection_recall'])
        for c in summary['cells']:
            self.assertEqual(c['sufficient']['n']+c['insufficient']['n'],0 if c['pipeline']=='pooled_bic' else 1)
        rows[-1]['pipelines']['fixed_full']['checks']['adequacy']['q']+=.1
        with self.assertRaises(ArithmeticError):
            p.assert_controls(rows,self.config)
        # Supplied omitted term produces insufficient span; outside truth has null recall.
        data=self.fixture()
        candidate=p.fit_candidates(data['a'],data['b'])['fixed_full']
        checks=p.check_candidate(candidate,data['c'],'fixed_full')
        metrics=p.evaluate(candidate,checks,laws['exponential'])
        self.assertFalse(metrics['sufficient'])
        self.assertIsNone(metrics['selection_recall'])
        outside=p.episode_record(7,'exponential',laws['exponential'],shared,self.config)
        for cell in p.summarize([outside],self.config)['cells']:
            self.assertIsNone(cell['total_true_terms'])
            self.assertIsNone(cell['confirmed_true_terms'])
        self.assertEqual(noise['total_true_terms'],0)
        self.assertEqual(noise['confirmed_true_terms'],0)

    def test_practical_vs_hard_gates(self):
        cells=[dict(world=w,pipeline=method,rates={'confirmed_any_false':{'count':6}},
                    end_to_end_term_recall=.8,sufficient={'count':8}) for w in p.WORLDS for method in p.PIPELINES]
        summary=dict(completed_keys=[[s,w] for s in self.config['seeds'] for w in p.WORLDS],cells=cells,
                     control_equality_checked=True,budgets_valid=True,immutable=True)
        self.assertTrue(p.decision(summary,self.config,True)['practical_screen_pass'])
        for w in p.CONTROLS:
            for method in p.PIPELINES:
                changed=copy.deepcopy(summary)
                next(c for c in changed['cells'] if c['world']==w and c['pipeline']==method)['rates']['confirmed_any_false']['count']=7
                result=p.decision(changed,self.config,True)
                self.assertFalse(result['practical_screen_pass'])
                self.assertTrue(result['hard_integration_pass'])
        for w in p.WORLDS[:2]:
            changed=copy.deepcopy(summary)
            next(c for c in changed['cells'] if c['world']==w and c['pipeline']=='selected_refit')['end_to_end_term_recall']=.79
            self.assertFalse(p.decision(changed,self.config,True)['practical_screen_pass'])
        changed=copy.deepcopy(summary)
        next(c for c in changed['cells'] if c['pipeline']=='fixed_full')['sufficient']['count']=9
        self.assertFalse(p.decision(changed,self.config,True)['practical_screen_pass'])
        self.assertTrue(p.decision(changed,self.config,True)['hard_integration_pass'])
        for flag in ('control_equality_checked','budgets_valid','immutable'):
            self.assertFalse(p.decision(dict(summary,**{flag:False}),self.config,True)['hard_integration_pass'])
        self.assertFalse(p.decision(dict(summary,completed_keys=summary['completed_keys'][:-1]),self.config,True)['hard_integration_pass'])

    def test_failed_control_run_and_resource_provenance(self):
        laws=p.world_catalog(7)
        shared=p.streams(7,self.config)
        fixture=p.episode_record(7,'strong_affine',laws['strong_affine'],shared,self.config)
        with tempfile.TemporaryDirectory(dir=p.ROOT/'results/runs',prefix='equation_pipeline_fixture_') as directory:
            parent=Path(directory)
            config_path=parent/'config.json'
            config_path.write_text(json.dumps(self.config))
            output=parent/'fresh'
            def record(seed,name,world,shared,config):
                result=copy.deepcopy(fixture)
                result.update(seed=7,world=name)
                return result
            with patch.object(p,'output_scope',return_value=output),patch.object(p,'world_catalog',return_value=laws), \
                 patch.object(p,'streams',return_value=shared),patch.object(p,'episode_record',side_effect=record), \
                 patch.object(p,'assert_controls',side_effect=ArithmeticError('forced control failure')):
                with self.assertRaises(ArithmeticError):
                    p.run(config_path,output,smoke=True)
            meta=json.loads((output/'metadata.json').read_text())
            self.assertEqual(meta['status'],'failed_partial')
            self.assertFalse(json.loads((output/'summary.json').read_text())['control_equality_checked'])
            self.assertFalse(json.loads((output/'decision.json').read_text())['hard_integration_pass'])
            with self.assertRaises(ValueError):
                p.verify_smoke(output,meta['config_sha256'],meta['source_sha256'],self.config)
            with self.assertRaises(FileExistsError):
                p.output_scope(parent)
            with self.assertRaises(ValueError):
                p.output_scope(p.ROOT/'wrong')
            # Synthetic complete metadata for provenance/resource guard checks; no experiment samples.
            meta.update(status='completed',mode='smoke',completed_episodes=8,elapsed_seconds=.01)
            def save():
                for _ in range(20):
                    text=json.dumps(meta)
                    size=sum(f.stat().st_size for f in output.iterdir() if f.name!='metadata.json')+len(text.encode())
                    if size==meta['artifact_bytes']:
                        (output/'metadata.json').write_text(text)
                        return
                    meta['artifact_bytes']=size
                self.fail('metadata fixture convergence')
            save()
            p.verify_smoke(output,meta['config_sha256'],meta['source_sha256'],self.config)
            meta['elapsed_seconds']=1.
            save()
            with self.assertRaises(RuntimeError):
                p.verify_smoke(output,meta['config_sha256'],meta['source_sha256'],self.config)
            meta['elapsed_seconds']=.01
            save()
            with self.assertRaises(RuntimeError):
                p.verify_smoke(output,meta['config_sha256'],meta['source_sha256'],dict(self.config,smoke_projection_limit_bytes=1))
            (output/'summary.json').write_text('tampered')
            with self.assertRaises(ValueError):
                p.verify_smoke(output,meta['config_sha256'],meta['source_sha256'],self.config)


if __name__=='__main__':
    unittest.main()
