"""Recorded Bayesian switch laboratory; supplied hypotheses and fixed toy worlds."""
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

ROOT = Path(__file__).resolve().parents[1]
POLICIES = ('hybrid_epig', 'hybrid_random', 'hybrid_roundrobin', 'structured_epig')


def entropy(p):
    if not 0 <= p <= 1:
        raise ValueError('probability outside [0,1]')
    return -(p*math.log(p) if p else 0.) - ((1-p)*math.log1p(-p) if p < 1 else 0.)


def logsumexp(values):
    maximum = max(values)
    if maximum == -math.inf:
        raise ValueError('observation has zero predictive probability')
    return maximum+math.log(math.fsum(math.exp(v-maximum) for v in values))


def bits(action):
    return [(action >> 2) & 1, (action >> 1) & 1, action & 1]


def rule_value(name, state):
    if name in ('false', 'true'):
        return int(name == 'true')
    if name == 'majority':
        return int(sum(state) >= 2)
    if name in ('A', 'B', 'C'):
        return state['ABC'.index(name)]
    if name.startswith('not_'):
        return 1-state['ABC'.index(name[-1])]
    operation, pair = name.split('_')
    a, b = [state['ABC'.index(letter)] for letter in pair]
    if operation == 'and':
        return a & b
    if operation == 'or':
        return a | b
    if operation == 'xor':
        return a ^ b
    raise ValueError('unknown Boolean function')


def rule_probabilities(name, noise):
    if name == 'fair':
        return [.5]*8
    return [1-noise if rule_value(name, bits(a)) else noise for a in range(8)]


def make_library(config):
    hypotheses = []
    for name in config['structured_functions']:
        for noise in config['structured_noise']:
            hypotheses.append(dict(id=f'{name}_e{noise:g}', label=f'{name.replace("_", " ")} / {noise:.0%} noise',
                probabilities=rule_probabilities(name, noise)+[config['noise_probability']]))
    if config['include_fair_hypothesis']:
        hypotheses.append(dict(id='fair', label='Fair random lamp', probabilities=[.5]*9))
    return dict(hypotheses=hypotheses, actions=[dict(id=a, bits=bits(a) if a<8 else None,
        label=f'Switches {a:03b}' if a<8 else 'Known fair noise lamp') for a in range(9)])


def make_worlds(config):
    return [dict(id=w['id'], label=w['label'], true_probabilities=rule_probabilities(w['function'], w['noise']),
                 in_family_primary=w['id'] in config['primary_worlds']) for w in config['worlds']]


