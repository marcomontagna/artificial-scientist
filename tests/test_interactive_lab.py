"""Synthetic fixtures only; no smoke390 or study400..439 execution."""
import copy
import json
import math
import random
import unittest
from pathlib import Path
from unittest.mock import patch

from artificial_scientist import interactive_lab as lab


def configuration():
    return json.loads((lab.ROOT/'experiments/interactive_lab_v0.json').read_text())


class InteractiveLabTests(unittest.TestCase):
    def test_library_and_truth_tables(self):
        config=configuration()
        lab.validate_config(config)
        hypotheses=lab.make_library(config)['hypotheses']
        self.assertEqual(len(hypotheses),35)
        self.assertEqual(len({tuple(h['probabilities']) for h in hypotheses}),35)
        self.assertTrue(all(h['probabilities'][8]==.5 for h in hypotheses))
        worlds=lab.make_worlds(config)
        self.assertEqual(len(worlds),6)
        for world in worlds:
            matching=[h for h in hypotheses if h['probabilities'][:8]==world['true_probabilities']]
            self.assertEqual(len(matching),0 if world['id']=='majority' else 1)
        self.assertEqual(lab.bits(5),[1,0,1])

    def test_exact_epig_matches_hypothetical_updates_without_mutation(self):
        config=configuration()
        for hybrid in (True,False):
            learner=lab.Learner(config,hybrid)
            for action,outcome in [(0,1),(3,0),(0,1),(7,0),(5,1)]:
                learner.observe(action,outcome)
            state=copy.deepcopy(vars(learner))
            actual=learner.epig_scores()
            before=sum(w*lab.entropy(p) for w,p in zip(config['query_weights'],learner.query_predictions()))
            for action in range(9):
                p=learner.predictive(action)
                expected=before
                for outcome,probability in [(1,p),(0,1-p)]:
                    alternative=copy.deepcopy(learner)
                    alternative.observe(action,outcome)
                    expected-=probability*sum(w*lab.entropy(q) for w,q in zip(config['query_weights'],alternative.query_predictions()))
                self.assertAlmostEqual(actual[action],expected,places=12)
                self.assertGreaterEqual(actual[action],0.)
            self.assertEqual(actual[8],0.)
            self.assertEqual(vars(learner),state)

    def test_analytical_two_hypothesis_and_beta_fixtures(self):
        config=configuration()
        for only_one in (False,True):
            low=[.2]*8 if not only_one else [.2]+[.5]*7
            high=[.8]*8 if not only_one else [.8]+[.5]*7
            library=[dict(id='low',label='low',probabilities=low+[.5]),
                     dict(id='high',label='high',probabilities=high+[.5])]
            learner=lab.Learner(config,False,library)
            expected=(math.log(2)-lab.entropy(.68))/(8 if only_one else 1)
            self.assertAlmostEqual(learner.epig_scores()[0],expected,places=12)
            if only_one:
                self.assertAlmostEqual(learner.epig_scores()[1],0.,places=12)
        beta=lab.Learner(config)
        beta.log_weights=[-math.inf]*35+[0.]
        expected=(math.log(2)-lab.entropy(2/3))/8
        for score in beta.epig_scores()[:8]:
            self.assertAlmostEqual(score,expected,places=12)
        # The same-action covariance is essential; omitting it would yield zero.
        self.assertGreater(expected,.007)

    def test_posterior_matches_batch_marginal_and_only_selected_beta_updates(self):
        config=configuration()
        learner=lab.Learner(config)
        history=[(0,1),(0,0),(3,1),(0,1)]
        for a,y in history:
            before=copy.deepcopy(learner.beta)
            learner.observe(a,y)
            self.assertAlmostEqual(sum(learner.weights()),1.,places=12)
            for other in range(8):
                if other!=a:
                    self.assertEqual(before[other],learner.beta[other])
        likelihoods=[math.prod(h['probabilities'][a] if y else 1-h['probabilities'][a]
                              for a,y in history)*.8/35 for h in learner.library]
        beta_marginal=1.
        for a in range(8):
            success=sum(y for action,y in history if action==a)
            failure=sum(1-y for action,y in history if action==a)
            beta_marginal*=math.exp(math.lgamma(1+success)+math.lgamma(1+failure)-math.lgamma(2+success+failure))
        likelihoods.append(.2*beta_marginal)
        for actual,value in zip(learner.weights(),likelihoods):
            self.assertAlmostEqual(actual,value/sum(likelihoods),places=12)
        state=copy.deepcopy(vars(learner))
        learner.observe(8,1)
        self.assertEqual(state,vars(learner))

    def test_evaluator_does_not_update_learner_or_supply_world_to_constructor(self):
        config=configuration()
        learner=lab.Learner(config)
        before=copy.deepcopy(vars(learner))
        worlds=lab.make_worlds(config)
        for world in worlds:
            state=lab.evaluate_state(learner,world,config)
            mass=state['query_metrics']['true_hypothesis_mass']
            self.assertEqual(mass is None,world['id']=='majority')
        self.assertEqual(before,vars(learner))
        self.assertNotIn('world',vars(learner))
        self.assertNotIn('truth',vars(learner))
        self.assertEqual(set(learner.config),{'noise_action','noise_probability','query_weights','negative_score_tolerance'})
        changed=copy.deepcopy(config)
        changed['worlds']=[]
        changed['primary_worlds']=[]
        changed['seeds']=[999]
        other=lab.Learner(changed)
        self.assertEqual(learner.query_predictions(),other.query_predictions())
        self.assertEqual(learner.epig_scores(),other.epig_scores())

    def test_noise_filter_ties_and_prediction_before_update_replay(self):
        config=configuration()
        learner=lab.Learner(config)
        with patch.object(learner,'epig_scores',return_value=[0.]*9):
            rng=random.Random(7)
            chosen=[lab.choose_action('hybrid_epig',learner,n,rng,config)[0] for n in range(40)]
            self.assertTrue(all(0<=a<8 for a in chosen))
            self.assertGreater(len(set(chosen)),1)
        fixture=copy.deepcopy(config)
        fixture['steps']=6
        world=lab.make_worlds(fixture)[0]
        episode=lab.episode_record(world,7,'hybrid_epig',fixture)
        replay=lab.Learner(fixture)
        self.assertEqual(len(episode['records']),7)
        for record in episode['records'][1:]:
            self.assertAlmostEqual(record['pre_action_probability'],replay.predictive(record['action']))
            replay.observe(record['action'],record['outcome'])
            self.assertEqual(record['query_probabilities'],replay.query_predictions())
        self.assertEqual(episode['noise_action_count'],0)
        self.assertEqual(set(episode['timing']),{'acquisition_seconds','prediction_seconds','update_seconds'})
        short=copy.deepcopy(fixture)
        short['steps']=3
        prefix=lab.episode_record(world,7,'hybrid_epig',short)
        self.assertEqual(prefix['records'],episode['records'][:4])

    def test_rng_keying_and_recorded_table_outcomes(self):
        config=configuration()
        fixture=copy.deepcopy(config)
        fixture['steps']=6
        uniforms=lab.observation_uniforms(11,fixture)
        rng=random.Random(5000003+11)
        self.assertEqual(uniforms,[[rng.random() for _ in range(9)] for _ in range(6)])
        worlds=lab.make_worlds(fixture)
        episodes=[lab.episode_record(w,11,'hybrid_random',fixture) for w in worlds[:2]]
        self.assertEqual([r['action'] for r in episodes[0]['records']],
                         [r['action'] for r in episodes[1]['records']])
        for world,episode in zip(worlds,episodes):
            for i,record in enumerate(episode['records'][1:]):
                a=record['action']
                self.assertEqual(record['outcome'],int(uniforms[i][a]<world['true_probabilities'][a]))
        rr=lab.episode_record(worlds[0],11,'hybrid_roundrobin',fixture)
        self.assertEqual([r['action'] for r in rr['records'][1:]],list(range(6)))

    def test_normalized_auc_seed_pairing_and_incomplete_decision(self):
        config=configuration()
        records=[dict(step=0)] + [dict(query_metrics=dict(excess_log_loss=n/100,excess_brier=0.,true_hypothesis_mass=.1),
                   fallback_weight=.2) for n in range(1,49)]
        episode=dict(world='lamp_a',seed=7,policy='hybrid_epig',records=records,
                     noise_action_count=0,timing=dict(acquisition_seconds=0.,prediction_seconds=0.,update_seconds=0.))
        row=lab.episode_summary(episode)
        self.assertAlmostEqual(row['auc_excess_log_loss'],.245)
        rows=[]
        for seed,delta in [(7,-.02),(11,-.04)]:
            for world in config['worlds']:
                for policy in config['policies']:
                    r=copy.deepcopy(row)
                    r.update(seed=seed,world=world['id'],policy=policy,
                             auc_excess_log_loss=.2+(delta if policy=='hybrid_epig' else 0.))
                    rows.append(r)
        summary=lab.summarize(rows,config)
        for paired in summary['paired_primary']:
            self.assertAlmostEqual(paired['mean_difference'],-.03)
            self.assertAlmostEqual(paired['seed_se'],.01)
            self.assertEqual(paired['seeds'],2)
        self.assertFalse(lab.decision(summary,config,True)['passed'])
        fixture=copy.deepcopy(config)
        fixture['seeds']=[7,11]
        self.assertTrue(lab.decision(summary,fixture,True)['passed'])
        self.assertFalse(lab.decision(summary,fixture,False)['passed'])
        self.assertFalse(lab.decision(lab.summarize(rows[:-1],fixture),fixture,True)['passed'])

    def test_scope_overwrite_missing_smoke_and_fixed_config(self):
        config=configuration()
        with self.assertRaises(ValueError):
            lab.output_scope(lab.ROOT/'interactive_lab_bad')
        candidate=lab.ROOT/'results/runs/interactive_lab_test_not_created'
        with patch.object(Path,'exists',return_value=True):
            with self.assertRaises(FileExistsError):
                lab.output_scope(candidate)
        with self.assertRaisesRegex(ValueError,'smoke-evidence'):
            lab.run(lab.ROOT/'experiments/interactive_lab_v0.json',candidate)
        changed=copy.deepcopy(config)
        changed['allowed_actions'].append(8)
        with self.assertRaises(ValueError):
            lab.validate_config(changed)


if __name__=='__main__':
    unittest.main()
