"""Synthetic seeds7/11 only; no study or smoke sampling."""
import copy
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from artificial_scientist import equation_revision as r
from artificial_scientist import equation_domain as dm


class RevisionTests(unittest.TestCase):
    def setUp(self):
        self.config=r.fixed_config()

    def data(self,seed=7,world='medium_x'):
        law=r.world_catalog(seed)[world]
        return {k:[(x,u,r.truth(law,x,u)+error) for x,u,error in rows] for k,rows in r.streams(seed,self.config).items()}

    def test_generic_qr_noisy_ols_and_rank(self):
        data=self.data()['b']
        fit=r.fit(data,list(range(8)))
        residuals=[y-r.predict(fit['coefficients'],x,u) for x,u,y in data]
        for j in range(8):
            self.assertAlmostEqual(sum(r.features(x,u)[j]*e for (x,u,_),e in zip(data,residuals)),0.,places=10)
        with self.assertRaises(ArithmeticError):
            r.fit([(0.,0.,1.)]*24,[0,1])
        empty=r.fit(data,[])
        self.assertEqual(empty['coefficients'],[0.]*8)
        self.assertAlmostEqual(empty['sse'],sum(y*y for _,_,y in data))
        # Independent intercept-only predictive covariance: I+11^T/n.
        constant=r.fit(data,[0])
        v=dm.predictive_covariance(constant['r'],[[1.]]*24,.05)
        self.assertAlmostEqual(v[0][0],.05**2*(1+1/24))
        self.assertAlmostEqual(v[0][1],.05**2/24)

    def test_even_tails_and_exact_z_se(self):
        self.assertEqual(r.log_survival(0,24),0.)
        direct=math.exp(-1)*sum(1/math.factorial(k) for k in range(12))
        self.assertAlmostEqual(math.exp(r.log_survival(2,24)),direct,places=14)
        self.assertNotEqual(r.log_survival(24,16),r.log_survival(24,24))
        with self.assertRaises(ArithmeticError):
            r.log_survival(1,23)
        d=self.data()['d']
        shared=r.shared_d_tests(d)
        # Residualize each column against the other seven: SE=sigma/||residualized column||.
        for j,test in enumerate(shared['exact_tests']):
            null=shared['null_fits'][j]
            self.assertEqual(null['support'],[i for i in range(8) if i!=j])
            column_data=[(x,u,r.features(x,u)[j]) for x,u,_ in d]
            projected=r.fit(column_data,[i for i in range(8) if i!=j])
            expected=.05/math.sqrt(projected['sse'])
            self.assertAlmostEqual(test['se'],expected,places=11)
            self.assertEqual(test['p_value'],math.erfc(abs(test['z'])/math.sqrt(2)))
            self.assertAlmostEqual((null['sse']-shared['full_fit']['sse'])/(2*.05**2),test['z']**2/2,places=9)

    def test_567_stream_keys_sites_and_budget(self):
        self.assertEqual(len(r.stream_keys(self.config)),567)
        with self.assertRaises(ValueError):
            r.stream_keys(dict(self.config,a_noise_offset=self.config['a_input_offset']+2))
        data=r.streams(11,self.config)
        self.assertEqual([len(data[k]) for k in ('a','c','b','d')],[24,16,24,24])
        self.assertEqual(sum(map(len,data.values())),88)
        for rows in data.values():
            self.assertEqual(len({(x,u) for x,u,_ in rows}),len(rows))

    def test_trigger_selection_refit_and_frozen_d(self):
        data=self.data(world='strong_x')
        initial=r.choose_revision(data['a'],data['c'])
        self.assertEqual(initial['candidate_sha256_before'],initial['candidate_sha256_after'])
        altered_c=[(x,u,y+4*x**3) for x,u,y in data['c']]
        changed=r.choose_revision(data['a'],altered_c)
        self.assertEqual(initial['equation'],changed['equation'])
        self.assertNotEqual(initial['check']['q'],changed['check']['q'])
        fitted,models=r.candidates(data['a'],data['c'],data['b'],initial)
        self.assertEqual([m['support'] for m in models],r.SUPPORTS)
        self.assertEqual(fitted['always_large_pooled']['n'],64)
        self.assertEqual(fitted['pooled_bic']['n'],64)
        for name in ('revise_once','never_revise','always_large'):
            self.assertEqual(fitted[name]['n'],24)
        self.assertEqual(fitted['never_revise'],r.fit(data['b'],r.BASE))
        shared=r.shared_d_tests(data['d'])
        before=copy.deepcopy(fitted)
        for name,candidate in fitted.items():
            check=r.final_check(candidate,data['d'],name,shared)
            self.assertEqual(check['candidate_sha256_before'],check['candidate_sha256_after'])
            self.assertEqual(check['predictions_sha256_before'],check['predictions_sha256_after'])
            self.assertTrue(set(check['e_claims'])<=set(check['exact_claims']))
            for j,log_e in enumerate(check['log_e']):
                self.assertLessEqual(log_e,shared['exact_tests'][j]['z']**2/2+1e-8)
                self.assertAlmostEqual(log_e,(shared['null_fits'][j]['sse']-check['candidate_sse'])/(2*.05**2))
            if name=='pooled_bic':
                self.assertIsNone(check['whole']['q'])
                self.assertIsNone(check['whole']['rejected'])
            else:
                self.assertEqual(check['whole']['df'],24)
        self.assertEqual(fitted,before)
        original_check=r.whole_check
        def mutating_check(candidate,observations,sigma=.05):
            result=original_check(candidate,observations,sigma)
            candidate['coefficients'][0]+=.001
            return result
        with patch.object(r,'whole_check',side_effect=mutating_check):
            with self.assertRaisesRegex(ArithmeticError,'mutated'):
                r.final_check(copy.deepcopy(fitted['always_large']),data['d'],'always_large',shared)
        changed_d=[(x,u,y+.1) for x,u,y in data['d']]
        changed_shared=r.shared_d_tests(changed_d)
        changed_check=r.final_check(fitted['always_large'],changed_d,'always_large',changed_shared)
        self.assertEqual(changed_check['candidate_sha256_before'],r.fingerprint(fitted['always_large']))
        self.assertEqual(fitted,before)
        self.assertLess(math.erfc(math.sqrt(math.log(160))),.05/8)
        # Adversarial shared null violates the algebraic upper bound and must fail.
        broken=copy.deepcopy(shared)
        broken['null_fits'][0]['sse']+=100
        with self.assertRaises(ArithmeticError):
            r.final_check(fitted['always_large'],data['d'],'always_large',broken)

    def test_controls_metrics_and_nonmutating_truth(self):
        shared=r.streams(7,self.config)
        worlds=r.world_catalog(7)
        rows=[r.episode_record(7,name,worlds[name],shared,self.config) for name in ('quadratic','noise')]
        r.assert_controls(rows,self.config)
        summary=r.summarize(rows,self.config,True)
        for cell in summary['cells']:
            self.assertIn('outer_shell_mse',cell['means'])
            self.assertNotIn('extrapolation_mse',cell['means'])
            if cell['world']=='noise':
                for values in cell['recalls'].values():
                    self.assertIsNone(values['pooled_all_true_recall'])
                    self.assertIsNone(values['mean_ratios']['all_true_recall'])
        rows[-1]['initial']['check']['q']+=1
        with self.assertRaises(ArithmeticError):
            r.assert_controls(rows,self.config)
        rec=rows[0]['pipelines']['revise_once']
        original=copy.deepcopy(rec)
        metrics=r.evaluate(rec['candidate'],rec['check'],worlds['exponential'])
        self.assertIsNone(metrics['true_count'])
        self.assertIsNone(metrics['exact']['all_true_recall'])
        self.assertEqual(rec,original)

    def test_hard_utility_warning_separate(self):
        cells=[]
        for world in r.WORLDS:
            for pipeline in r.PIPELINES:
                mse=.7 if pipeline=='revise_once' else 1.
                cells.append(dict(world=world,pipeline=pipeline,means={'outer_shell_mse':mse},initial_rejection={'count':7}))
        summary=dict(completed_keys=[[s,w] for s in self.config['seeds'] for w in r.WORLDS],cells=cells,budgets_valid=True,immutable=True,control_equality_checked=True)
        result=r.decision(summary,self.config,True)
        self.assertTrue(result['hard_integration_pass'])
        self.assertTrue(result['utility_screen_pass'])
        self.assertEqual(result['false_revision_warning_worlds'],['quadratic','noise'])
        for world in ('medium_x','strong_x'):
            changed=copy.deepcopy(summary)
            next(c for c in changed['cells'] if c['world']==world and c['pipeline']=='always_large_pooled')['means']['outer_shell_mse']=.6
            self.assertFalse(r.decision(changed,self.config,True)['utility_screen_pass'])
            self.assertTrue(r.decision(changed,self.config,True)['hard_integration_pass'])
        for flag in ('budgets_valid','immutable','control_equality_checked'):
            self.assertFalse(r.decision(dict(summary,**{flag:False}),self.config,True)['hard_integration_pass'])
        self.assertFalse(r.decision(dict(summary,completed_keys=summary['completed_keys'][:-1]),self.config,True)['hard_integration_pass'])

    def test_partial_failure_clean_full_provenance_resources(self):
        worlds=r.world_catalog(7)
        shared=r.streams(7,self.config)
        fixture=r.episode_record(7,'quadratic',worlds['quadratic'],shared,self.config)
        with tempfile.TemporaryDirectory(dir=r.ROOT/'results/runs',prefix='equation_revision_fixture_') as directory:
            parent=Path(directory)
            config_path=parent/'config.json'
            config_path.write_text(json.dumps(self.config))
            output=parent/'fresh'
            def record(seed,name,world,shared,config):
                value=copy.deepcopy(fixture)
                value.update(seed=7,world=name)
                return value
            with patch.object(r,'output_scope',return_value=output),patch.object(r,'world_catalog',return_value=worlds), \
                 patch.object(r,'streams',return_value=shared),patch.object(r,'episode_record',side_effect=record), \
                 patch.object(r,'assert_controls',side_effect=ArithmeticError('forced')):
                with self.assertRaises(ArithmeticError):
                    r.run(config_path,output,smoke=True)
            meta=json.loads((output/'metadata.json').read_text())
            self.assertEqual(meta['status'],'failed_partial')
            self.assertFalse(json.loads((output/'summary.json').read_text())['control_equality_checked'])
            self.assertFalse(json.loads((output/'decision.json').read_text())['hard_integration_pass'])
            with patch.object(r,'output_scope',return_value=parent/'uncreated'),patch.object(r,'verify_smoke',return_value={}), \
                 patch.object(r,'git_info',return_value=dict(dirty=True,revision='abc')):
                with self.assertRaisesRegex(RuntimeError,'clean committed'):
                    r.run(config_path,parent/'uncreated',smoke_evidence=output)
            self.assertFalse((parent/'uncreated').exists())
            meta.update(status='completed',mode='smoke',completed_episodes=8,elapsed_seconds=.01)
            def save():
                for _ in range(20):
                    text=json.dumps(meta)
                    size=sum(f.stat().st_size for f in output.iterdir() if f.name!='metadata.json')+len(text.encode())
                    if size==meta['artifact_bytes']:
                        (output/'metadata.json').write_text(text)
                        return
                    meta['artifact_bytes']=size
                self.fail('metadata convergence')
            save()
            r.verify_smoke(output,meta['config_sha256'],meta['source_sha256'],self.config)
            for setting in ('time','disk'):
                if setting=='time':
                    meta['elapsed_seconds']=1.
                    save()
                    settings=self.config
                else:
                    meta['elapsed_seconds']=.01
                    save()
                    settings=dict(self.config,smoke_projection_limit_bytes=1)
                with self.assertRaises(RuntimeError):
                    r.verify_smoke(output,meta['config_sha256'],meta['source_sha256'],settings)
            (output/'summary.json').write_text('tampered')
            with self.assertRaises(ValueError):
                r.verify_smoke(output,meta['config_sha256'],meta['source_sha256'],self.config)
            with self.assertRaises(FileExistsError):
                r.output_scope(parent)


if __name__=='__main__':
    unittest.main()
