"""Tabular learning and exact shallow coverage planning in five designed rooms."""
import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import time
from pathlib import Path

from .run import git_info

ROOT=Path(__file__).resolve().parents[1]
POLICIES=('random','cycle','greedy','lookahead2')


def next_state(state,outcome):
    return state if outcome==4 else outcome


def entropy(probabilities):
    return -math.fsum(p*math.log(p) for p in probabilities if p)


def row_gain(counts,prior=.5,tolerance=1e-10):
    """Predictive mutual information for one of twelve equally weighted rows."""
    c=[n+prior for n in counts]
    total=math.fsum(c)
    clogs=[x*math.log(x) for x in c]
    sum_clogs=math.fsum(clogs)
    before=math.log(total)-sum_clogs/total
    increment=math.fsum(x/total*((x+1)*math.log(x+1)-old) for x,old in zip(c,clogs))
    after=math.log(total+1)-(sum_clogs+increment)/(total+1)
    value=(before-after)/12
    if value < -tolerance:
        raise ArithmeticError('substantially negative predictive-information score')
    return max(0.,value)


class TabularLearner:
    """Only visible state/action/outcome and the fixed scalar prior are inputs."""
    def __init__(self,prior=.5):
        if not math.isfinite(prior) or prior<=0:
            raise ValueError('positive prior required')
        self.prior=prior
        self.counts=[[0]*5 for _ in range(12)]

    def predictive(self,state,action):
        validate_visible(state,action)
        row=self.counts[3*state+action]
        total=sum(row)+5*self.prior
        return [(n+self.prior)/total for n in row]

    def observe(self,state,action,outcome):
        validate_visible(state,action)
        if type(outcome) is not int or not 0<=outcome<5:
            raise ValueError('outcome must be0..4')
        self.counts[3*state+action][outcome]+=1

    def gain(self,state,action):
        validate_visible(state,action)
        return row_gain(self.counts[3*state+action],self.prior)

    def scores(self,state,depth=1):
        validate_visible(state,0)
        if depth==1:
            return [self.gain(state,a) for a in range(3)]
        if depth!=2:
            raise ValueError('depth must be1or2')
        gains=[row_gain(row,self.prior) for row in self.counts]
        best=[max(gains[3*s:3*s+3]) for s in range(4)]
        totals=[]
        for action in range(3):
            row=3*state+action
            expected=0.
            for outcome,p in enumerate(self.predictive(state,action)):
                following=next_state(state,outcome)
                if following==state:
                    updated=list(self.counts[row])
                    updated[outcome]+=1
                    future=max(row_gain(updated,self.prior),
                               max(gains[3*state+b] for b in range(3) if b!=action))
                else:
                    future=best[following]
                expected+=p*future
            totals.append(gains[row]+expected)
        return totals

    def joint_predictive(self,state,first,second):
        validate_visible(state,first)
        validate_visible(state,second)
        initial=self.predictive(state,first)
        result=[]
        for outcome,p in enumerate(initial):
            following=next_state(state,outcome)
            row=list(self.counts[3*following+second])
            if following==state and second==first:
                row[outcome]+=1
            total=sum(row)+5*self.prior
            result.append([p*(n+self.prior)/total for n in row])
        return result


def validate_visible(state,action):
    if type(state) is not int or not 0<=state<4 or type(action) is not int or not 0<=action<3:
        raise ValueError('visible state0..3/action0..2 required')


def transition_branches(world,state,action,arm=0):
    """Evaluator/world transition: each branch is (observed outcome,next arm,p)."""
    validate_visible(state,action)
    if arm not in (0,1):
        raise ValueError('binary hidden arm required')
    kind=world['kind']
    if kind=='uniform_accepted':
        return [(outcome,0,.25) for outcome in range(4)]
    if kind=='hidden_arm':
        if action==0:
            return [(state^2,1,1.)]
        if action==1:
            return [(state^1 if arm else 4,0,1.)]
        return [(state,0,1.)]
    if kind!='visible_gate':
        raise ValueError('unknown world kind')
    if action==0:
        return [(state^2,0,1.)]
    if action==2:
        return [(state,0,1.)]
    power,door=state//2,state%2
    gates={'power_on':power==1,'power_off':power==0,'power_differs_door':power!=door}
    return [(state^1 if gates[world['gate']] else 4,0,1.)]


