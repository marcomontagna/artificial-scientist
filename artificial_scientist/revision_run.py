"""Evaluator-owned harness for the frozen assumption-revision protocol."""
import argparse
import hashlib
import json
import math
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from .lab_api import Action, Observation, Transition
from .lab_agent import Investigator, digest
from .lab_run import EVALUATION as ORIGINAL_EVALUATION, frozen_rollout
from .revision_agent import RevisionInvestigator
from .revision_models import VectorModel, linear_reference
from .revision_world import make_revision_world

EVALUATION = ORIGINAL_EVALUATION + ((Action('push',angle=.61,magnitude=.8),Action('wait',ticks=4),
    Action('push',angle=2.43,magnitude=.6),Action('wait',ticks=4),
    Action('push',angle=4.72,magnitude=.4),Action('wait',ticks=4),Action('observe')),)
MAX_BYTES=10*1024*1024
WORLD_COMMIT='dfabfe1'


def tape(model, initial, sequence):
    if isinstance(model,VectorModel):
        return model.predict_tape(initial,[],sequence)
    return [(p['x'],p['y']) for p in frozen_rollout(model,initial,sequence)]


def evaluation(model, history, cycles, variant, seed, deadline, include_history_reference=False):
    reference=linear_reference(history,deadline)
    models={'learned':model,'vector_linear':reference}
    memory_reference=None
    if include_history_reference:
        from .revision_models import history_reference
        memory_reference=history_reference(history,deadline)
        models['history_linear']=memory_reference
    for cycle in cycles:
        for snapshot in cycle.get('models',[]):
            models['cycle%d:%s'%(cycle['id'],snapshot['id'])]=VectorModel.from_snapshot(snapshot)
    records=[]
    for index,sequence in enumerate(EVALUATION):
        if time.process_time()>=deadline:raise TimeoutError('evaluation CPU cap')
        world=make_revision_world(seed+100000+index*1009,variant)
        initial=world.step(Action('reset'))
        predictions={name:tape(m,initial,sequence) for name,m in models.items()}
        frozen_hash=digest(predictions)
        actual=[world.step(a) for a in sequence]
        errors={name:[(p[0]-a.x)**2+(p[1]-a.y)**2 for p,a in zip(points,actual)] for name,points in predictions.items()}
        records.append(dict(sequence=index,initial=asdict(initial),actions=[asdict(a) for a in sequence],
            predictions=predictions,prediction_hash=frozen_hash,actual=[asdict(a) for a in actual],squared_errors=errors,cost=world.consumed))
    metrics={name:sum(v for r in records for v in r['squared_errors'][name])/sum(len(r['actual']) for r in records) for name in models}
    agreement=[]
    decision_diagnostics=[]
    for cycle in cycles:
        if not cycle.get('models'):continue
        inc=VectorModel.from_snapshot(cycle['models'][0]);alts=[VectorModel.from_snapshot(s) for s in cycle['models'][1:]]
        key=lambda ident:'cycle%d:%s'%(cycle['id'],ident)
        candidate=next(m for m in alts if m.id==cycle['best_alternative'])
        incumbent_error=metrics[key(inc.id)];candidate_error=metrics[key(candidate.id)]
        candidate_margin=max(.15*incumbent_error,.0001*max(1,candidate.parameter_count-inc.parameter_count))
        useful=incumbent_error-candidate_error>candidate_margin
        decision_diagnostics.append(dict(cycle_id=cycle['id'],check_rule=cycle.get('check_rule','original'),
            candidate_id=candidate.id,accepted=cycle['accepted'],external_incumbent_mse=incumbent_error,
            external_candidate_mse=candidate_error,external_required_margin=candidate_margin,
            harmful_accepted=cycle['accepted'] and candidate_error>incumbent_error,
            useful_accepted=cycle['accepted'] and useful,missed_useful=(not cycle['accepted']) and useful))
        best=min(alts,key=lambda m:(metrics[key(m.id)],m.id))
        margin=max(.15*metrics[key(inc.id)],.0001*max(1,best.parameter_count-inc.parameter_count))
        accepted=metrics[key(inc.id)]-metrics[key(best.id)]>margin
        selected=best.id if accepted else inc.id
        agreement.append(dict(cycle_id=cycle['id'],external_incumbent_mse=metrics[key(inc.id)],
            external_best_alternative=best.id,external_alternative_mse=metrics[key(best.id)],
            external_required_margin=margin,external_accepted=accepted,external_selected_id=selected,
            same_accept_reject=accepted==cycle['accepted'],same_selected_model=selected==cycle['selected_id'],
            meaning='Posthoc best-alternative single-batch margin on frozen snapshots; NOT the two-stage adoption rule. Different intervention distribution, not causal truth.'))
    return dict(metrics={k:metrics[k] for k in models if not k.startswith('cycle')},
        history_reference=memory_reference.snapshot() if memory_reference else None,
        history_reference_work=getattr(memory_reference,'fit_work',None),
        snapshot_metrics={k:v for k,v in metrics.items() if k.startswith('cycle')},records=records,
        tool_cost=sum(r['cost'] for r in records),reference=reference.snapshot(),agreement=agreement,decision_diagnostics=decision_diagnostics,
        warning='Separate outcomes never affect adoption; reused evaluator design and three noise seeds are descriptive.')


