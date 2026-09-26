import ast
import unittest
import tempfile
import json
from pathlib import Path
from artificial_scientist.lab_api import Action,Observation,Transition
from artificial_scientist import revision_run
from artificial_scientist.revision_models import VectorModel
from unittest.mock import patch


class FakeWorld:
    def __init__(self):self.consumed=0;self.x=0.0;self.initial=Observation(0,0,0)
    def step(self,a):
        self.consumed+=a.cost
        if a.kind=='reset':self.x=0
        else:self.x+=.1*a.cost
        return Observation(self.consumed,self.x,0)


class HarnessTests(unittest.TestCase):
    def test_same_evaluator_and_no_fit_to_evaluation(self):
        model=VectorModel(('v','u'),True,(.5,.3))
        old=model.snapshot();history=[];worlds=[]
        def make(seed,variant):
            w=FakeWorld();worlds.append(w);return w
        with patch.object(revision_run,'make_revision_world',side_effect=make),patch.object(revision_run,'linear_reference',return_value=model) as fitter:
            result=revision_run.evaluation(model,history,[],'not_passed_to_model',7,float('inf'))
        fitter.assert_called_once_with(history,float('inf'))
        self.assertEqual(history,[]);self.assertEqual(old,model.snapshot())
        self.assertEqual(result['tool_cost'],68)
        self.assertEqual(sum(a.cost for a in revision_run.EVALUATION[-1]),16)
        for r in result['records']:
            self.assertEqual(r['prediction_hash'],revision_run.digest(r['predictions']))
            for name,pred in r['predictions'].items():
                self.assertEqual(r['squared_errors'][name],[(p[0]-a['x'])**2+(p[1]-a['y'])**2 for p,a in zip(pred,r['actual'])])

    def test_learner_import_boundary(self):
        for name in ('revision_agent.py','revision_models.py'):
            source=Path('artificial_scientist',name).read_text()
            tree=ast.parse(source)
            modules=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
            self.assertFalse(any('world' in n or 'run' in n for n in modules))
            self.assertNotIn('make_revision_world',source)

    def test_expired_evaluation_stops_before_world(self):
        with patch.object(revision_run,'make_revision_world') as factory:
            with self.assertRaises(TimeoutError):revision_run.evaluation(VectorModel((),True,()),[],[],'control',7,0)
            factory.assert_not_called()

    def test_synthetic_harness_journal_and_resource_stops(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'complete';created=[]
            class JournalWorld(FakeWorld):
                def step(self,action):
                    # The first world is the learner fixture, others are evaluation.
                    if created and self is created[0]:
                        lines=(out/'predictions_before_experiments.jsonl').read_text().splitlines()
                        self_test.assertEqual(len(lines),self.consumed//2+1 if self.consumed%2==0 else (self.consumed+1)//2)
                    return super().step(action)
            self_test=self
            def factory(seed,variant):
                w=JournalWorld();created.append(w);return w
            with patch.object(revision_run,'make_revision_world',side_effect=factory),patch.object(revision_run,'source_info',return_value={'synthetic_fixture':True}):
                result=revision_run.investigate('fixture','no-revision',7,out)
            self.assertEqual(result['status'],'budget_complete')
            self.assertEqual(result['training_cost'],80);self.assertEqual(result['evaluation_cost'],68)
            trace=json.loads((out/'trace.json').read_text())
            journal=[json.loads(line) for line in (out/'predictions_before_experiments.jsonl').read_text().splitlines()]
            for e,j in zip(trace['events'],journal):
                self.assertEqual(e['prediction_hash'],revision_run.digest(j['plan']))
                self.assertTrue(all(e[k]==v for k,v in j['plan'].items()))
            with patch.object(revision_run,'make_revision_world',return_value=FakeWorld()),patch.object(revision_run,'source_info',return_value={}),patch.object(revision_run,'MAX_BYTES',5000):
                result=revision_run.investigate('fixture','active',7,Path(directory)/'bytes')
            self.assertEqual(result['status'],'incomplete_trace_cap');self.assertEqual(result['training_cost'],0)
            with patch.object(revision_run,'make_revision_world',return_value=FakeWorld()),patch.object(revision_run,'source_info',return_value={}):
                result=revision_run.investigate('fixture','active',7,Path(directory)/'time',cpu_seconds=1e-12)
            self.assertEqual(result['status'],'incomplete_cpu_cap');self.assertEqual(result['training_cost'],0)

    def test_external_diagnostics_use_actual_decision_candidate(self):
        incumbent=VectorModel(('v',),True,(0.,))
        worse=VectorModel(('one',),True,(1.,))
        best=VectorModel(('u',),True,(0.,))
        cycle=dict(id=0,models=[m.snapshot() for m in (incumbent,worse,best)],
                   best_alternative=worse.id,accepted=False,selected_id=incumbent.id,check_rule='confirm_long')
        with patch.object(revision_run,'make_revision_world',side_effect=lambda *a:FakeWorld()),patch.object(revision_run,'linear_reference',return_value=incumbent):
            result=revision_run.evaluation(incumbent,[],[cycle],'fixture',7,float('inf'))
        d=result['decision_diagnostics'][0]
        self.assertEqual(d['candidate_id'],worse.id)
        self.assertGreater(d['external_candidate_mse'],d['external_incumbent_mse'])
        self.assertFalse(d['harmful_accepted']);self.assertFalse(d['useful_accepted']);self.assertFalse(d['missed_useful'])
        self.assertIn('NOT the two-stage',result['agreement'][0]['meaning'])
        cycle['accepted']=True;cycle['selected_id']=worse.id
        with patch.object(revision_run,'make_revision_world',side_effect=lambda *a:FakeWorld()),patch.object(revision_run,'linear_reference',return_value=incumbent):
            result=revision_run.evaluation(worse,[],[cycle],'fixture',7,float('inf'))
        self.assertTrue(result['decision_diagnostics'][0]['harmful_accepted'])

    def test_invalid_rule_rejected_before_output_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'unused'
            with self.assertRaises(ValueError):revision_run.investigate('fixture','active',7,output,check_rule='invalid')
            with self.assertRaises(ValueError):revision_run.investigate('fixture','legacy',7,output,check_rule='confirm_long')
            self.assertFalse(output.exists())

    def test_each_external_tape_rebuilds_from_own_empty_history(self):
        calls=[]
        class Spy(VectorModel):
            def predict_tape(self,observation,history,actions):
                calls.append((observation.tick,list(history),tuple(actions)))
                self_test.assertEqual(history,[])
                return super().predict_tape(observation,history,actions)
        self_test=self
        model=Spy(('v',),True,(0.,))
        training=[Transition(Observation(0,0,0),Action('push',magnitude=1),Observation(1,1,0))]
        with patch.object(revision_run,'make_revision_world',side_effect=lambda *a:FakeWorld()),patch.object(revision_run,'linear_reference',return_value=model),patch('artificial_scientist.revision_models.history_reference',return_value=model) as fitter,patch('artificial_scientist.revision_reference.sparse_history_reference',return_value=model) as sparse:
            result=revision_run.evaluation(model,training,[],'fixture',7,float('inf'),include_history_reference=True,include_sparse_reference=True)
        sparse.assert_called_once_with(training,float('inf'))
        fitter.assert_called_once_with(training,float('inf'))
        self.assertEqual(len(calls),16)
        self.assertTrue(all(tick==8 and not history for tick,history,actions in calls))
        self.assertIn('history_linear',result['metrics'])
        self.assertEqual(len(training),1)