def initial_query_arms(world,config):
    p=config['hidden_query_arm_probability']
    return [(0,1-p),(1,p)] if world['kind']=='hidden_arm' else [(0,1.)]


def truth_joint(world,state,first,second,config):
    result=[[0.]*5 for _ in range(5)]
    for arm,weight in initial_query_arms(world,config):
        for o1,following_arm,p1 in transition_branches(world,state,first,arm):
            following=next_state(state,o1)
            for o2,_,p2 in transition_branches(world,following,second,following_arm):
                result[o1][o2]+=weight*p1*p2
    return result


def evaluator_reference(world,config):
    rows=[]
    joint=[]
    for state in range(4):
        for action in range(3):
            row=[0.]*5
            for arm,weight in initial_query_arms(world,config):
                for outcome,_,p in transition_branches(world,state,action,arm):
                    row[outcome]+=weight*p
            rows.append(row)
            for second in range(3):
                joint.append((state,action,second,truth_joint(world,state,action,second,config)))
    return dict(rows=rows,joints=joint,
        entropy=math.fsum(entropy(r) for r in rows)*config['query_row_weight'],
        joint_entropy=math.fsum(entropy([p for r in table for p in r]) for _,_,_,table in joint)*config['query_pair_weight'])


def evaluate(learner,reference,config,checkpoint=False):
    predictions=[learner.predictive(s,a) for s in range(4) for a in range(3)]
    weight=config['query_row_weight']
    loss=-math.fsum(t*math.log(p) for true,pred in zip(reference['rows'],predictions)
                    for t,p in zip(true,pred) if t)*weight
    metrics=dict(expected_log_loss=loss,excess_log_loss=loss-reference['entropy'],
        squared_probability_error=math.fsum((p-t)**2 for true,pred in zip(reference['rows'],predictions) for t,p in zip(true,pred))*weight,
        blocked_squared_error=math.fsum((p[4]-t[4])**2 for t,p in zip(reference['rows'],predictions))*weight,
        visited_row_coverage=sum(sum(row)>0 for row in learner.counts)/12)
    two=None
    if checkpoint:
        terms=[]
        for state,first,second,true in reference['joints']:
            predicted=learner.joint_predictive(state,first,second)
            terms.extend(-t*math.log(p) for tr,pr in zip(true,predicted) for t,p in zip(tr,pr) if t)
        value=math.fsum(terms)*config['query_pair_weight']
        two=dict(expected_log_loss=value,excess_log_loss=value-reference['joint_entropy'])
    return metrics,two


def observation_uniforms(seed,config):
    rng=random.Random(config['observation_seed_offset']+seed)
    return [[[rng.random() for _ in range(3)] for _ in range(4)] for _ in range(config['steps'])]


def draw_branch(branches,uniform):
    if not 0<=uniform<1:
        raise ValueError('uniform must be[0,1)')
    total=0.
    last=None
    for outcome,arm,p in branches:
        if p>0:
            last=(outcome,arm)
            total+=p
            if uniform<total:
                return last
    if last is None or abs(total-1)>1e-12:
        raise ValueError('invalid transition distribution')
    return last


def select_action(policy,learner,state,step,rng,tolerance):
    scores=None
    tie=False
    if policy in ('greedy','lookahead2'):
        scores=learner.scores(state,1 if policy=='greedy' else 2)
        maximum=max(scores)
        choices=[a for a in range(3) if maximum-scores[a]<=tolerance]
        tie=len(choices)>1
        action=rng.choice(choices)
    elif policy=='random':
        action=rng.randrange(3)
    elif policy=='cycle':
        action=step%3
    else:
        raise ValueError('unknown policy')
    return action,scores,tie