def source_info():
    files=list(Path('artificial_scientist').glob('lab_*.py'))+list(Path('artificial_scientist').glob('revision_*.py'))
    return dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        git_status=subprocess.check_output(['git','status','--porcelain'],text=True).strip(),
        source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)})


def investigate(variant,policy,seed,output,cpu_seconds=120,check_rule='original',proposal_mode='ordinary',include_history_reference=False):
    if not 0<cpu_seconds<=120:raise ValueError('invalid CPU cap')
    if policy not in ('active','random','coverage','no-revision','legacy'):raise ValueError('unknown policy')
    if check_rule not in ('original','pooled','confirm_short','confirm_long'):raise ValueError('unknown check rule')
    if proposal_mode not in ('ordinary','history'):raise ValueError('unknown proposal mode')
    if policy=='legacy' and (check_rule!='original' or proposal_mode!='ordinary'):raise ValueError('legacy has no revision modes')
    output=Path(output)
    if output.exists():raise FileExistsError('fresh output required')
    provenance=source_info()
    output.mkdir(parents=True)
    start=time.process_time();deadline=start+cpu_seconds
    world=make_revision_world(seed,variant)
    legacy=policy=='legacy'
    agent=Investigator(world.initial,'active',seed+700001) if legacy else RevisionInvestigator(world.initial,policy,seed+700001,check_rule=check_rule,proposal_mode=proposal_mode)
    trace=dict(schema_version=2,variant=variant,policy=policy,seed=seed,check_rule=check_rule,proposal_mode=proposal_mode,include_history_reference=include_history_reference,world_source_commit=WORLD_COMMIT,
        initial=asdict(world.initial),events=[],cycles=[],status='running',caps={'training':80,'evaluation':68,'cpu_seconds':cpu_seconds,'trace_bytes':MAX_BYTES},
        assumptions='Supplied initial v/u structure for revision policies; known zero home, weak noise floor, bounded predefined revision operators; no calibrated confidence.')
    journal_bytes=0
    with (output/'predictions_before_experiments.jsonl').open('x') as journal:
        while world.consumed<80:
            if time.process_time()>=deadline:
                trace['status']='incomplete_cpu_cap';break
            plan=agent.plan(80-world.consumed)
            if time.process_time()>=deadline:
                trace['status']='incomplete_cpu_cap';break
            line=json.dumps(dict(step=len(trace['events']),plan=plan,prediction_hash=digest(plan)),allow_nan=False)+'\n'
            if len(json.dumps(trace).encode())+journal_bytes+2*len(line.encode())+262144>MAX_BYTES:
                trace['status']='incomplete_trace_cap';break
            journal.write(line);journal.flush();journal_bytes+=len(line.encode())
            action_list=[Action(**plan['action'])] if legacy else [Action(**a) for a in plan['actions']]
            stamp=time.monotonic_ns()
            outcomes=[world.step(a) for a in action_list]
            event=dict(plan,prediction_hash=digest(plan),execution_started_ns=stamp,outcomes=[asdict(a) for a in outcomes],total_cost=world.consumed)
            try:
                if legacy:
                    errors,revision=agent.accept(action_list[0],outcomes[0],deadline)
                    event.update(errors=errors,revision=revision,models_after=[m.snapshot() for m in agent.models])
                    if revision.get('incomplete'):trace['status']='incomplete_cpu_cap'
                else:
                    event.update(agent.accept(outcomes,deadline))
                    if event.get('incomplete'):trace['status']='incomplete_cpu_cap'
            except TimeoutError as exc:
                event['incomplete']=str(exc);trace['status']='incomplete_cpu_cap'
            trace['events'].append(event)
            if time.process_time()>=deadline:trace['status']='incomplete_cpu_cap'
            if trace['status'].startswith('incomplete'):break
    if trace['status']=='running':trace['status']='budget_complete'
    model=agent.final_model() if legacy else agent.incumbent
    trace.update(selected_model=model.snapshot(),training_cost=world.consumed,
        cycles=[] if legacy else agent.cycles,explanation_status='not_instrumented_legacy' if legacy else agent.explanation_status(),
        work=agent.search_cost if legacy else agent.work,
        incomplete_cycle=None if legacy or not agent.cycle else dict(id=agent.cycle['id'],
            models=agent.cycle['snapshots'],trigger=agent.cycle['trigger'],check_steps=agent.cycle['check_steps'],
            losses=agent.cycle['losses'],proposal_audit=agent.cycle['audit'],check_rule=check_rule,
            position_losses=agent.cycle.get('position_losses'),screening=agent.cycle.get('screening'),
            confirmation_plan=agent.cycle.get('confirmation_plan')))
    if not trace['status'].startswith('incomplete'):
        try:trace['evaluation']=evaluation(model,agent.history,trace['cycles'],variant,seed,deadline,include_history_reference=include_history_reference)
        except TimeoutError:trace['status']='incomplete_evaluation_cpu_cap'
    trace['cpu_seconds']=time.process_time()-start
    if time.process_time()>=deadline and not trace['status'].startswith('incomplete'):trace['status']='incomplete_cpu_cap'
    encoded=json.dumps(trace,allow_nan=False).encode()
    if len(encoded)+journal_bytes>MAX_BYTES:raise RuntimeError('raw artifact cap exceeded')
    (output/'trace.json').write_bytes(encoded)
    summary=dict(provenance,variant=variant,policy=policy,seed=seed,check_rule=check_rule,proposal_mode=proposal_mode,include_history_reference=include_history_reference,status=trace['status'],
        training_cost=world.consumed,tool_actions=len(agent.history),experiments=len(trace['events']),
        evaluation_cost=trace.get('evaluation',{}).get('tool_cost'),metrics=trace.get('evaluation',{}).get('metrics'),
        formula=model.formula,selected_model=model.snapshot(),cycles=len(trace['cycles']),
        adoptions=sum(c.get('accepted',False) for c in trace['cycles']),explanation_status=trace['explanation_status'],
        work=trace['work'],cpu_seconds=trace['cpu_seconds'])
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    if not legacy:
        from .revision_replay import replay
        (output/'replay.html').write_text(replay(trace))
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--variant',choices=('control','challenge','stress'),required=True)
    p.add_argument('--policy',choices=('active','random','coverage','no-revision','legacy'),default='active')
    p.add_argument('--seed',type=int,default=270001);p.add_argument('--output',required=True)
    p.add_argument('--check-rule',choices=('original','pooled','confirm_short','confirm_long'),default='original')
    p.add_argument('--proposal-mode',choices=('ordinary','history'),default='ordinary')
    p.add_argument('--history-reference',action='store_true')
    args=p.parse_args();r=investigate(args.variant,args.policy,args.seed,args.output,check_rule=args.check_rule,proposal_mode=args.proposal_mode,include_history_reference=args.history_reference)
    print(json.dumps(r,indent=2))
    if r['status']!='budget_complete':raise SystemExit(2)


if __name__=='__main__':main()