class Learner:
    """Receives only a supplied library, action and observation; no hidden world."""
    def __init__(self, config, hybrid=True, library=None):
        self.config = {key:config[key] for key in (
            "noise_action", "noise_probability", "query_weights", "negative_score_tolerance")}
        self.library = make_library(config)['hypotheses'] if library is None else library
        self.tables = [h['probabilities'] for h in self.library]
        self.columns = list(zip(*self.tables))
        fallback = config['fallback_prior_mass'] if hybrid else 0.
        self.log_weights = [math.log((1-fallback)/len(self.tables))]*len(self.tables)
        self.log_weights.append(math.log(fallback) if fallback else -math.inf)
        self.beta = [list(config['beta_prior']) for _ in range(8)]

    def weights(self):
        return [math.exp(w) for w in self.log_weights]

    def query_predictions(self):
        weights = self.weights()
        return [math.fsum(w*p for w, p in zip(weights[:-1], column))+
                weights[-1]*a/(a+b) for column, (a,b) in zip(self.columns[:8], self.beta)]

    def predictive(self, action):
        if type(action) is not int or not 0 <= action <= 8:
            raise ValueError('action must be 0..8')
        return self.config['noise_probability'] if action == 8 else self.query_predictions()[action]

    def observe(self, action, outcome):
        if type(action) is not int or not 0 <= action <= 8 or type(outcome) is not int or outcome not in (0,1):
            raise ValueError('valid action and binary observation required')
        if action == self.config['noise_action']:
            return
        a, b = self.beta[action]
        likelihoods = list(self.columns[action])+[a/(a+b)]
        logs = [w+math.log(p if outcome else 1-p) if (p if outcome else 1-p)>0 else -math.inf
                for w, p in zip(self.log_weights, likelihoods)]
        normalizer = logsumexp(logs)
        self.log_weights = [w-normalizer for w in logs]
        self.beta[action][0 if outcome else 1] += 1

    def epig_scores(self):
        weights, q = self.weights(), self.query_predictions()
        means = [a/(a+b) for a,b in self.beta]
        variances = [a*b/((a+b)**2*(a+b+1)) for a,b in self.beta]
        joint = [[0.]*8 for _ in range(8)]
        for a in range(8):
            for b in range(a,8):
                value = math.fsum(w*pa*pb for w,pa,pb in zip(weights[:-1], self.columns[a], self.columns[b]))
                value += weights[-1]*(means[a]*means[b]+(variances[a] if a==b else 0.))
                joint[a][b] = joint[b][a] = value
        scores = []
        for a in range(8):
            terms = []
            for b in range(8):
                # Independent future draw shares its unknown Beta parameter with the experiment.
                one = joint[a][b]/q[a] if q[a] else q[b]
                zero = (q[b]-joint[a][b])/(1-q[a]) if q[a]<1 else q[b]
                if not -1e-12 <= one <= 1+1e-12 or not -1e-12 <= zero <= 1+1e-12:
                    raise ArithmeticError('invalid joint predictive distribution')
                one, zero = min(1.,max(0.,one)), min(1.,max(0.,zero))
                terms.append(self.config['query_weights'][b]*(entropy(q[b])-q[a]*entropy(one)-(1-q[a])*entropy(zero)))
            value = math.fsum(terms)
            if value < -self.config['negative_score_tolerance']:
                raise ArithmeticError('substantially negative information score')
            scores.append(max(0., value))
        return scores+[0.]


def choose_action(policy, learner, step, rng, config):
    scores = None
    if policy.endswith('_epig'):
        scores = learner.epig_scores()
        maximum = max(scores[a] for a in config['allowed_actions'])
        choices = [a for a in config['allowed_actions'] if maximum-scores[a] <= config['tie_tolerance']]
        action = rng.choice(choices)
    elif policy == 'hybrid_random':
        action = rng.choice(config['allowed_actions'])
    elif policy == 'hybrid_roundrobin':
        action = config['allowed_actions'][step % len(config['allowed_actions'])]
    else:
        raise ValueError('unknown policy')
    return action, scores


def evaluate_state(learner, world, config):
    predictions, weights = learner.query_predictions(), learner.weights()
    truth = world['true_probabilities']
    expected = math.fsum(w*(-t*math.log(p)-(1-t)*math.log1p(-p))
                        for w,t,p in zip(config['query_weights'], truth, predictions))
    irreducible = math.fsum(w*entropy(t) for w,t in zip(config['query_weights'], truth))
    matching = [i for i,h in enumerate(learner.library)
                if all(abs(p-t)<1e-12 for p,t in zip(h['probabilities'][:8],truth))]
    top = sorted(range(len(learner.library)), key=lambda i:(-weights[i],i))[:config['top_hypotheses']]
    return dict(query_probabilities=predictions,
        top_hypotheses=[dict(id=learner.library[i]['id'], label=learner.library[i]['label'], posterior_mass=weights[i]) for i in top],
        fallback_weight=weights[-1], query_metrics=dict(expected_log_loss=expected,
        excess_log_loss=expected-irreducible,
        excess_brier=math.fsum(w*(p-t)**2 for w,p,t in zip(config['query_weights'],predictions,truth)),
        true_hypothesis_mass=math.fsum(weights[i] for i in matching) if matching else None))


