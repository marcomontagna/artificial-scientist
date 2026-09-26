"""One frozen equation receives independent term evidence and a whole-form check."""
import argparse
import copy
import hashlib
import json
import math
import platform
import random
import statistics
import time
from pathlib import Path
from . import equation_discovery as ed
from . import equation_confirmation as ec
from . import equation_domain as domain
from .run import git_info
ROOT = Path(__file__).resolve().parents[1]
WORLDS = ('strong_affine','strong_quadratic','weak_affine','weak_quadratic','noise_only','exponential','cubic','sine')
PIPELINES = ('selected_refit','fixed_full','pooled_bic')
CONTROLS = WORLDS[:5]


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def stream_keys(config):
    seeds = config['seeds']+config['smoke_seeds']+config['fixture_seeds']
    offsets = [config['law_seed_offset']]+[config[k] for k in ('a_input_offset','a_noise_offset','b_input_offset','b_noise_offset','c_input_offset','c_noise_offset')]
    keys = [offset+seed for offset in offsets for seed in seeds]
    if len(set(keys)) != len(keys):
        raise ValueError('cross-role/seed RNG collision')
    return keys


def streams(seed, config):
    result = {}
    for label, sites, repeats, radius in [('a',12,2,1),('b',12,2,1),('c',16,1,2)]:
        inputs = random.Random(config[label+'_input_offset']+seed)
        noise = random.Random(config[label+'_noise_offset']+seed)
        points = [(inputs.uniform(-radius,radius),inputs.uniform(-radius,radius)) for _ in range(sites)]
        result[label] = [(x,u,noise.gauss(0,config['sigma'])) for x,u in points for _ in range(repeats)]
    return result


def world_catalog(seed):
    old = ed.world_catalog(seed, ed.fixed_config())
    result = dict(strong_affine=old['affine'],strong_quadratic=old['sparse_quadratic'],noise_only=old['noise_only'],
                  exponential=old['exponential'],sine=old['sine'],cubic=dict(kind='cubic',formula='0.3*x^3+0.5*u',support=None,coefficients=None))
    for name in ('affine','quadratic'):
        strong = result['strong_'+name]
        weak = copy.deepcopy(strong)
        weak['coefficients'] = [.1*x for x in strong['coefficients']]
        weak['formula'] = ed.formula(weak['coefficients'], weak['support'])
        result['weak_'+name] = weak
    return result


def selected_r(design, support, tolerance=1e-10):
    q, r = [], [[0.]*len(support) for _ in support]
    for column,j in enumerate(support):
        vector = [row[j] for row in design]
        original = math.sqrt(math.fsum(v*v for v in vector))
        for _ in range(2):
            for i,unit in enumerate(q):
                projection = math.fsum(a*b for a,b in zip(unit,vector))
                r[i][column] += projection
                vector = [a-projection*b for a,b in zip(vector,unit)]
        norm = math.sqrt(math.fsum(v*v for v in vector))
        if original == 0 or norm <= tolerance*original or not math.isfinite(norm):
            raise ArithmeticError('rank-deficient fitted design')
        r[column][column] = norm
        q.append([v/norm for v in vector])
    return r


def fit_candidates(a, b, sigma=.05):
    """Observed A/B only; C and hidden metadata are absent from this API."""
    selected = ed.fit_committee(a, sigma)
    pooled = ed.fit_committee(a+b, sigma)
    candidates = {}
    for pipeline, observations, support, selection in [
            ('selected_refit', b, selected['selected']['support'], selected),
            ('fixed_full', a+b, list(range(6)), None),
            ('pooled_bic', a+b, pooled['selected']['support'], pooled)]:
        fit = ed.least_squares([ed.basis(x,u) for x,u,_ in observations],[y for _,_,y in observations],support)
        candidates[pipeline] = dict(equation=fit, fitted_data='B' if pipeline=='selected_refit' else 'A+B',
            fit_observations=len(observations), fitted_design=[ed.basis(x,u) for x,u,_ in observations],
            selection=None if selection is None else dict(chosen=selection['selected'],top3=selection['top3']))
    return candidates