def episode_record(world,seed,policy,config,deadline=math.inf,reference=None):
    if policy not in config['policies']:
        raise ValueError('undeclared policy')
    learner=TabularLearner(config['dirichlet_prior'])
    reference=evaluator_reference(world,config) if reference is None else reference
    uniforms=observation_uniforms(seed,config)
    rng=random.Random(config['policy_seed_offset']+config['policy_seed_multiplier']*seed+config['policies'].index(policy))
    state,arm=config['start_state'],config['start_arm']
    timing=dict(selection_seconds=0.,prediction_seconds=0.,update_seconds=0.)
    metrics,two=evaluate(learner,reference,config,True)
    initial=dict(step=0,before_state=state,after_state=state,action=None,outcome=None,accepted=None,
        pre_action_probabilities=None,policy_scores=None,tie=None,counts=[r[:] for r in learner.counts],
        query_metrics=metrics,two_step_metrics=two)
    if world['kind']=='hidden_arm':
        initial['evaluator_only']=dict(arm_before=arm,arm_after=arm)
    records=[initial]
    first_full=None
    for step in range(config['steps']):
        if time.perf_counter()>deadline:
            raise TimeoutError('internal experiment deadline reached')
        start=time.perf_counter()
        action,scores,tie=select_action(policy,learner,state,step,rng,config['tie_tolerance'])
        timing['selection_seconds']+=time.perf_counter()-start
        start=time.perf_counter()
        prediction=learner.predictive(state,action)
        timing['prediction_seconds']+=time.perf_counter()-start
        outcome,following_arm=draw_branch(transition_branches(world,state,action,arm),uniforms[step][state][action])
        following=next_state(state,outcome)
        start=time.perf_counter()
        learner.observe(state,action,outcome)
        timing['update_seconds']+=time.perf_counter()-start
        metrics,two=evaluate(learner,reference,config,step+1 in config['two_step_checkpoints'])
        if first_full is None and metrics['visited_row_coverage']==1:
            first_full=step+1
        record=dict(step=step+1,before_state=state,after_state=following,action=action,outcome=outcome,
            accepted=outcome!=config['blocked_outcome'],pre_action_probabilities=prediction,policy_scores=scores,
            tie=tie,counts=[r[:] for r in learner.counts],query_metrics=metrics,two_step_metrics=two)
        if world['kind']=='hidden_arm':
            record['evaluator_only']=dict(arm_before=arm,arm_after=following_arm)
        records.append(record)
        state,arm=following,following_arm
    visits=[sum(row) for row in learner.counts]
    return dict(schema_version=1,world=world['id'],seed=seed,policy=policy,steps=config['steps'],records=records,
        timing=timing,first_full_coverage_step=first_full,final_visit_imbalance=max(visits)-min(visits))


def episode_summary(episode):
    records=episode['records'][1:]
    return dict(world=episode['world'],seed=episode['seed'],policy=episode['policy'],steps=episode['steps'],
        record_count=len(episode['records']),auc_excess_log_loss=statistics.mean(r['query_metrics']['excess_log_loss'] for r in records),
        final_excess_log_loss=records[-1]['query_metrics']['excess_log_loss'],
        final_squared_probability_error=records[-1]['query_metrics']['squared_probability_error'],
        final_blocked_squared_error=records[-1]['query_metrics']['blocked_squared_error'],
        final_coverage=records[-1]['query_metrics']['visited_row_coverage'],
        two_step={str(r['step']):r['two_step_metrics'] for r in episode['records'] if r['two_step_metrics'] is not None},
        tie_count=sum(r['tie'] for r in records),first_full_coverage_step=episode['first_full_coverage_step'],
        final_visit_imbalance=episode['final_visit_imbalance'],timing=episode['timing'])


def paired_stats(values,config):
    mean=statistics.mean(r['difference'] for r in values)
    se=statistics.stdev(r['difference'] for r in values)/math.sqrt(len(values)) if len(values)>1 else None
    return dict(mean_difference=mean,seed_se=se,normal95=None if se is None else
                [mean-config['normal_interval_z']*se,mean+config['normal_interval_z']*se],seeds=len(values),per_seed=values)