def observation_uniforms(seed, config):
    rng = random.Random(config['observation_seed_offset']+seed)
    return [[rng.random() for _ in range(9)] for _ in range(config['steps'])]


def episode_record(world, seed, policy, config, deadline=math.inf, library=None):
    if policy not in config['policies']:
        raise ValueError('undeclared policy')
    learner = Learner(config, hybrid=policy!='structured_epig', library=library)
    rng = random.Random(config['policy_seed_offset']+config['policy_seed_multiplier']*seed+config['policies'].index(policy))
    uniforms = observation_uniforms(seed, config)
    policy_config = {key:config[key] for key in ('allowed_actions','tie_tolerance')}
    timing = dict(acquisition_seconds=0., prediction_seconds=0., update_seconds=0.)
    records = [dict(step=0, action=None, outcome=None, pre_action_probability=None,
                    acquisition_scores=None, **evaluate_state(learner,world,config))]
    for step in range(config['steps']):
        if time.perf_counter()>deadline:
            raise TimeoutError('internal experiment deadline reached')
        start = time.perf_counter()
        action, scores = choose_action(policy,learner,step,rng,policy_config)
        timing['acquisition_seconds'] += time.perf_counter()-start
        start = time.perf_counter()
        probability = learner.predictive(action)
        timing['prediction_seconds'] += time.perf_counter()-start
        truth = config['noise_probability'] if action==8 else world['true_probabilities'][action]
        outcome = int(uniforms[step][action]<truth)
        start = time.perf_counter()
        learner.observe(action,outcome)
        timing['update_seconds'] += time.perf_counter()-start
        records.append(dict(step=step+1,action=action,outcome=outcome,pre_action_probability=probability,
                            acquisition_scores=scores,**evaluate_state(learner,world,config)))
    return dict(schema_version=1,world=world['id'],seed=seed,policy=policy,steps=config['steps'],
                records=records,timing=timing,
                noise_action_count=sum(r['action']==config['noise_action'] for r in records[1:]))


def episode_summary(episode):
    records = episode['records'][1:]
    final = records[-1]['query_metrics']
    return dict(world=episode['world'],seed=episode['seed'],policy=episode['policy'],
        auc_excess_log_loss=statistics.mean(r['query_metrics']['excess_log_loss'] for r in records),
        final_excess_log_loss=final['excess_log_loss'], final_excess_brier=final['excess_brier'],
        final_true_hypothesis_mass=final['true_hypothesis_mass'],
        final_fallback_weight=records[-1]['fallback_weight'],noise_action_count=episode['noise_action_count'],
        timing=episode['timing'])


def summarize(episodes, config):
    cells = []
    for world in [w['id'] for w in config['worlds']]:
        for policy in config['policies']:
            rows = [r for r in episodes if r['world']==world and r['policy']==policy]
            if rows:
                cells.append(dict(world=world,policy=policy,n=len(rows),noise_action_count=sum(r['noise_action_count'] for r in rows),
                    **{key:statistics.mean(r[key] for r in rows) for key in
                       ('auc_excess_log_loss','final_excess_log_loss','final_excess_brier','final_fallback_weight')},
                    timing={key:sum(r['timing'][key] for r in rows) for key in rows[0]['timing']}))
    by = {(r['seed'],r['world'],r['policy']):r['auc_excess_log_loss'] for r in episodes}
    paired = []
    for comparator in ('hybrid_random','hybrid_roundrobin'):
        per_seed = []
        for seed in sorted({r['seed'] for r in episodes}):
            keys = [(seed,w,p) for w in config['primary_worlds'] for p in ('hybrid_epig',comparator)]
            if all(k in by for k in keys):
                per_seed.append(dict(seed=seed,difference=statistics.mean(
                    by[seed,w,'hybrid_epig']-by[seed,w,comparator] for w in config['primary_worlds'])))
        if per_seed:
            mean = statistics.mean(r['difference'] for r in per_seed)
            se = statistics.stdev(r['difference'] for r in per_seed)/math.sqrt(len(per_seed)) if len(per_seed)>1 else None
            paired.append(dict(comparator=comparator,mean_difference=mean,seed_se=se,
                normal95=[mean-config['normal_interval_z']*se,mean+config['normal_interval_z']*se] if se is not None else None,
                seeds=len(per_seed),per_seed=per_seed))
    return dict(episodes=episodes,cells=cells,paired_primary=paired,
                auc_definition='arithmetic mean of post-update excess query log loss over steps1..48')