def check_candidate(candidate, c, pipeline, sigma=.05):
    before = fingerprint(candidate)
    equation = candidate['equation']
    predictions = [ed.predict(equation['coefficients'],x,u) for x,u,_ in c]
    predictions_before = fingerprint(predictions)
    evidence = ec.term_evidence(equation,c,sigma)
    confirmed = [j for j in equation['support'] if evidence['terms'][j]['log_e'] >= math.log(120)]
    unsupported = [j for j in equation['support'] if j not in confirmed]
    q = log_p = rejection = qualified = None
    status = 'unavailable_post_selection'
    if pipeline != 'pooled_bic':
        support = equation['support']
        r = selected_r(candidate['fitted_design'],support)
        audit_design = [[ed.basis(x,u)[j] for j in support] for x,u,_ in c]
        covariance = domain.predictive_covariance(r,audit_design,sigma)
        lower = domain.cholesky(covariance)
        q = domain.quadratic_form(lower,[y-p for (_,_,y),p in zip(c,predictions)])
        log_p = domain.log_survival(q)
        rejection = log_p <= math.log(.05)
        qualified = bool(support and not unsupported and not rejection)
        status = 'rejected' if rejection else 'not_rejected'
    after = fingerprint(candidate)
    predictions_after = fingerprint([ed.predict(equation['coefficients'],x,u) for x,u,_ in c])
    if before != after or predictions_before != predictions_after:
        raise ArithmeticError('candidate or predictions mutated by C check')
    return dict(confirmed_terms=confirmed,unsupported_terms=unsupported,term_evidence=evidence,
                adequacy=dict(status=status,q=q,log_p=log_p,p_value=None if log_p is None else math.exp(log_p),rejected=rejection),
                qualified_nonempty=qualified,predictions=predictions,c_mse=evidence['candidate_audit_sse']/len(c),
                candidate_sha256_before=before,candidate_sha256_after=after,
                predictions_sha256_before=predictions_before,predictions_sha256_after=predictions_after)


def evaluate(candidate, checks, world):
    support = set(candidate['equation']['support'])
    true = None if world['support'] is None else set(world['support'])
    confirmed = set(checks['confirmed_terms'])
    metrics = dict(raw_any_false=None,confirmed_any_false=None,exact_support=None,selection_recall=None,
        end_to_end_recall=None,confirmation_among_selected_true=None,true_term_count=None,confirmed_true_count=None,
        sufficient=False if true is None else true <= support,empty_support=not support)
    if true is not None:
        selected_true = true & support
        metrics.update(raw_any_false=bool(support-true),confirmed_any_false=bool(confirmed-true),exact_support=support==true,
            selection_recall=len(selected_true)/len(true) if true else None,
            end_to_end_recall=len(confirmed & true)/len(true) if true else None,
            confirmation_among_selected_true=len(confirmed & true)/len(selected_true) if selected_true else None,
            true_term_count=len(true),confirmed_true_count=len(confirmed & true))
    for label, points in ed.query_grids().items():
        metrics[label+'_mse'] = statistics.mean((ed.predict(candidate['equation']['coefficients'],x,u)-domain.truth(world,x,u))**2 for x,u in points)
    return metrics


def episode_record(seed, name, world, shared, config):
    data = {label:[(x,u,domain.truth(world,x,u)+noise) for x,u,noise in values] for label,values in shared.items()}
    candidates = fit_candidates(data['a'],data['b'],config['sigma'])
    records = {}
    for pipeline,candidate in candidates.items():
        checks = check_candidate(candidate,data['c'],pipeline,config['sigma'])
        metrics = evaluate(candidate,checks,world)
        records[pipeline] = dict(candidate=candidate,checks=checks,evaluator_only=metrics)
    return dict(schema_version=1,seed=seed,world=name,a=data['a'],b=data['b'],c=data['c'],
                pipelines=records,evaluator_only=world,unique_observations=64,candidate_records=3)


