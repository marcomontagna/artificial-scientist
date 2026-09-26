"""Evaluator-only greedy history regression; no world or evaluator data inputs."""
import math
import time
from . import revision_models as models


class SparseHistoryReference(models.VectorModel):
    max_terms=8
    max_nodes=40


def _training_mse(model,pairs,deadline,work):
    errors=[]
    for pair in pairs:
        models.deadline_check(deadline)
        error=0.
        for axis,(inputs,target) in enumerate(pair):
            predicted=math.fsum(c*models.value(term,inputs) for c,term in zip(model.coefficients[axis],model.terms))
            work['training_score_feature_evaluations']+=len(model.terms)
            error+=(predicted-target)**2
        errors.append(error)
    return math.fsum(errors)/max(1,len(errors))


def _validation(model,boundary,prefix,suffix,deadline,work):
    models.deadline_check(deadline)
    # Single call: only prefix observations initialize state, never suffix readings.
    predictions=model.predict_tape(boundary,prefix,[t.action for t in suffix])
    models.deadline_check(deadline)
    work['validation_rollouts']+=1
    work['validation_predicted_positions']+=len(predictions)
    ticks=sum(t.action.ticks if t.action.kind=='wait' else 0 if t.action.kind=='reset' else 1 for t in suffix)
    work['validation_feature_evaluations']+=2*len(model.terms)*ticks
    mse=math.fsum((x-t.after.x)**2+(y-t.after.y)**2 for (x,y),t in zip(predictions,suffix))/len(suffix)
    if not math.isfinite(mse):
        raise ArithmeticError('nonfinite reference validation loss')
    return mse,predictions


def sparse_history_reference(history,deadline=float('inf')):
    """Choose a forward-path size by internal continuous suffix validation."""
    models.deadline_check(deadline)
    if len(history)<10:
        raise ValueError('sparse history reference requires at least10 transitions')
    start=time.process_time()
    split=math.floor(.6*len(history))
    prefix,suffix=history[:split],history[split:]
    boundary=prefix[-1].after
    pairs=models.training_rows(prefix)
    pool=models.VARIABLES+models.lag_menu()
    work=dict(candidate_fits=0,feature_evaluations=0,training_score_feature_evaluations=0,
              validation_rollouts=0,validation_predicted_positions=0,validation_feature_evaluations=0)
    current=models._fit((),False,pairs,deadline,work,SparseHistoryReference)
    stages=[]
    candidates_by_stage=[]
    for size in range(9):
        models.deadline_check(deadline)
        if size:
            scored=[]
            for term in pool:
                if term in current.terms:
                    continue
                candidate=models._fit(current.terms+(term,),False,pairs,deadline,work,SparseHistoryReference)
                train=_training_mse(candidate,pairs,deadline,work)
                scored.append((train,candidate.id,candidate))
            scored.sort(key=lambda row:(row[0],row[1]))
            current=scored[0][2]
            train=scored[0][0]
            candidates_by_stage.append(dict(size=size,candidates=[dict(id=ident,training_mse=score) for score,ident,_ in scored]))
        else:
            train=_training_mse(current,pairs,deadline,work)
        validation,predictions=_validation(current,boundary,prefix,suffix,deadline,work)
        stages.append(dict(size=size,model=current.snapshot(),training_mse=train,validation_mse=validation,
                           validation_predictions=predictions))
    selected=min(stages,key=lambda stage:(stage['validation_mse'],stage['model']['parameter_count'],stage['model']['id']))
    terms=tuple(models.restore(t) for t in selected['model']['terms'])
    result=models._fit(terms,False,models.training_rows(history),deadline,work,SparseHistoryReference)
    work['cpu_seconds']=time.process_time()-start
    result.fit_work=dict(work)
    result.selection_audit=dict(transitions=len(history),prefix_transitions=split,suffix_transitions=len(suffix),
        prefix_training_pairs=len(pairs),boundary=dict(tick=boundary.tick,x=boundary.x,y=boundary.y),
        pool_size=len(pool),stages=stages,candidates_by_stage=candidates_by_stage,selected_size=selected['size'],
        selected_id=selected['model']['id'],selection='internal training suffix; not external evaluation',
        validation='continuous rollout initialized from prefix only',work=dict(work))
    return result