def summarize(episodes,config):
    by={(r['seed'],r['world'],r['policy']):r for r in episodes}
    seeds=sorted({r['seed'] for r in episodes})
    comparisons=config['primary_comparators']+config['descriptive_comparators']
    per_world=[]
    for world in config['worlds']:
        for comparator in comparisons:
            values=[dict(seed=s,difference=by[s,world['id'],'lookahead2']['auc_excess_log_loss']-
                        by[s,world['id'],comparator]['auc_excess_log_loss']) for s in seeds
                    if (s,world['id'],'lookahead2') in by and (s,world['id'],comparator) in by]
            if values:
                per_world.append(dict(world=world['id'],comparator=comparator,**paired_stats(values,config)))
    pooled=[]
    for comparator in comparisons:
        values=[]
        for seed in seeds:
            if all((seed,w,p) in by for w in config['primary_worlds'] for p in ('lookahead2',comparator)):
                values.append(dict(seed=seed,difference=statistics.mean(
                    by[seed,w,'lookahead2']['auc_excess_log_loss']-by[seed,w,comparator]['auc_excess_log_loss']
                    for w in config['primary_worlds'])))
        if values:
            pooled.append(dict(comparator=comparator,**paired_stats(values,config)))
    cells=[]
    keys=('auc_excess_log_loss','final_excess_log_loss','final_squared_probability_error',
          'final_blocked_squared_error','final_coverage','tie_count','final_visit_imbalance')
    for world in config['worlds']:
        for policy in config['policies']:
            rows=[r for r in episodes if r['world']==world['id'] and r['policy']==policy]
            if not rows:
                continue
            cells.append(dict(world=world['id'],policy=policy,n=len(rows),
                **{k:statistics.mean(r[k] for r in rows) for k in keys},
                full_coverage_episodes=sum(r['first_full_coverage_step'] is not None for r in rows),
                two_step={str(n):{k:statistics.mean(r['two_step'][str(n)][k] for r in rows)
                          for k in ('expected_log_loss','excess_log_loss')} for n in config['two_step_checkpoints']},
                timing={k:sum(r['timing'][k] for r in rows) for k in rows[0]['timing']}))
    return dict(episodes=episodes,cells=cells,paired_primary=pooled,paired_per_world=per_world,
                interval_scope='policy/tie randomisation in fixed primary worlds; not environment generalisation')


def decision(summary,config,complete):
    expected={(s,w['id'],p) for s in config['seeds'] for w in config['worlds'] for p in config['policies']}
    rows=summary['episodes']
    observed={(r['seed'],r['world'],r['policy']) for r in rows}
    complete=bool(complete and observed==expected and len(rows)==len(expected) and
        all(r['steps']==config['steps'] and r['record_count']==config['steps']+1 for r in rows))
    pooled=[r for r in summary['paired_primary'] if r['comparator'] in config['primary_comparators']]
    guards=[r for r in summary['paired_per_world'] if r['world'] in config['primary_worlds']
            and r['comparator'] in config['primary_comparators']]
    pool_ok=len(pooled)==2 and all(r['mean_difference']<=config['pooled_max_difference'] for r in pooled)
    guard_ok=len(guards)==6 and all(r['mean_difference']<=config['per_world_max_difference'] for r in guards)
    passed=bool(complete and pool_ok and guard_ok)
    mixed=bool(complete and pool_ok and not guard_ok)
    return dict(complete=complete,passed=passed,mixed=mixed,pooled_pass=pool_ok,per_world_guard_pass=guard_ok,
        completed_episodes=len(rows),expected_episodes=len(expected),
        conclusion='bounded shallow coverage-planning benefit' if passed else
                   'mixed; primary screen failed' if mixed else 'no claimed primary planning benefit',
        limitation='supplied tabular state and prior; deterministic-world gain reduces to visit counting; no post-result tuning')


