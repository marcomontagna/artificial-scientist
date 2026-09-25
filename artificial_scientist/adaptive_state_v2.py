"""Reversible context selection against slow and fast simple alternatives."""
import argparse
import csv
import hashlib
import json
import math
import platform
import random
import statistics
import time
from collections import deque
from pathlib import Path

from .adaptive_state import AdaptiveContext, SparsePredictor, SparseMixture, validate
from .metrics import scores
from .run import git_info
from .sequence_worlds import ContextPredictor, probability_one

CONDITIONS = ('stable', 'parameter', 'noise') + tuple('structural'+str(k) for k in range(2, 6))
NAMES = ('slow', 'fast', 'v1', 'sparse_mixture', 'matched_mixture', 'v2')


def bank(discount=.99, fast_discount=.90):
    return [SparsePredictor((1,), d) for d in (discount, fast_discount)] + [
        SparsePredictor((1, k), discount) for k in range(2, 6)]


class MatchedMixture:
    def __init__(self, discount=.99, fast_discount=.90, share=.01):
        self.models = bank(discount, fast_discount)
        self.weights = [1/6] * 6
        self.share = share

    def predict(self):
        return sum(w*m.predict() for w,m in zip(self.weights, self.models))

    def update(self, outcome):
        ls = [m.predict() if outcome else 1-m.predict() for m in self.models]
        z = sum(w*p for w,p in zip(self.weights, ls))
        self.weights = [(1-self.share)*w*p/z+self.share/6 for w,p in zip(self.weights, ls)]
        for model in self.models:
            model.update(outcome)

    def storage(self):
        return 6 + sum(m.storage() for m in self.models)


class ReversibleContext:
    def __init__(self, discount=.99, fast_discount=.90, window=128, every=64, threshold=math.log(400)):
        if type(window) is not int or window<1 or type(every) is not int or every<1:
            raise ValueError('positive integer window/period required')
        if not math.isfinite(threshold) or threshold<0:
            raise ValueError('finite nonnegative threshold required')
        self.models = bank(discount, fast_discount)
        self.losses = [deque(maxlen=window) for _ in self.models]
        self.window,self.every,self.threshold = window,every,threshold
        self.active = self.observed = self.checks = 0

    def predict(self):
        return self.models[self.active].predict()

    def storage(self):
        return sum(m.storage() for m in self.models) + 6*self.window + 6

    def update(self, outcome):
        if outcome not in (0,1):
            raise ValueError('binary outcome required')
        for losses,model in zip(self.losses,self.models):
            losses.append(scores(model.predict(),outcome)['log_loss'])
        for model in self.models:
            model.update(outcome)
        self.observed += 1
        if self.observed < self.window or self.observed % self.every:
            return None
        self.checks += 1
        totals = [sum(x) for x in self.losses]
        simple = min(range(2), key=lambda i:totals[i])
        sparse = min(range(2,6), key=lambda i:totals[i])
        gain = totals[simple]-totals[sparse]
        choice = sparse if gain>self.threshold else simple
        previous = self.active
        self.active = choice
        if previous == choice:
            return None
        kind = ('expand' if previous<2<=choice else 'contract' if choice<2<=previous
                else 'speed' if choice<2 else 'reselect')
        return dict(observed_tick=self.observed-1,effective_tick=self.observed,
                    previous_expert=previous,selected_expert=choice,
                    selected_lag=self.models[choice].lags[-1],kind=kind,
                    window_gain=gain)


def generate(seed, condition, steps, change):
    if condition not in CONDITIONS:
        raise ValueError('unknown condition')
    structural = condition.startswith('structural')
    lag = int(condition[-1]) if structural else 1
    history = deque(random.Random(seed+3000001).choices((0,1),k=5),maxlen=5)
    noise = random.Random(seed+2000003)
    result = []
    for tick in range(steps):
        p = probability_one(history,'structural' if structural else condition,tick>=change,lag)
        y = int(noise.random()<p)
        result.append(y)
        history.append(y)
    return result, lag


def learners(config):
    d,f,s = config['discount'],config['fast_discount'],config['share']
    kw = dict(discount=d,window=config['gain_window'],every=config['check_every'],threshold=config['gain_threshold'])
    return dict(slow=ContextPredictor(1,d),fast=ContextPredictor(1,f),v1=AdaptiveContext(**kw),
                sparse_mixture=SparseMixture(d,s),matched_mixture=MatchedMixture(d,f,s),
                v2=ReversibleContext(**kw,fast_discount=f))