def assert_controls(episodes, config):
    by = {e['world']:e for e in episodes}
    values = [by[w]['pipelines']['fixed_full']['checks']['adequacy']['q'] for w in CONTROLS]
    if not all(math.isclose(values[0],x,rel_tol=1e-10,abs_tol=1e-8) for x in values[1:]):
        raise ArithmeticError('fixed-full shared controls disagree')


def rate(values):
    values = [v for v in values if v is not None]
    n = len(values)
    return dict(count=sum(values),n=n,rate=sum(values)/n if n else None,wilson95=ed.wilson(sum(values),n))


def summarize(episodes, config, control_equality_checked=False):
    cells,paired = [],[]
    for world in WORLDS:
        rows = [e for e in episodes if e['world']==world]
        if not rows:
            continue
        for pipeline in PIPELINES:
            records = [e['pipelines'][pipeline] for e in rows]
            metrics = [r['evaluator_only'] for r in records]
            checks = [r['checks'] for r in records]
            counts = {key:rate([m[key] for m in metrics]) for key in ('raw_any_false','confirmed_any_false','exact_support','empty_support')}
            counts.update(qualified_nonempty=rate([c['qualified_nonempty'] for c in checks]),
                          adequacy_rejected=rate([c['adequacy']['rejected'] for c in checks]))
            recalls = {key:statistics.mean(values) if values else None for key in
                       ('selection_recall','end_to_end_recall','confirmation_among_selected_true')
                       for values in [[m[key] for m in metrics if m[key] is not None]]}
            true_count = None if all(m['true_term_count'] is None for m in metrics) else sum(m['true_term_count'] or 0 for m in metrics)
            confirmed_count = None if true_count is None else sum(m['confirmed_true_count'] or 0 for m in metrics)
            cells.append(dict(world=world,pipeline=pipeline,n=len(rows),rates=counts,mean_recalls=recalls,
                end_to_end_term_recall=confirmed_count/true_count if true_count else None,
                confirmed_true_terms=confirmed_count,total_true_terms=true_count,
                sufficient=rate([c['adequacy']['rejected'] for c,m in zip(checks,metrics) if m['sufficient']]),
                insufficient=rate([c['adequacy']['rejected'] for c,m in zip(checks,metrics) if not m['sufficient']]),
                means=dict(c_mse=statistics.mean(c['c_mse'] for c in checks),
                           **{key:statistics.mean(m[key] for m in metrics) for key in ('interpolation_mse','extrapolation_mse')}),
                true_coefficient_range=None if rows[0]['evaluator_only']['coefficients'] is None else
                    [min((abs(c) for e in rows for c in e['evaluator_only']['coefficients'] if c),default=0.),
                     max((abs(c) for e in rows for c in e['evaluator_only']['coefficients'] if c),default=0.)]))
        for baseline in ('fixed_full','pooled_bic'):
            for metric in ('c_mse','interpolation_mse','extrapolation_mse','confirmed_any_false','raw_any_false','adequacy_rejected'):
                if metric=='adequacy_rejected' and baseline=='pooled_bic':
                    continue
                differences=[]
                for e in rows:
                    def value(p):
                        r=e['pipelines'][p]
                        return r['checks']['c_mse'] if metric=='c_mse' else r['checks']['adequacy']['rejected'] if metric=='adequacy_rejected' else r['evaluator_only'][metric]
                    left,right=value('selected_refit'),value(baseline)
                    if left is not None and right is not None:
                        differences.append(dict(seed=e['seed'],difference=left-right))
                if differences:
                    paired.append(dict(world=world,baseline=baseline,metric=metric,
                        interpretation='different-null descriptive contrast' if metric=='adequacy_rejected' else 'descriptive paired contrast',
                        **ed.paired_stats(differences,config['normal_interval_z'])))
    return dict(completed_keys=[[e['seed'],e['world']] for e in episodes],cells=cells,paired=paired,
        control_equality_checked=control_equality_checked,
        budgets_valid=all(len(e['a'])==24 and len(e['b'])==24 and len(e['c'])==16 and e['unique_observations']==64 and len(e['pipelines'])==3 for e in episodes),
        immutable=all(r['checks']['candidate_sha256_before']==r['checks']['candidate_sha256_after'] and
                      r['checks']['predictions_sha256_before']==r['checks']['predictions_sha256_after'] for e in episodes for r in e['pipelines'].values()))