def validate_config(config):
    fixed=dict(schema_version=1,steps=96,seeds=list(range(500,532)),smoke_seeds=[490],policies=list(POLICIES),
        dirichlet_prior=.5,states=4,actions=[0,1,2],outcomes=5,blocked_outcome=4,start_state=0,start_arm=0,
        query_row_weight=1/12,query_pair_weight=1/36,hidden_query_arm_probability=.5,
        two_step_checkpoints=[0,24,48,96],tie_tolerance=1e-12,negative_score_tolerance=1e-10,
        observation_seed_offset=7000003,policy_seed_offset=8000009,policy_seed_multiplier=100,
        primary_worlds=['gate_on','gate_off','directional'],primary_comparators=['random','greedy'],
        descriptive_comparators=['cycle'],pooled_max_difference=-.01,per_world_max_difference=.01,
        normal_interval_z=1.959963984540054,timeout_seconds=120,external_timeout_seconds=150,
        max_output_bytes=100000000,smoke_safety_factor=1.25,smoke_projection_limit_seconds=72,
        smoke_projection_limit_bytes=80000000,loop_order='seed,world,policy')
    if any(config[k]!=v for k,v in fixed.items()):
        raise ValueError('fixed protocol parameters differ')
    worlds=[(w['id'],w['kind'],w.get('gate')) for w in config['worlds']]
    if worlds!=[('gate_on','visible_gate','power_on'),('gate_off','visible_gate','power_off'),
                ('directional','visible_gate','power_differs_door'),('random_room','uniform_accepted',None),
                ('hidden_arm','hidden_arm',None)]:
        raise ValueError('world definitions differ')


def output_scope(output):
    output,runs=Path(output).resolve(),(ROOT/'results/runs').resolve()
    if ROOT not in runs.parents or output.parent!=runs or not output.name.startswith('stateful_room_'):
        raise ValueError('use fresh results/runs/stateful_room_<label>')
    if output.exists():
        raise FileExistsError('output exists')
    return output


