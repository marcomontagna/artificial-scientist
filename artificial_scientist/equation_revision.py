"""One triggered expansion of a supplied polynomial grammar, checked afresh."""
import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import time
from pathlib import Path
from . import equation_discovery as ed
from . import equation_domain as dm
from .run import git_info
ROOT=Path(__file__).resolve().parents[1]
TERMS=ed.TERMS+('x*x*x','u*u*u')
BASE=list(range(6))
SUPPORTS=[BASE,BASE+[6],BASE+[7],list(range(8))]
WORLDS=('quadratic','noise','weak_x','medium_x','strong_x','medium_u','both','exponential')
PIPELINES=('revise_once','never_revise','always_large','always_large_pooled','pooled_bic')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def features(x,u):
    return ed.basis(x,u)+(x**3,u**3)


def predict(coefficients,x,u):
    return math.fsum(a*b for a,b in zip(coefficients,features(x,u)))


def fit(observations,support):
    design=[features(x,u) for x,u,_ in observations]
    outcomes=[y for _,_,y in observations]
    k=len(support)
    q,r=[],[[0.]*k for _ in support]
    for column,j in enumerate(support):
        vector=[row[j] for row in design]
        original=math.sqrt(math.fsum(v*v for v in vector))
        for _ in range(2):
            for i,unit in enumerate(q):
                projection=math.fsum(a*b for a,b in zip(unit,vector))
                r[i][column]+=projection
                vector=[a-projection*b for a,b in zip(vector,unit)]
        norm=math.sqrt(math.fsum(v*v for v in vector))
        if original==0 or norm<=1e-10*original or not math.isfinite(norm):
            raise ArithmeticError('rank-deficient/nonfinite design')
        r[column][column]=norm
        q.append([v/norm for v in vector])
    rhs=[math.fsum(a*b for a,b in zip(unit,outcomes)) for unit in q]
    beta=[0.]*k
    for i in reversed(range(k)):
        beta[i]=(rhs[i]-math.fsum(r[i][j]*beta[j] for j in range(i+1,k)))/r[i][i]
    coefficients=[0.]*8
    for j,value in zip(support,beta):
        coefficients[j]=value
    sse=math.fsum((y-predict(coefficients,x,u))**2 for x,u,y in observations)
    if not all(math.isfinite(x) for x in coefficients+[sse]):
        raise ArithmeticError('nonfinite fitted equation')
    return dict(support=list(support),coefficients=coefficients,sse=sse,r=r,n=len(observations),
                formula=' + '.join(f'({coefficients[j]:.17g})*{TERMS[j]}' for j in support) or '0')


