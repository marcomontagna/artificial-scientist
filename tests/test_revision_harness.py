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
