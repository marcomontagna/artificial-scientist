import json
import re
import unittest
from artificial_scientist.revision_replay import replay


class RevisionReplayTests(unittest.TestCase):
    def test_safe_roundtrip_of_actual_decision_records(self):
        hostile='</script><img src=x onerror=alert(1)> & \u2028'
        trace=dict(policy='active',variant=hostile,seed=7,events=[dict(step=1,phase='check',cycle_id=0,
            models=[dict(id='old',formula=hostile)],predictions=[dict(model_id='old',tape=[[1,2],[3,4]])],
            reason=hostile,outcomes=[dict(tick=1,x=1.,y=2.)],losses={'old':.4})],
            cycles=[dict(id=0,check_steps=[1,2,3,4],accepted=False,mean_squared_error={'old':.2})])
        html=replay(trace)
        payload=re.search(r'<script id="trace-data" type="application/json">(.*?)</script>',html,re.S).group(1)
        self.assertEqual(json.loads(payload),trace)
        self.assertNotIn('<',payload)
        self.assertNotIn(hostile,html)
        self.assertNotIn('innerHTML',html)
        self.assertNotIn('document.write',html)
        self.assertEqual(html.count('<script'),2)

    def test_chronology_empty_and_offline_contract(self):
        html=replay(dict(events=[]))
        self.assertIn('final decision not yet available',html)
        self.assertIn('e.step>=Math.max(...cycle.check_steps)',html)
        self.assertIn('No revision cycles recorded',html)
        self.assertIn('unobserved motion is not reconstructed',html)
        self.assertIn('Recorded choice reason',html)
        self.assertNotRegex(html,r'<(?:script|link)[^>]+(?:src|href)=')
        for trace in [dict(events={}),dict(events=[],seed=float('nan'))]:
            with self.assertRaises(ValueError):
                replay(trace)


if __name__=='__main__':
    unittest.main()