def decision(summary, config, complete):
    expected = {(s,w['id'],p) for s in config['seeds'] for w in config['worlds'] for p in config['policies']}
    rows = summary['episodes']
    observed = {(r['seed'],r['world'],r['policy']) for r in rows}
    complete = complete and observed==expected and len(rows)==len(expected)
    paired = summary['paired_primary']
    passed = bool(complete and len(paired)==2 and all(r['seeds']==len(config['seeds']) and
                  r['mean_difference']<=config['screen_max_difference'] for r in paired))
    return dict(complete=bool(complete),passed=passed,completed_episodes=len(rows),expected_episodes=len(expected),
        screen_max_difference=config['screen_max_difference'],
        meaning='exploratory predictive sample efficiency in four supplied-library worlds only',
        consequence='report bounded toy benefit only' if passed else 'no claimed primary benefit; no acquisition tuning in this version')


def source_hashes():
    paths = [Path(__file__).resolve(),ROOT/'tests/test_interactive_lab.py',
             ROOT/'experiments/interactive_lab_v0.md',ROOT/'artificial_scientist/run.py']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def validate_config(config):
    if (config['steps']!=48 or config['seeds']!=list(range(400,440)) or config['smoke_seeds']!=[390]
            or config['policies']!=list(POLICIES) or config['allowed_actions']!=list(range(8))
            or config['noise_action']!=8 or config['noise_probability']!=.5
            or config['structured_noise']!=[.05,.2] or config['fallback_prior_mass']!=.2
            or config['beta_prior']!=[1.,1.] or config['query_weights']!=[.125]*8):
        raise ValueError('fixed design differs from reviewed protocol')
    expected_functions = ['false','true','A','not_A','B','not_B','C','not_C']+[
        op+'_'+pair for op in ('and','or','xor') for pair in ('AB','AC','BC')]
    if config['structured_functions']!=expected_functions or config['include_fair_hypothesis'] is not True:
        raise ValueError('structured library differs')
    fixed = dict(schema_version=1,tie_tolerance=1e-12,negative_score_tolerance=1e-10,
        observation_seed_offset=5000003,policy_seed_offset=6000011,policy_seed_multiplier=100,
        primary_worlds=['lamp_a','and_ab','xor_ab','or_ac'],screen_max_difference=-.01,
        normal_interval_z=1.959963984540054,timeout_seconds=120,external_timeout_seconds=150,
        max_output_bytes=100000000,smoke_projection_limit_seconds=72,smoke_safety_factor=1.25,
        top_hypotheses=3,loop_order='seed,world,policy')
    if any(config[k]!=v for k,v in fixed.items()):
        raise ValueError('reviewed constants differ')
    expected = [('lamp_a','A',.05),('and_ab','and_AB',.05),('xor_ab','xor_AB',.05),
                ('or_ac','or_AC',.2),('random','fair',.5),('majority','majority',.05)]
    if [(w['id'],w['function'],w['noise']) for w in config['worlds']]!=expected:
        raise ValueError('world definitions differ')


def output_scope(output):
    output,runs = Path(output).resolve(),(ROOT/'results/runs').resolve()
    if ROOT not in runs.parents or output.parent!=runs or not output.name.startswith('interactive_lab_'):
        raise ValueError('use fresh results/runs/interactive_lab_<label>')
    if output.exists():
        raise FileExistsError('output exists')
    return output


