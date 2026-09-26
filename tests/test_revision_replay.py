import json
import re
import unittest
from artificial_scientist.revision_replay import replay, event_view


class RevisionReplayTests(unittest.TestCase):
    def test_safe_roundtrip_of_actual_decision_records(self):
        hostile='</script><img src=x onerror=alert(1)> & \u2028'
        trace=dict(policy='active',variant=hostile,seed=7,events=[dict(step=1,phase='check',cycle_id=0,
            models=[dict(id='old',formula=hostile)],predictions=[dict(model_id='old',tape=[[1,2],[3,4]])],
            reason=hostile,outcomes=[dict(tick=1,x=1.,y=2.)],losses={'old':.4})],
            cycles=[dict(id=0,check_steps=[1,2,3,4],accepted=False,mean_squared_error={'old':.2})])
        html=replay(trace)
        payload=re.search(r'<script id="trace-data" type="application/json">(.*?)</script>',html,re.S).group(1)
        decoded=json.loads(payload)
        decoded.pop('replay_views')
        self.assertEqual(decoded,trace)
        self.assertNotIn('<',payload)
        self.assertNotIn(hostile,html)
        self.assertNotIn('innerHTML',html)
        self.assertNotIn('document.write',html)
        self.assertEqual(html.count('<script'),2)

    def test_confirmation_origin_and_prefix_chronology(self):
        plan=dict(start=dict(tick=8,x=2.,y=3.),predictions=[dict(model_id='m',tape=[[i,i+1] for i in range(8)])])
        screen=dict(winner_id='m',passed=True,mean_squared_error={'m':.1})
        events=[dict(step=3,cycle_id=0,before={'tick':6,'x':1.,'y':1.},revision=None),
                dict(step=4,cycle_id=0,revision=dict(screening_complete=True,screening=screen,confirmation_plan=plan)),
                dict(step=5,cycle_id=0,prediction_origin='confirmation_start_frozen_tape',confirmation_plan=plan,
                     confirmation_offset=0,before=dict(tick=8,x=2.,y=3.),predictions=plan['predictions']),
                dict(step=6,cycle_id=0,prediction_origin='confirmation_start_frozen_tape',confirmation_plan=plan,
                     confirmation_offset=2,before=dict(tick=10,x=999.,y=999.),predictions=[dict(model_id='m',tape=[[2,3],[3,4]])]),
                dict(step=8,cycle_id=0)]
        cycle=dict(id=0,check_steps=list(range(1,9)),accepted=True,screening=screen,confirmation_mean_squared_error={'m':.2})
        trace=dict(events=events,cycles=[cycle])
        self.assertIsNone(event_view(trace,0)['screening'])
        self.assertIsNone(event_view(trace,0)['completed'])
        self.assertEqual(event_view(trace,1)['screening'],screen)
        view=event_view(trace,3)
        self.assertEqual(view['prediction_origin'],plan['start'])
        self.assertEqual(len(view['plot_predictions'][0]['tape']),8)
        self.assertIsNone(view['completed'])
        self.assertEqual(event_view(trace,4)['completed'],cycle)
        short=dict(events=[dict(step=1,before=dict(tick=1,x=4.,y=5.),predictions=[],check_rule='confirm_short')])
        self.assertEqual(event_view(short,0)['prediction_origin'],short['events'][0]['before'])
        self.assertFalse(event_view(short,0)['continuous_confirmation'])

    def test_chronology_empty_and_offline_contract(self):
        html=replay(dict(events=[]))
        self.assertIn('final decision not yet available',html)
        self.assertIn('No revision cycles recorded',html)
        self.assertIn('unobserved motion is not reconstructed',html)
        self.assertIn('Recorded choice reason',html)
        self.assertNotRegex(html,r'<(?:script|link)[^>]+(?:src|href)=')
        for trace in [dict(events={}),dict(events=[],seed=float('nan'))]:
            with self.assertRaises(ValueError):
                replay(trace)


if __name__=='__main__':
    unittest.main()