def source_hashes():
    paths=[Path(__file__).resolve(),ROOT/'tests/test_stateful_room.py',ROOT/'experiments/stateful_room_v0.md',
           ROOT/'artificial_scientist/run.py']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def verify_smoke(path,config_hash,sources,config):
    path=Path(path).resolve()
    if ROOT not in path.parents:
        raise ValueError('smoke outside repository')
    meta=json.loads((path/'metadata.json').read_text())
    if (meta.get('status')!='completed' or meta.get('mode')!='smoke' or meta.get('completed_episodes')!=20
            or not meta.get('sources_unchanged') or meta.get('source_sha256')!=sources or meta.get('config_sha256')!=config_hash):
        raise ValueError('smoke provenance/completion mismatch')
    required={'config.json','worlds.json','trajectories.jsonl','summary.json','decision.json'}
    if set(meta.get('artifact_sha256',{}))!=required:
        raise ValueError('smoke artifact manifest incomplete')
    for name,digest in meta['artifact_sha256'].items():
        if Path(name).name!=name or hashlib.sha256((path/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('smoke artifact mismatch')
    size=sum(p.stat().st_size for p in path.iterdir() if p.is_file())
    elapsed=meta['elapsed_seconds']
    if size!=meta['artifact_bytes'] or not isinstance(elapsed,(int,float)) or not math.isfinite(elapsed) or elapsed<=0:
        raise ValueError('invalid smoke size/time')
    factor=config['smoke_safety_factor']/20*640
    projected_time,projected_bytes=factor*elapsed,factor*size
    if projected_time>config['smoke_projection_limit_seconds'] or projected_bytes>config['smoke_projection_limit_bytes']:
        raise RuntimeError('resource no-go: smoke exceeds fixed time/disk projection')
    return dict(path=str(path.relative_to(ROOT)),projected_full_seconds=projected_time,
                projected_full_bytes=projected_bytes,metadata_sha256=hashlib.sha256((path/'metadata.json').read_bytes()).hexdigest())


def run(config_path,output,smoke=False,smoke_evidence=None):
    config_path=Path(config_path).resolve()
    if ROOT not in config_path.parents:
        raise ValueError('config outside repository')
    raw=config_path.read_bytes()
    config=json.loads(raw)
    validate_config(config)
    output=output_scope(output)
    sources,config_hash=source_hashes(),hashlib.sha256(raw).hexdigest()
    if not smoke and smoke_evidence is None:
        raise ValueError('full run requires --smoke-evidence')
    evidence=None if smoke else verify_smoke(smoke_evidence,config_hash,sources,config)
    start=time.perf_counter()
    meta=dict(git_info(ROOT),status='running',mode='smoke' if smoke else 'full',source_sha256=sources,
        config_sha256=config_hash,smoke_evidence=evidence,python=platform.python_version(),platform=platform.platform(),
        seeds=config['smoke_seeds'] if smoke else config['seeds'],external_timeout_seconds=config['external_timeout_seconds'],
        schema_version=1,seed_status='inspected development; primary intervals reflect policy/tie randomness')
    output.mkdir(parents=True,exist_ok=False)
    used=0
    def write(name,data):
        nonlocal used
        text=json.dumps(data,indent=2,allow_nan=False)+'\n'
        used+=len(text.encode())
        if used>config['max_output_bytes']:
            raise RuntimeError('output cap reached')
        (output/name).write_text(text)
    write('config.json',config)
    write('metadata.json',meta)
    references={w['id']:evaluator_reference(w,config) for w in config['worlds']}
    write('worlds.json',[dict(id=w['id'],label=w['label'],description=w['description'],
        one_step_reference_rows=references[w['id']]['rows']) for w in config['worlds']])
    episodes,error=[],None
    try:
        with (output/'trajectories.jsonl').open('w') as handle:
            for seed in meta['seeds']:
                for world in config['worlds']:
                    for policy in config['policies']:
                        episode=episode_record(world,seed,policy,config,start+config['timeout_seconds'],references[world['id']])
                        text=json.dumps(episode,separators=(',',':'),allow_nan=False)+'\n'
                        used+=len(text.encode())
                        if used>config['max_output_bytes']-5_000_000:
                            raise RuntimeError('output cap reserve reached')
                        handle.write(text)
                        handle.flush()
                        episodes.append(episode_summary(episode))
        meta['status']='completed'
    except Exception as exc:
        error=exc
        meta.update(status='failed_partial',error=type(exc).__name__+': '+str(exc))
    finally:
        meta['sources_unchanged']=sources==source_hashes() and hashlib.sha256(config_path.read_bytes()).hexdigest()==config_hash
        if not meta['sources_unchanged']:
            meta['status']='invalid_source_changed'
        expected=20 if smoke else 640
        if len(episodes)!=expected and meta['status']=='completed':
            meta['status']='incomplete'
        summary=summarize(episodes,config)
        result=decision(summary,config,meta['status']=='completed' and not smoke)
        write('summary.json',summary)
        write('decision.json',result)
        meta.update(completed_episodes=len(episodes),expected_episodes=expected,completed_observations=len(episodes)*config['steps'],
                    elapsed_seconds=time.perf_counter()-start)
        meta['artifact_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()
                                if p.is_file() and p.name!='metadata.json'}
        other_bytes=sum(p.stat().st_size for p in output.iterdir() if p.is_file() and p.name!='metadata.json')
        meta['artifact_bytes']=0
        for _ in range(20):
            if smoke:
                factor=config['smoke_safety_factor']/20*640
                meta.update(projected_full_seconds=factor*meta['elapsed_seconds'],projected_full_bytes=factor*meta['artifact_bytes'])
                meta['resource_go']=(meta['status']=='completed' and meta['projected_full_seconds']<=config['smoke_projection_limit_seconds']
                                     and meta['projected_full_bytes']<=config['smoke_projection_limit_bytes'])
            size=other_bytes+len((json.dumps(meta,indent=2,allow_nan=False)+'\n').encode())
            if size==meta['artifact_bytes']:
                break
            meta['artifact_bytes']=size
        else:
            raise RuntimeError('metadata byte count did not stabilise')
        write('metadata.json',meta)
    if error is not None:
        raise error
    if meta['status']!='completed':
        raise RuntimeError('run incomplete or invalid; see preserved records')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path('experiments/stateful_room_v0.json'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--smoke-evidence',type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.config,args.output,args.smoke,args.smoke_evidence),indent=2))