def verify_smoke(path,config_hash,sources,config):
    path=Path(path).resolve()
    if ROOT not in path.parents:
        raise ValueError('smoke must be in repository')
    meta=json.loads((path/'metadata.json').read_text())
    if (meta.get('status')!='completed' or meta.get('mode')!='smoke' or meta.get('completed_episodes')!=24
            or not meta.get('sources_unchanged') or meta.get('config_sha256')!=config_hash
            or meta.get('source_sha256')!=sources):
        raise ValueError('smoke evidence does not match source/config or completion')
    for name,digest in meta['artifact_sha256'].items():
        if Path(name).name!=name or hashlib.sha256((path/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('smoke artifact changed')
    elapsed=meta['elapsed_seconds']
    if not isinstance(elapsed,(int,float)) or not math.isfinite(elapsed) or elapsed<=0:
        raise ValueError('invalid smoke elapsed time')
    projection=config['smoke_safety_factor']*elapsed/24*960
    if projection>config['smoke_projection_limit_seconds']:
        raise RuntimeError('resource no-go: smoke projection exceeds72seconds')
    return dict(path=str(path.relative_to(ROOT)),projected_full_seconds=projection,
        metadata_sha256=hashlib.sha256((path/'metadata.json').read_bytes()).hexdigest())


def run(config_path,output,smoke=False,smoke_evidence=None):
    config_path=Path(config_path).resolve()
    if ROOT not in config_path.parents:
        raise ValueError('config must be in repository')
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
        seed_status='inspected development; no held-out claim',schema_version=1)
    output.mkdir(parents=True,exist_ok=False)
    used=0
    def write(name,data):
        nonlocal used
        text=json.dumps(data,indent=2,allow_nan=False)+'\n'
        used+=len(text.encode())
        if used>config['max_output_bytes']:
            raise RuntimeError('artifact cap reached')
        (output/name).write_text(text)
    write('config.json',config)
    write('metadata.json',meta)
    worlds,library=make_worlds(config),make_library(config)
    write('worlds.json',worlds)
    write('library.json',library)
    episodes,error=[],None
    try:
        with (output/'trajectories.jsonl').open('w') as handle:
            for seed in meta['seeds']:
                for world in worlds:
                    for policy in config['policies']:
                        episode=episode_record(world,seed,policy,config,start+config['timeout_seconds'],library['hypotheses'])
                        text=json.dumps(episode,separators=(',',':'),allow_nan=False)+'\n'
                        used+=len(text.encode())
                        if used>config['max_output_bytes']-5_000_000:
                            raise RuntimeError('artifact cap reserve reached')
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
        expected=24 if smoke else 960
        if len(episodes)!=expected and meta['status']=='completed':
            meta['status']='incomplete'
        summary=summarize(episodes,config)
        result=decision(summary,config,meta['status']=='completed' and not smoke)
        write('summary.json',summary)
        write('decision.json',result)
        meta.update(completed_episodes=len(episodes),expected_episodes=expected,elapsed_seconds=time.perf_counter()-start,
                    completed_observations=len(episodes)*config['steps'])
        if smoke:
            meta['projected_full_seconds']=config['smoke_safety_factor']*meta['elapsed_seconds']/24*960
            meta['resource_go']=meta['status']=='completed' and meta['projected_full_seconds']<=config['smoke_projection_limit_seconds']
        meta['artifact_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()
                                if p.is_file() and p.name!='metadata.json'}
        write('metadata.json',meta)
    if error is not None:
        raise error
    if meta['status']!='completed':
        raise RuntimeError('run incomplete/invalid; see preserved artifacts')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path('experiments/interactive_lab_v0.json'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--smoke-evidence',type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.config,args.output,args.smoke,args.smoke_evidence),indent=2))