def log_survival(q,df):
    if df<=0 or df%2 or not math.isfinite(q) or q < -1e-10:
        raise ArithmeticError('invalid even chi-square argument')
    if q<=0:
        return 0.
    z=q/2
    logs=[k*math.log(z)-math.lgamma(k+1) for k in range(df//2)]
    maximum=max(logs)
    return min(0.,-z+maximum+math.log(math.fsum(math.exp(v-maximum) for v in logs)))


def whole_check(candidate,observations,sigma=.05):
    predictions=[predict(candidate['coefficients'],x,u) for x,u,_ in observations]
    design=[[features(x,u)[j] for j in candidate['support']] for x,u,_ in observations]
    lower=dm.cholesky(dm.predictive_covariance(candidate['r'],design,sigma))
    q=dm.quadratic_form(lower,[y-p for (_,_,y),p in zip(observations,predictions)])
    log_p=log_survival(q,len(observations))
    return dict(q=q,df=len(observations),log_p=log_p,p_value=math.exp(log_p),rejected=log_p<=math.log(.025),predictions=predictions)


def choose_revision(a,c):
    """Only A/C are available when the supplied extension is chosen."""
    initial=fit(a,BASE)
    before=fingerprint(initial)
    predictions=[predict(initial['coefficients'],x,u) for x,u,_ in c]
    pred_before=fingerprint(predictions)
    check=whole_check(initial,c)
    alternatives=[]
    support=BASE
    if check['rejected']:
        alternatives=[fit(a+c,BASE+[j]) for j in (6,7)]
        minimum=min(m['sse'] for m in alternatives)
        support=min((m for m in alternatives if m['sse']-minimum<=1e-12),key=lambda m:m['support'])['support']
    after=fingerprint(initial)
    pred_after=fingerprint([predict(initial['coefficients'],x,u) for x,u,_ in c])
    if before!=after or pred_before!=pred_after:
        raise ArithmeticError('initial equation mutated')
    return dict(equation=initial,check=check,selected_support=list(support),selected_extension=None if len(support)==6 else support[-1],
                alternatives=alternatives,candidate_sha256_before=before,candidate_sha256_after=after,
                predictions_sha256_before=pred_before,predictions_sha256_after=pred_after)


def candidates(a,c,b,initial):
    pooled=a+c+b
    models=[fit(pooled,support) for support in SUPPORTS]
    for model in models:
        model['score']=model['sse']/.05**2+len(model['support'])*math.log(len(pooled))
    minimum=min(m['score'] for m in models)
    chosen=min((m for m in models if m['score']-minimum<=1e-12),key=lambda m:(len(m['support']),m['support']))
    return dict(revise_once=fit(b,initial['selected_support']),never_revise=fit(b,BASE),
                always_large=fit(b,list(range(8))),always_large_pooled=fit(pooled,list(range(8))),
                pooled_bic=chosen),models


def shared_d_tests(d,sigma=.05):
    full=fit(d,list(range(8)))
    transpose=[list(row) for row in zip(*full['r'])]
    exact=[]
    nulls=[]
    for j in range(8):
        unit=[float(i==j) for i in range(8)]
        vector=dm.solve_lower(transpose,unit)
        se=sigma*math.sqrt(math.fsum(x*x for x in vector))
        z=full['coefficients'][j]/se
        p=math.erfc(abs(z)/math.sqrt(2))
        if not math.isfinite(z):
            raise ArithmeticError('nonfinite exact coefficient test')
        exact.append(dict(term=j,estimate=full['coefficients'][j],se=se,z=z,p_value=p,confirmed=p<=.05/8))
        nulls.append(fit(d,[i for i in range(8) if i!=j]))
    return dict(full_fit=full,exact_tests=exact,null_fits=nulls)


def final_check(candidate,d,pipeline,shared):
    before=fingerprint(candidate)
    predictions=[predict(candidate['coefficients'],x,u) for x,u,_ in d]
    pred_before=fingerprint(predictions)
    sse=math.fsum((y-p)**2 for (_,_,y),p in zip(d,predictions))
    evidence=[(null['sse']-sse)/(2*.05**2) for null in shared['null_fits']]
    if not all(math.isfinite(x) for x in evidence):
        raise ArithmeticError('nonfinite likelihood evidence')
    for j,value in enumerate(evidence):
        if j not in candidate['support'] and value>1e-8:
            raise ArithmeticError('nonselected null likelihood violation')
    for j,value in enumerate(evidence):
        if value>shared['exact_tests'][j]['z']**2/2+1e-8:
            raise ArithmeticError('likelihood evidence exceeds full-model z bound')
    exact=[j for j in candidate['support'] if shared['exact_tests'][j]['confirmed']]
    eclaims=[j for j in candidate['support'] if evidence[j]>=math.log(160)]
    if not set(eclaims)<=set(exact):
        raise ArithmeticError('likelihood claims are not nested in exact claims')
    whole=dict(status='unavailable_post_selection',q=None,df=None,log_p=None,p_value=None,rejected=None)
    if pipeline!='pooled_bic':
        whole=whole_check(candidate,d)
        whole.pop('predictions')
        whole['status']='rejected' if whole['rejected'] else 'not_rejected'
    after=fingerprint(candidate)
    pred_after=fingerprint([predict(candidate['coefficients'],x,u) for x,u,_ in d])
    if before!=after or pred_before!=pred_after:
        raise ArithmeticError('final equation mutated')
    return dict(whole=whole,predictions=predictions,d_mse=sse/len(d),candidate_sse=sse,log_e=evidence,
                exact_claims=exact,e_claims=eclaims,
                exact_unsupported=[j for j in candidate['support'] if j not in exact],
                e_unsupported=[j for j in candidate['support'] if j not in eclaims],
                candidate_sha256_before=before,candidate_sha256_after=after,predictions_sha256_before=pred_before,predictions_sha256_after=pred_after)


def stream_keys(config):
    offsets=[config['law_offset']]+[config[label+'_'+kind+'_offset'] for label in ('a','c','b','d') for kind in ('input','noise')]
    keys=[offset+seed for offset in offsets for seed in config['seeds']+config['smoke_seeds']+config['fixture_seeds']]
    if len(set(keys))!=len(keys):
        raise ValueError('RNG role/seed collision')
    return keys


def streams(seed,config):
    result={}
    for label,n,radius in [('a',24,1),('c',16,2),('b',24,2),('d',24,2)]:
        rng=random.Random(config[label+'_input_offset']+seed)
        noise=random.Random(config[label+'_noise_offset']+seed)
        sites=[(rng.uniform(-radius,radius),rng.uniform(-radius,radius)) for _ in range(n)]
        result[label]=[(x,u,noise.gauss(0,.05)) for x,u in sites]
    return result


def world_catalog(seed):
    q=ed.world_catalog(seed,ed.fixed_config())['sparse_quadratic']['coefficients']+[0.,0.]
    result={}
    for name,x3,u3 in [('quadratic',0,0),('noise',0,0),('weak_x',.01,0),('medium_x',.05,0),('strong_x',.3,0),('medium_u',0,.05),('both',.05,.05),('exponential',0,0)]:
        coefficients=q[:] if name!='noise' else [0.]*8
        coefficients[6:]=[x3,u3]
        result[name]=dict(coefficients=coefficients,support=None if name=='exponential' else [j for j,c in enumerate(coefficients) if c],
                          exponential_addition=.3 if name=='exponential' else 0.)
    return result


def truth(world,x,u):
    return predict(world['coefficients'],x,u)+world['exponential_addition']*math.exp(x)


def evaluate(candidate,check,world):
    selected=set(candidate['support'])
    true=None if world['support'] is None else set(world['support'])
    metrics=dict(sufficient=False if true is None else true<=selected,exact_support=None if true is None else true==selected,
                 raw_false_count=None if true is None else len(selected-true),true_count=None if true is None else len(true),
                 selected_true_count=None if true is None else len(selected&true))
    for label in ('exact','e'):
        claims=set(check[label+'_claims'])
        metrics[label]=dict(false_count=None if true is None else len(claims-true),confirmed_true_count=None if true is None else len(claims&true),
            all_true_recall=None if not true else len(claims&true)/len(true),
            selected_true_recall=None if not true or not selected&true else len(claims&true)/len(selected&true))
    for label,points in ed.query_grids().items():
        key='inner_mse' if label=='interpolation' else 'outer_shell_mse'
        metrics[key]=statistics.mean((predict(candidate['coefficients'],x,u)-truth(world,x,u))**2 for x,u in points)
    return metrics


def episode_record(seed,name,world,shared,config):
    data={label:[(x,u,truth(world,x,u)+noise) for x,u,noise in rows] for label,rows in shared.items()}
    start=time.perf_counter()
    initial=choose_revision(data['a'],data['c'])
    fitted,selection=candidates(data['a'],data['c'],data['b'],initial)
    fit_seconds=time.perf_counter()-start
    # D outcomes are not passed to selection or fitting above.
    start=time.perf_counter()
    dtests=shared_d_tests(data['d'])
    records={p:dict(candidate=candidate,check=final_check(candidate,data['d'],p,dtests)) for p,candidate in fitted.items()}
    check_seconds=time.perf_counter()-start
    for record in records.values():
        record['evaluator_only']=evaluate(record['candidate'],record['check'],world)
    return dict(schema_version=1,seed=seed,world=name,data=data,initial=initial,pipelines=records,shared_d_tests=dtests,
                pooled_bic_candidates=selection,evaluator_only=world,unique_observations=88,candidate_records=5,
                timing=dict(fit_seconds=fit_seconds,check_seconds=check_seconds))


def assert_controls(episodes,config):
    by={e['world']:e for e in episodes}
    if not math.isclose(by['quadratic']['initial']['check']['q'],by['noise']['initial']['check']['q'],abs_tol=1e-8,rel_tol=1e-10):
        raise ArithmeticError('initial shared control mismatch')


def rate(values):
    values=[x for x in values if x is not None]
    return dict(n=len(values),count=sum(values),rate=sum(values)/len(values) if values else None,wilson95=ed.wilson(sum(values),len(values)))


def summarize(episodes,config,control_equality_checked=False):
    cells,paired=[],[]
    for world in WORLDS:
        rows=[e for e in episodes if e['world']==world]
        if not rows:
            continue
        for pipeline in PIPELINES:
            records=[e['pipelines'][pipeline] for e in rows]
            metrics=[r['evaluator_only'] for r in records]
            recalls={}
            for method in ('exact','e'):
                total=sum(m['true_count'] or 0 for m in metrics)
                selected=sum(m['selected_true_count'] or 0 for m in metrics)
                confirmed=sum(m[method]['confirmed_true_count'] or 0 for m in metrics)
                known=any(m['true_count'] is not None for m in metrics)
                means={key:statistics.mean(values) if values else None for key in ('all_true_recall','selected_true_recall')
                       for values in [[m[method][key] for m in metrics if m[method][key] is not None]]}
                recalls[method]=dict(total_true_terms=total if known else None,selected_true_terms=selected if known else None,
                    confirmed_true_terms=confirmed if known else None,pooled_all_true_recall=confirmed/total if total else None,
                    pooled_selected_true_recall=confirmed/selected if selected else None,mean_ratios=means,
                    any_false=rate([None if m[method]['false_count'] is None else m[method]['false_count']>0 for m in metrics]))
            cells.append(dict(world=world,pipeline=pipeline,n=len(rows),initial_rejection=rate([e['initial']['check']['rejected'] for e in rows]),
                final_rejection=rate([r['check']['whole']['rejected'] for r in records]),
                raw_any_false=rate([None if m['raw_false_count'] is None else m['raw_false_count']>0 for m in metrics]),
                exact_support=rate([m['exact_support'] for m in metrics]),recalls=recalls,
                means=dict(d_mse=statistics.mean(r['check']['d_mse'] for r in records),
                           **{key:statistics.mean(m[key] for m in metrics) for key in ('inner_mse','outer_shell_mse')})))
        for comparator in PIPELINES[1:]:
            for metric in ('d_mse','inner_mse','outer_shell_mse'):
                def value(e,p):
                    record=e['pipelines'][p]
                    return record['check'][metric] if metric=='d_mse' else record['evaluator_only'][metric]
                differences=[dict(seed=e['seed'],difference=value(e,'revise_once')-value(e,comparator)) for e in rows]
                paired.append(dict(world=world,comparator=comparator,metric=metric,**ed.paired_stats(differences,config['normal_interval_z'])))
    checks=[e['initial'] for e in episodes]+[r['check'] for e in episodes for r in e['pipelines'].values()]
    return dict(completed_keys=[[e['seed'],e['world']] for e in episodes],cells=cells,paired=paired,
        control_equality_checked=control_equality_checked,
        budgets_valid=all([len(e['data'][k]) for k in ('a','c','b','d')]==[24,16,24,24] and e['unique_observations']==88 and len(e['pipelines'])==5 for e in episodes),
        immutable=all(c['candidate_sha256_before']==c['candidate_sha256_after'] and c['predictions_sha256_before']==c['predictions_sha256_after'] for c in checks))


def decision(summary,config,complete):
    expected={(s,w) for s in config['seeds'] for w in WORLDS}
    keys=[tuple(k) for k in summary['completed_keys']]
    hard=bool(complete and len(keys)==len(expected) and set(keys)==expected and summary['budgets_valid'] and summary['immutable'] and summary['control_equality_checked'])
    cells={(c['world'],c['pipeline']):c for c in summary['cells']}
    guards={}
    for world in ('medium_x','strong_x','quadratic','noise'):
        if all((world,p) in cells for p in PIPELINES):
            revision=cells[world,'revise_once']['means']['outer_shell_mse']
            never=cells[world,'never_revise']['means']['outer_shell_mse']
            if world in ('medium_x','strong_x'):
                guards[world]=revision<=.8*never and revision<=cells[world,'always_large']['means']['outer_shell_mse'] and revision<=cells[world,'always_large_pooled']['means']['outer_shell_mse']
            else:
                guards[world]=revision<=1.1*never
    warnings=[w for w in ('quadratic','noise') if (w,'revise_once') in cells and cells[w,'revise_once']['initial_rejection']['count']>6]
    return dict(complete=hard,hard_integration_pass=hard,utility_screen_pass=bool(hard and len(guards)==4 and all(guards.values())),
                utility_conditions=guards,false_revision_warning_worlds=warnings,limitation='one supplied-grammar extension; no novelty, operator invention or observations saved')


def fixed_config():
    return dict(schema_version=1,seeds=list(range(1200,1260)),smoke_seeds=[1190],fixture_seeds=[7,11],worlds=list(WORLDS),pipelines=list(PIPELINES),
        law_offset=9100001,a_input_offset=13100001,a_noise_offset=13200003,c_input_offset=13300007,c_noise_offset=13400009,
        b_input_offset=13500011,b_noise_offset=13600013,d_input_offset=13700017,d_noise_offset=13800019,
        sigma=.05,alpha=.025,exact_alpha=.05/8,log_e_threshold=math.log(160),rank_tolerance=1e-10,tie_tolerance=1e-12,
        features=list(TERMS),candidate_supports=SUPPORTS,a_sites=24,c_sites=16,b_sites=24,d_sites=24,a_radius=1,other_radius=2,
        cubic_coefficients=[.01,.05,.3],exponential_scale=.3,unique_observations=88,control_absolute_tolerance=1e-8,control_relative_tolerance=1e-10,
        target_improvement_ratio=.8,control_max_ratio=1.1,false_revision_warning_count=6,normal_interval_z=1.959963984540054,
        timeout_seconds=120,external_timeout_seconds=150,max_output_bytes=50000000,smoke_safety_factor=1.5,
        smoke_projection_limit_seconds=60,smoke_projection_limit_bytes=40000000,loop_order='seed,world,pipeline')


def validate_config(config):
    if config!=fixed_config():
        raise ValueError('fixed protocol parameters differ')
    stream_keys(config)


def output_scope(output):
    output, runs = Path(output).resolve(), (ROOT/'results/runs').resolve()
    if ROOT not in runs.parents or output.parent != runs or not output.name.startswith('equation_revision_'):
        raise ValueError('use fresh results/runs/equation_revision_<label>')
    if output.exists():
        raise FileExistsError('output exists')
    return output


def source_hashes():
    paths = [Path(__file__).resolve(), ROOT/'tests/test_equation_revision.py',
             ROOT/'experiments/equation_revision_v0.md', ROOT/'artificial_scientist/run.py', ROOT/'artificial_scientist/equation_discovery.py', ROOT/'artificial_scientist/equation_domain.py']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def verify_smoke(path, config_hash, sources, config):
    path = Path(path).resolve()
    if ROOT not in path.parents:
        raise ValueError('smoke outside repository')
    meta = json.loads((path/'metadata.json').read_text())
    if (meta.get('status') != 'completed' or meta.get('mode') != 'smoke' or meta.get('completed_episodes') != 8
            or not meta.get('sources_unchanged') or meta.get('source_sha256') != sources or meta.get('config_sha256') != config_hash):
        raise ValueError('smoke provenance/completion mismatch')
    required = {'config.json', 'episodes.jsonl', 'summary.json', 'decision.json'}
    if set(meta.get('artifact_sha256', {})) != required:
        raise ValueError('smoke artifact manifest incomplete')
    for name, digest in meta['artifact_sha256'].items():
        if Path(name).name != name or hashlib.sha256((path/name).read_bytes()).hexdigest() != digest:
            raise ValueError('smoke artifact mismatch')
    size = sum(p.stat().st_size for p in path.iterdir() if p.is_file())
    elapsed = meta['elapsed_seconds']
    if size != meta['artifact_bytes'] or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed <= 0:
        raise ValueError('invalid smoke size/time')
    factor = config['smoke_safety_factor']*480/8
    projected_time, projected_bytes = factor*elapsed, factor*size
    if projected_time > config['smoke_projection_limit_seconds'] or projected_bytes > config['smoke_projection_limit_bytes']:
        raise RuntimeError('resource no-go: smoke exceeds fixed time/disk projection')
    return dict(path=str(path.relative_to(ROOT)), projected_full_seconds=projected_time,
                projected_full_bytes=projected_bytes, metadata_sha256=hashlib.sha256((path/'metadata.json').read_bytes()).hexdigest())


def run(config_path, output, smoke=False, smoke_evidence=None):
    config_path = Path(config_path).resolve()
    if ROOT not in config_path.parents:
        raise ValueError('config outside repository')
    raw = config_path.read_bytes()
    config = json.loads(raw)
    validate_config(config)
    output = output_scope(output)
    sources, config_hash = source_hashes(), hashlib.sha256(raw).hexdigest()
    if not smoke and smoke_evidence is None:
        raise ValueError('full run requires --smoke-evidence')
    evidence = None if smoke else verify_smoke(smoke_evidence, config_hash, sources, config)
    start = time.perf_counter()
    meta = dict(git_info(ROOT), status='running', mode='smoke' if smoke else 'full', source_sha256=sources,
        config_sha256=config_hash, smoke_evidence=evidence, python=platform.python_version(), platform=platform.platform(),
        seeds=config['smoke_seeds'] if smoke else config['seeds'], external_timeout_seconds=config['external_timeout_seconds'], schema_version=1)
    if not smoke and (meta.get('dirty') is not False or not meta.get('revision')):
        raise RuntimeError('full run requires a clean committed repository')
    output.mkdir(parents=True, exist_ok=False)
    def write(name, data):
        text = json.dumps(data, indent=2, allow_nan=False)+'\n'
        other = sum(p.stat().st_size for p in output.iterdir() if p.is_file() and p.name != name)
        if other+len(text.encode()) > config['max_output_bytes']:
            raise RuntimeError('output cap reached')
        (output/name).write_text(text)
    write('config.json', config)
    write('metadata.json', meta)
    episodes, error = [], None
    verified_control_seeds = []
    try:
        with (output/'episodes.jsonl').open('w') as handle:
            for seed in meta['seeds']:
                worlds = world_catalog(seed)
                shared = streams(seed, config)
                seed_episodes = []
                for name in WORLDS:
                    if time.perf_counter()-start > config['timeout_seconds']:
                        raise TimeoutError('internal deadline reached')
                    episode = episode_record(seed, name, worlds[name], shared, config)
                    seed_episodes.append(episode)
                    text = json.dumps(episode, separators=(',', ':'), allow_nan=False)+'\n'
                    if sum(p.stat().st_size for p in output.iterdir() if p.is_file())+len(text.encode()) > config['max_output_bytes']-2000000:
                        raise RuntimeError('output cap reserve reached')
                    handle.write(text)
                    handle.flush()
                    episodes.append(episode)
                assert_controls(seed_episodes, config)
                verified_control_seeds.append(seed)
        meta['status'] = 'completed'
    except Exception as exc:
        error = exc
        meta.update(status='failed_partial', error=type(exc).__name__+': '+str(exc))
    finally:
        meta['sources_unchanged'] = sources == source_hashes() and hashlib.sha256(config_path.read_bytes()).hexdigest() == config_hash
        if not meta['sources_unchanged']:
            meta['status'] = 'invalid_source_changed'
        expected = 8 if smoke else 480
        if len(episodes) != expected and meta['status'] == 'completed':
            meta['status'] = 'incomplete'
        controls_checked = bool(episodes and len(episodes) == 8*len(verified_control_seeds))
        meta['verified_control_seeds'] = verified_control_seeds
        summary = summarize(episodes, config, controls_checked)
        result = decision(summary, config, meta['status'] == 'completed' and not smoke)
        write('summary.json', summary)
        write('decision.json', result)
        meta.update(completed_episodes=len(episodes), expected_episodes=expected, completed_observations=len(episodes)*88, completed_candidate_records=len(episodes)*5,
                    elapsed_seconds=time.perf_counter()-start)
        meta['artifact_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()
                                  if p.is_file() and p.name != 'metadata.json'}
        other_bytes = sum(p.stat().st_size for p in output.iterdir() if p.is_file() and p.name != 'metadata.json')
        meta['artifact_bytes'] = 0
        for _ in range(20):
            if smoke:
                factor = config['smoke_safety_factor']*480/8
                meta.update(projected_full_seconds=factor*meta['elapsed_seconds'], projected_full_bytes=factor*meta['artifact_bytes'])
                meta['resource_go'] = (meta['status'] == 'completed' and meta['projected_full_seconds'] <= config['smoke_projection_limit_seconds']
                                       and meta['projected_full_bytes'] <= config['smoke_projection_limit_bytes'])
            size = other_bytes+len((json.dumps(meta, indent=2, allow_nan=False)+'\n').encode())
            if size == meta['artifact_bytes']:
                break
            meta['artifact_bytes'] = size
        else:
            raise RuntimeError('metadata byte count did not stabilize')
        write('metadata.json', meta)
    if error is not None:
        raise error
    if meta['status'] != 'completed':
        raise RuntimeError('run incomplete or invalid; see preserved records')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('experiments/equation_revision_v0.json'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--smoke-evidence', type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output, args.smoke, args.smoke_evidence), indent=2))
