import json
import re
import tempfile
import unittest
from pathlib import Path
from artificial_scientist.lab_replay import export_replay


class ReplayTests(unittest.TestCase):
    def render(self,trace):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            path=Path(directory)/'replay.html'
            export_replay(trace,path)
            return path.read_text(encoding='utf-8')

    def test_untrusted_strings_cannot_end_json_script_and_roundtrip(self):
        hostile='</script><script>alert("owned")</script><img src=x onerror=alert(1)> & \u2028'
        trace=dict(schema_version=1,policy=hostile,seed=7,status='complete',events=[dict(step=1,
            predictions=[dict(model_id=hostile,formula=hostile,x=.2,y=-.4)],
            choice=dict(reason=hostile),models_after=[dict(id='a',formula=hostile)])],final_models=[])
        html=self.render(trace)
        self.assertNotIn(hostile,html)
        payload=re.search(r'<script id="trace-data" type="application/json">(.*?)</script>',html,re.S).group(1)
        self.assertEqual(json.loads(payload),trace)
        self.assertNotIn('<',payload)
        self.assertNotIn('innerHTML',html)
        self.assertNotIn('document.write',html)
        self.assertEqual(html.count('<script'),2)

    def test_empty_optional_fields_and_offline_shell(self):
        trace=dict(schema_version=1,events=[])
        html=self.render(trace)
        self.assertIn('No recorded actions',html)
        self.assertIn('Saved replay',html)
        self.assertIn('not calibrated',html)
        self.assertIn('supplied grammar',html)
        self.assertNotRegex(html,r'<(?:script|link)[^>]+(?:src|href)=')
        self.assertIn('trace.final_models||[]',html)

    def test_guided_proposals_preserved_and_linked_to_next_action(self):
        evidence=dict(step=2,axis='x',inputs={'v':.2},residual=.3,prediction=.1,observed=.4,coefficient_version=3)
        search=dict(mode='guided',candidate_fits=2,feature_evaluations=5,
            diagnosis=dict(base_model_id='base',evidence=[evidence],associations=[dict(feature='abs(v)',axis='x',count=1,score=.8)],
                           selected_features=['abs(v)'],reason='recorded residual association'),
            candidates=[dict(model_id='new',origin='guided',feature='abs(v)',training_score=.2,selected=True)])
        link=dict(model_id='new',proposed_after_step=3,base_model_id='base',feature='abs(v)',origin='guided',
                  selected_action_separation_squared=.4,base_present=True)
        trace=dict(schema_version=1,events=[dict(step=3,revision={'search':search}),dict(step=4,choice={'hypothesis_links':[link]})])
        html=self.render(trace)
        payload=re.search(r'<script id="trace-data" type="application/json">(.*?)</script>',html,re.S).group(1)
        self.assertEqual(json.loads(payload),trace)
        self.assertIn('heuristics, not causal evidence',html)
        self.assertIn('events[index+1]',html)
        self.assertIn('link.proposed_after_step===event.step',html)
        self.assertIn('No next action is recorded',html)
        self.assertIn('Base absent; separation unavailable',html)
        self.assertIn('it does not invent a rationale',html)

    def test_contract_and_nonfinite_data_rejected_before_write(self):
        for trace in [dict(schema_version=2,events=[]),dict(schema_version=1,events={}),
                      dict(schema_version=1,events=[],evaluation={'mse':float('nan')})]:
            with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
                path=Path(directory)/'replay.html'
                with self.assertRaises(ValueError):
                    export_replay(trace,path)
                self.assertFalse(path.exists())


if __name__=='__main__':
    unittest.main()
