import copy
import time
import unittest
from unittest.mock import patch
from artificial_scientist.lab_api import Action,Observation,Transition
from artificial_scientist import revision_reference as r
from artificial_scientist import revision_models as m


class SparseReferenceTests(unittest.TestCase):
    def history(self,n=12):
        before=Observation(0,0.,0.)
        history=[]
        for i in range(n):
            action=Action('push',angle=(i%4)*1.5707963267948966,magnitude=.3)
            x,y=m.old.impulse(action)
            after=Observation(i+1,before.x+.4*x,before.y+.7*y)
            history.append(Transition(before,action,after));before=after
        return history

    def test_future_outcomes_leave_forward_path_and_predictions_unchanged(self):
        history=self.history()
        changed=copy.deepcopy(history)
        split=int(.6*len(history))
        for i in range(split,len(changed)):
            t=changed[i]
            changed[i]=Transition(Observation(t.before.tick,999.,999.),t.action,Observation(t.after.tick,100.+i,-100.-i))
        first=r.sparse_history_reference(history)
        second=r.sparse_history_reference(changed)
        self.assertEqual(first.selection_audit['prefix_transitions'],7)
        for a,b in zip(first.selection_audit['stages'],second.selection_audit['stages']):
            self.assertEqual(a['model'],b['model'])
            self.assertEqual(a['training_mse'],b['training_mse'])
            self.assertEqual(a['validation_predictions'],b['validation_predictions'])
            self.assertNotEqual(a['validation_mse'],b['validation_mse'])
        self.assertEqual(len(first.selection_audit['stages']),9)
        self.assertEqual(first.fit_work['candidate_fits'],1+sum(39-i for i in range(8))+1)
        self.assertEqual(first.fit_work['validation_rollouts'],9)
        self.assertEqual(first.fit_work['validation_predicted_positions'],45)

    def test_zero_ties_caps_and_minimum(self):
        history=[Transition(Observation(i,0.,0.),Action('observe'),Observation(i+1,0.,0.)) for i in range(10)]
        result=r.sparse_history_reference(history)
        self.assertEqual(result.terms,())
        self.assertEqual(result.selection_audit['selected_size'],0)
        for stage in result.selection_audit['candidates_by_stage']:
            scores=stage['candidates']
            self.assertEqual(scores[0]['id'],min(row['id'] for row in scores))
        self.assertEqual(result.max_terms,8)
        self.assertEqual(result.max_nodes,40)
        with self.assertRaises(ValueError):
            r.sparse_history_reference(history[:9])
        with self.assertRaises(TimeoutError):
            r.sparse_history_reference(history,deadline=time.process_time()-1)
        with self.assertRaises(ValueError):
            r.SparseHistoryReference(m.VARIABLES,False,((0.,)*9,)*2)
        self.assertEqual(m.VectorModel.max_terms,4)

    def test_validation_reset_and_no_observed_restart(self):
        model=r.SparseHistoryReference(('one',),False,((1.,),(2.,)))
        prefix=self.history(6)
        boundary=Observation(6,10.,20.)
        suffix=[Transition(boundary,Action('observe'),Observation(7,999.,999.)),
                Transition(Observation(7,999.,999.),Action('reset'),Observation(15,999.,999.)),
                Transition(Observation(15,999.,999.),Action('wait',ticks=2),Observation(17,999.,999.))]
        work=dict(validation_rollouts=0,validation_predicted_positions=0,validation_feature_evaluations=0)
        loss,predictions=r._validation(model,boundary,prefix,suffix,float('inf'),work)
        self.assertEqual(predictions,[(11.,22.),(0.,0.),(2.,4.)])
        self.assertGreater(loss,1.)
        self.assertEqual(work['validation_feature_evaluations'],6)


if __name__=='__main__':
    unittest.main()