def decision(summary,config,complete):
    expected={(s,w) for s in config['seeds'] for w in WORLDS}
    keys=[tuple(k) for k in summary['completed_keys']]
    hard=bool(complete and len(keys)==len(expected) and set(keys)==expected and summary['control_equality_checked'] and summary['budgets_valid'] and summary['immutable'])
    cells={(c['world'],c['pipeline']):c for c in summary['cells']}
    false_guards={w+'_'+p:cells[w,p]['rates']['confirmed_any_false']['count']<=6 for w in CONTROLS for p in PIPELINES if (w,p) in cells}
    recall={w:cells[w,'selected_refit']['end_to_end_term_recall']>=.8 for w in WORLDS[:2] if (w,'selected_refit') in cells}
    warnings=[w for w in CONTROLS if (w,'fixed_full') in cells and cells[w,'fixed_full']['sufficient']['count']>8]
    practical=bool(hard and len(false_guards)==15 and all(false_guards.values()) and len(recall)==2 and all(recall.values()) and not warnings)
    return dict(complete=hard,hard_integration_pass=hard,practical_screen_pass=practical,false_term_guards=false_guards,
                strong_recall_guards=recall,full_null_warning_worlds=warnings,limitation='known-method integration; no novelty or simultaneous calibration claim')


def fixed_config():
    return dict(schema_version=1,seeds=list(range(1100,1160)),smoke_seeds=[1090],fixture_seeds=[7,11],worlds=list(WORLDS),pipelines=list(PIPELINES),
        law_seed_offset=9100001,a_input_offset=12100001,a_noise_offset=12200003,b_input_offset=12300007,b_noise_offset=12400009,
        c_input_offset=12500013,c_noise_offset=12600017,sigma=.05,alpha=.05,term_log_threshold=math.log(120),
        rank_tolerance=1e-10,tie_tolerance=1e-12,max_terms=3,basis=list(ed.TERMS),weak_multiplier=.1,
        a_sites=12,b_sites=12,replicates=2,c_sites=16,c_radius=2,unique_observations=64,
        maximum_false_claim_datasets=6,maximum_full_null_rejections=8,minimum_strong_recall=.8,
        control_absolute_tolerance=1e-8,control_relative_tolerance=1e-10,normal_interval_z=1.959963984540054,
        timeout_seconds=120,external_timeout_seconds=150,max_output_bytes=50000000,
        smoke_safety_factor=1.5,smoke_projection_limit_seconds=60,smoke_projection_limit_bytes=40000000,loop_order='seed,world,pipeline')


def validate_config(config):
    if config!=fixed_config():
        raise ValueError('fixed protocol parameters differ')
    stream_keys(config)


def output_scope(output):
    output, runs = Path(output).resolve(), (ROOT/'results/runs').resolve()
    if ROOT not in runs.parents or output.parent != runs or not output.name.startswith('equation_pipeline_'):
        raise ValueError('use fresh results/runs/equation_pipeline_<label>')
    if output.exists():
        raise FileExistsError('output exists')
    return output


def source_hashes():
    paths = [Path(__file__).resolve(), ROOT/'tests/test_equation_pipeline.py',
             ROOT/'experiments/equation_pipeline_v0.md', ROOT/'artificial_scientist/run.py', ROOT/'artificial_scientist/equation_discovery.py', ROOT/'artificial_scientist/equation_domain.py', ROOT/'artificial_scientist/equation_confirmation.py']
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
        meta.update(completed_episodes=len(episodes), expected_episodes=expected, completed_observations=len(episodes)*64, completed_candidate_records=len(episodes)*3,
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
    parser.add_argument('--config', type=Path, default=Path('experiments/equation_pipeline_v0.json'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--smoke-evidence', type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output, args.smoke, args.smoke_evidence), indent=2))
