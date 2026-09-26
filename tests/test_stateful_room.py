"""Stateful-room synthetic fixtures7/11 only; no smoke or study sampling."""
import copy
import hashlib
import json
import math
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from artificial_scientist import stateful_room as room


def configuration():
    return json.loads((room.ROOT/'experiments/stateful_room_v0.json').read_text())


def world(name,config):
    return next(w for w in config['worlds'] if w['id']==name)


class StatefulRoomTests(unittest.TestCase):
    def test_dirichlet_normalization_update_locality_and_no_hidden_inputs(self):
        learner=room.TabularLearner(.5)
        self.assertEqual(set(vars(learner)),{'prior','counts'})
        for s in range(4):
            for a in range(3):
                self.assertEqual(learner.predictive(s,a),[.2]*5)
        before=copy.deepcopy(learner.counts)
        learner.observe(2,1,4)
        self.assertEqual(learner.counts[7],[0,0,0,0,1])
        self.assertTrue(all(row==old for i,(row,old) in enumerate(zip(learner.counts,before)) if i!=7))
        self.assertAlmostEqual(sum(learner.predictive(2,1)),1.)
        self.assertAlmostEqual(learner.predictive(2,1)[4],3/7)
        with self.assertRaises(ValueError):
            learner.observe(0,0,5)

    def test_gain_analytical_prior_direct_mi_and_deterministic_category_invariance(self):
        expected=(math.log(5)-math.log(7)+(3/7)*math.log(3))/12
        self.assertAlmostEqual(room.row_gain([0]*5),expected,places=14)
        for counts in ([0]*5,[1,2,0,3,1],[20,0,0,0,0]):
            alpha=[n+.5 for n in counts]
            total=sum(alpha)
            direct=0.
            for i in range(5):
                for j in range(5):
                    joint=alpha[i]*(alpha[j]+(i==j))/(total*(total+1))
                    direct+=joint*math.log(joint/(alpha[i]/total*alpha[j]/total))
            self.assertAlmostEqual(room.row_gain(counts),direct/12,places=14)
            self.assertGreaterEqual(room.row_gain(counts),0.)
        for n in (0,1,8,96):
            gains=[room.row_gain([n if i==category else 0 for i in range(5)]) for category in range(5)]
            self.assertLess(max(gains)-min(gains),1e-14)

    def test_depth_two_matches_hypothetical_update_and_does_not_mutate(self):
        learner=room.TabularLearner(.5)
        for s,a,o in [(0,0,4),(0,0,4),(0,1,0),(1,0,2),(2,2,2),(3,1,0)]:
            learner.observe(s,a,o)
        before=copy.deepcopy(vars(learner))
        for s in range(4):
            actual=learner.scores(s,2)
            for a in range(3):
                future=0.
                for outcome,p in enumerate(learner.predictive(s,a)):
                    imagined=copy.deepcopy(learner)
                    imagined.observe(s,a,outcome)
                    future+=p*max(imagined.gain(room.next_state(s,outcome),b) for b in range(3))
                self.assertAlmostEqual(actual[a],learner.gain(s,a)+future,places=14)
        self.assertEqual(before,vars(learner))

    def test_joint_prediction_same_row_only_on_return(self):
        learner=room.TabularLearner(.5)
        matrix=learner.joint_predictive(0,2,2)
        self.assertAlmostEqual(sum(map(sum,matrix)),1.)
        for first in range(5):
            for second in range(5):
                expected=((3/35 if first==second else 1/35) if first in (0,4) else 1/25)
                self.assertAlmostEqual(matrix[first][second],expected)
        before=copy.deepcopy(learner.counts)
        learner.joint_predictive(0,0,1)
        self.assertEqual(before,learner.counts)

    def test_world_support_blocked_accepted_and_hidden_arm_propagation(self):
        config=configuration()
        for w in config['worlds']:
            for s in range(4):
                for a in range(3):
                    for arm in (0,1):
                        branches=room.transition_branches(w,s,a,arm)
                        self.assertAlmostEqual(sum(p for _,_,p in branches),1.)
                        for outcome,next_arm,p in branches:
                            self.assertTrue(0<=outcome<5 and next_arm in (0,1) and p>0)
        gate=world('gate_on',config)
        self.assertEqual(room.transition_branches(gate,0,1),[(4,0,1.)])
        self.assertEqual(room.transition_branches(gate,0,2),[(0,0,1.)])
        hidden=world('hidden_arm',config)
        joint=room.truth_joint(hidden,0,1,1,config)
        self.assertAlmostEqual(joint[1][4],.5)
        self.assertAlmostEqual(joint[4][4],.5)
        self.assertEqual(joint[1][0],0.)  # no rearming/reset between query steps
        power_then_door=room.truth_joint(hidden,0,0,1,config)
        self.assertEqual(power_then_door[2][3],1.)
        branches=room.transition_branches(world('random_room',config),0,0)
        self.assertEqual(room.draw_branch(branches,math.nextafter(1.,0.)),(3,0))

    def test_cycle_hand_computed_paths_and_coverage(self):
        config=configuration()
        paths={'gate_on':[0,2,3,3,1,1,1,3,2,2,0,0,0],
               'gate_off':[0,2,2,2,0,1,1,3,3,3,1,0,0],
               'directional':[0,2,3,3,1,0,0,2,3,3,1,0,0]}
        fixture=copy.deepcopy(config)
        fixture.update(steps=12,two_step_checkpoints=[0,12])
        for name,path in paths.items():
            episode=room.episode_record(world(name,fixture),7,'cycle',fixture)
            self.assertEqual([r['after_state'] for r in episode['records']],path)
            visited=sum(sum(row)>0 for row in episode['records'][-1]['counts'])
            self.assertEqual(visited,6 if name=='directional' else 12)
            self.assertEqual(episode['first_full_coverage_step'],None if name=='directional' else 12)
            self.assertEqual(episode['final_visit_imbalance'],2 if name=='directional' else 0)

    def test_replay_metric_timing_query_isolation_and_rng(self):
        config=configuration()
        fixture=copy.deepcopy(config)
        fixture.update(steps=6,two_step_checkpoints=[0,3,6])
        w=world('hidden_arm',fixture)
        episode=room.episode_record(w,11,'lookahead2',fixture)
        learner=room.TabularLearner(.5)
        reference=room.evaluator_reference(w,fixture)
        before=copy.deepcopy(vars(learner))
        room.evaluate(learner,reference,fixture,True)
        self.assertEqual(vars(learner),before)
        for record in episode['records'][1:]:
            self.assertEqual(record['pre_action_probabilities'],learner.predictive(record['before_state'],record['action']))
            learner.observe(record['before_state'],record['action'],record['outcome'])
            self.assertEqual(record['counts'],learner.counts)
            metrics,two=room.evaluate(learner,reference,fixture,record['step'] in fixture['two_step_checkpoints'])
            self.assertEqual(record['query_metrics'],metrics)
            self.assertEqual(record['two_step_metrics'],two)
            self.assertEqual(record['accepted'],record['outcome']!=4)
        rng=random.Random(7000003+11)
        self.assertEqual(room.observation_uniforms(11,fixture),
                         [[[rng.random() for _ in range(3)] for _ in range(4)] for _ in range(6)])
        short=copy.deepcopy(fixture)
        short.update(steps=3,two_step_checkpoints=[0,3])
        prefix=room.episode_record(w,11,'lookahead2',short)
        self.assertEqual(prefix['records'],episode['records'][:4])
        random_a=room.episode_record(world('gate_on',fixture),7,'random',fixture)
        random_b=room.episode_record(world('random_room',fixture),7,'random',fixture)
        self.assertEqual([r['action'] for r in random_a['records']],[r['action'] for r in random_b['records']])

    def test_ties_and_primary_mixed_incomplete_decision(self):
        config=configuration()
        learner=room.TabularLearner()
        action,scores,tie=room.select_action('greedy',learner,0,0,random.Random(7),1e-12)
        self.assertTrue(tie)
        self.assertIn(action,[0,1,2])
        fixture=copy.deepcopy(config)
        fixture['seeds']=[7,11]
        rows=[dict(seed=s,world=w['id'],policy=p,steps=96,record_count=97)
              for s in fixture['seeds'] for w in config['worlds'] for p in config['policies']]
        summary=dict(episodes=rows,paired_primary=[dict(comparator=c,mean_difference=-.02) for c in ('random','greedy','cycle')],
            paired_per_world=[dict(world=w,comparator=c,mean_difference=-.02)
                              for w in config['primary_worlds'] for c in ('random','greedy')])
        self.assertTrue(room.decision(summary,fixture,True)['passed'])
        summary['paired_per_world'][0]['mean_difference']=.02
        result=room.decision(summary,fixture,True)
        self.assertTrue(result['mixed'])
        self.assertFalse(result['passed'])
        self.assertFalse(room.decision(summary,fixture,False)['complete'])
        summary['episodes']=rows[:-1]
        self.assertFalse(room.decision(summary,fixture,True)['complete'])
        self.assertFalse(room.decision(summary,config,True)['passed'])
        summary['episodes']=rows[:-1]+[rows[0]]
        self.assertFalse(room.decision(summary,fixture,True)['complete'])

    def test_auc_normalization_and_seed_aggregation(self):
        fixture=configuration()
        fixture.update(steps=3,two_step_checkpoints=[0,3])
        episode=room.episode_record(world('gate_on',fixture),7,'cycle',fixture)
        row=room.episode_summary(episode)
        self.assertAlmostEqual(row['auc_excess_log_loss'],sum(r['query_metrics']['excess_log_loss'] for r in episode['records'][1:])/3)
        rows=[]
        for seed,delta in ((7,-.02),(11,-.04)):
            for w in fixture['worlds']:
                for p in fixture['policies']:
                    record=copy.deepcopy(row)
                    record.update(seed=seed,world=w['id'],policy=p,auc_excess_log_loss=.2+(delta if p=='lookahead2' else 0.))
                    rows.append(record)
        summary=room.summarize(rows,fixture)
        for paired in summary['paired_primary']:
            self.assertAlmostEqual(paired['mean_difference'],-.03)
            self.assertAlmostEqual(paired['seed_se'],.01)

    def test_output_scope_overwrite_missing_smoke_and_fixed_config(self):
        room.validate_config(configuration())
        with self.assertRaises(ValueError):
            room.output_scope(room.ROOT/'stateful_room_bad')
        candidate=room.ROOT/'results/runs/stateful_room_test_not_created'
        with patch.object(Path,'exists',return_value=True):
            with self.assertRaises(FileExistsError):
                room.output_scope(candidate)
        with self.assertRaisesRegex(ValueError,'smoke-evidence'):
            room.run(room.ROOT/'experiments/stateful_room_v0.json',candidate)
        changed=configuration()
        changed['primary_comparators']=['random','greedy','cycle']
        with self.assertRaises(ValueError):
            room.validate_config(changed)

    def test_smoke_source_artifact_time_and_disk_guards_without_sampling(self):
        config=configuration()
        with tempfile.TemporaryDirectory(prefix='stateful_room_fixture_',dir=room.ROOT/'results/runs') as folder:
            path=Path(folder)
            for name in ('config.json','worlds.json','trajectories.jsonl','summary.json','decision.json'):
                (path/name).write_text('synthetic verifier fixture, not an experiment\n')
            meta=dict(status='completed',mode='smoke',completed_episodes=20,sources_unchanged=True,
                      source_sha256={'fixture':'source'},config_sha256='fixture-config',elapsed_seconds=1.,
                      artifact_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in path.iterdir()})
            def save_meta():
                meta['artifact_bytes']=0
                for _ in range(20):
                    text=json.dumps(meta)+'\n'
                    size=sum(p.stat().st_size for p in path.iterdir() if p.name!='metadata.json')+len(text.encode())
                    if meta['artifact_bytes']==size:
                        break
                    meta['artifact_bytes']=size
                (path/'metadata.json').write_text(json.dumps(meta)+'\n')
            save_meta()
            room.verify_smoke(path,'fixture-config',{'fixture':'source'},config)
            with self.assertRaises(ValueError):
                room.verify_smoke(path,'different-config',{'fixture':'source'},config)
            altered=copy.deepcopy(config)
            altered['smoke_projection_limit_bytes']=1
            with self.assertRaises(RuntimeError):
                room.verify_smoke(path,'fixture-config',{'fixture':'source'},altered)
            meta['elapsed_seconds']=3.
            save_meta()
            with self.assertRaises(RuntimeError):
                room.verify_smoke(path,'fixture-config',{'fixture':'source'},config)
            (path/'worlds.json').write_text('changed')
            with self.assertRaises(ValueError):
                room.verify_smoke(path,'fixture-config',{'fixture':'source'},config)


if __name__=='__main__':
    unittest.main()