def simulate(config):
    validate(config)
    if not 0<config['fast_discount']<=1 or config['steps']*len(config['seeds'])*42>300000:
        raise ValueError('invalid fast discount or run exceeds 300000 rows')
    rows,summary,events,timings,decisions = [],[],[],[],[]
    for seed in config['seeds']:
        for condition in CONDITIONS:
            stream,lag = generate(seed,condition,config['steps'],config['change_at'])
            models = learners(config)
            groups = {(n,p):[] for n in NAMES for p in ('before','after')}
            durations = {n:0. for n in NAMES}
            for tick,outcome in enumerate(stream):
                phase = 'before' if tick<config['change_at'] else 'after'
                for name,m in models.items():
                    t=time.perf_counter();p=m.predict();durations[name]+=time.perf_counter()-t
                    dynamic = name in ('v1','v2')
                    active_model = m.models[m.active] if dynamic else None
                    row=dict(seed=seed,condition=condition,tick=tick,phase=phase,baseline=name,
                             outcome=outcome,probability=p,logical_slots=m.storage(),
                             active_expert=m.active if dynamic else '',
                             active_lag=active_model.lags[-1] if dynamic else '',
                             active_width=len(active_model.lags) if dynamic else '',
                             checks=m.checks if dynamic else '',**scores(p,outcome))
                    rows.append(row);groups[name,phase].append(row)
                    t=time.perf_counter();event=m.update(outcome);durations[name]+=time.perf_counter()-t
                    if event is not None:
                        events.append(dict(seed=seed,condition=condition,baseline=name,evaluator_lag=lag,**event))
            for (name,phase),group in groups.items():
                summary.append(dict(seed=seed,condition=condition,baseline=name,phase=phase,
                                    evaluator_lag=lag,n=len(group),**{k:statistics.mean(r[k] for r in group)
                                    for k in ('log_loss','brier','logical_slots')}))
            for name in ('v1','v2'):
                group=groups[name,'before']+groups[name,'after']
                switched=sum(a['active_expert']!=b['active_expert'] for a,b in zip(group,group[1:]))
                expanded=[r for r in group if r['active_width']==2]
                decisions.append(dict(seed=seed,condition=condition,baseline=name,
                    ever_expanded=bool(expanded),premature=any(r['tick']<config['change_at'] for r in expanded),
                    first_expansion=expanded[0]['tick'] if expanded else None,
                    final_lag=group[-1]['active_lag'],final_expert=group[-1]['active_expert'],
                    switches=switched,mean_dwell=len(group)/(switched+1),
                    correct_fraction_after=(statistics.mean(r['active_lag']==lag for r in groups[name,'after'])
                                            if condition.startswith('structural') else None)))
            timings.extend(dict(seed=seed,condition=condition,baseline=n,prediction_update_seconds=d)
                           for n,d in durations.items())
    return rows,summary,events,timings,decisions


def diagnostic(summary,decisions):
    def expanded(n,c):
        return sum(d['ever_expanded'] for d in decisions if d['baseline']==n and d['condition']==c)
    def penalty(c,ref):
        by={(r['seed'],r['condition'],r['baseline']):r['log_loss'] for r in summary
            if r['phase']=='after' and r['condition'].startswith(c)}
        keys=[(seed,cond) for seed,cond,name in by if name=='v2']
        return statistics.mean(by[seed,cond,'v2']-by[seed,cond,ref] for seed,cond in keys)
    correct=sum(d['final_lag']==int(d['condition'][-1]) for d in decisions
                if d['baseline']=='v2' and d['condition'].startswith('structural'))
    result=dict(parameter_expansion_v1=expanded('v1','parameter'),parameter_expansion_v2=expanded('v2','parameter'),
                final_structural_correct=correct,structural_penalty_vs_matched=penalty('structural','matched_mixture'),
                stable_penalty_vs_slow=penalty('stable','slow'),stable_expansions=expanded('v2','stable'),
                noise_expansions=expanded('v2','noise'))
    n=sum(d['baseline']=='v2' and d['condition']=='stable' for d in decisions)
    result['screen_passed']=(result['parameter_expansion_v1']-result['parameter_expansion_v2']>=.6*n
        and correct>=.8*4*n and result['structural_penalty_vs_matched']<=.02
        and result['stable_penalty_vs_slow']<=.01 and result['stable_expansions']<=.2*n
        and result['noise_expansions']<=.2*n)
    result['label']='exploratory engineering screen, not confirmation'
    return result


def run(config_path,output):
    root=Path(__file__).resolve().parents[1];output=Path(output).resolve()
    if root not in output.parents:raise ValueError('output must be inside repository')
    if output.exists():raise FileExistsError('choose fresh output')
    raw=Path(config_path).read_bytes();config=json.loads(raw);started=time.perf_counter()
    rows,summary,events,timings,decisions=simulate(config)
    output.mkdir(parents=True,exist_ok=False);(output/'config.json').write_bytes(raw)
    with (output/'predictions.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    for name,value in [('summary',summary),('events',events),('timings',timings),('decisions',decisions),
                       ('diagnostic',diagnostic(summary,decisions))]:
        (output/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    sources=sorted((root/'artificial_scientist').glob('*.py'))+[root/'experiments/adaptive_state_v2.md']
    meta=dict(git_info(root),python=platform.python_version(),platform=platform.platform(),
        elapsed_seconds=time.perf_counter()-started,config_sha256=hashlib.sha256(raw).hexdigest(),
        predictions_sha256=hashlib.sha256((output/'predictions.csv').read_bytes()).hexdigest(),
        source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        purpose='exploratory reversible expert selection, no novelty/efficiency claim')
    (output/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    return summary,events


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path('experiments/adaptive_state_v2.json'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.config,args.output)
    print('Saved reversible development experiment:',args.output)
