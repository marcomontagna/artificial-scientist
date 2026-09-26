"""Bounded best-subset equation fitting in a supplied six-monomial grammar."""
import argparse
import hashlib
import itertools
import json
import math
import platform
import random
import statistics
import time
from pathlib import Path
from .run import git_info

ROOT = Path(__file__).resolve().parents[1]
METHODS = ('constant', 'linear', 'dense', 'sparse')
WORLDS = ('affine', 'sparse_quadratic', 'sine', 'exponential', 'noise_only')
TERMS = ('1', 'x', 'u', 'x*x', 'x*u', 'u*u')


def basis(x, u):
    return (1., x, u, x*x, x*u, u*u)


def supports(max_terms=3):
    return [s for k in range(max_terms+1) for s in itertools.combinations(range(6), k)]


def predict(coefficients, x, u):
    return math.fsum(c*v for c, v in zip(coefficients, basis(x, u)))


def formula(coefficients, support):
    return ' + '.join(f'({coefficients[j]:.17g})*{TERMS[j]}' for j in support) or '0'


def least_squares(design, outcomes, support, rank_tolerance=1e-10):
    """Twice-orthogonalized MGS; return six coefficients, or fail on rank loss."""
    n, k = len(outcomes), len(support)
    if not n or len(design) != n or any(len(row) != 6 for row in design):
        raise ValueError('nonempty aligned six-column design required')
    if len(set(support)) != k or any(j not in range(6) for j in support):
        raise ValueError('invalid support')
    if not all(math.isfinite(v) for row in design for v in row) or not all(math.isfinite(y) for y in outcomes):
        raise ArithmeticError('nonfinite fit input')
    q, r = [], [[0.]*k for _ in range(k)]
    for column, j in enumerate(support):
        vector = [row[j] for row in design]
        original = math.sqrt(math.fsum(v*v for v in vector))
        for _ in range(2):
            for i, unit in enumerate(q):
                projection = math.fsum(a*b for a, b in zip(unit, vector))
                r[i][column] += projection
                vector = [a-projection*b for a, b in zip(vector, unit)]
        norm = math.sqrt(math.fsum(v*v for v in vector))
        if original == 0 or norm <= rank_tolerance*original:
            raise ArithmeticError('rank-deficient support')
        r[column][column] = norm
        q.append([v/norm for v in vector])
    rhs = [math.fsum(a*b for a, b in zip(unit, outcomes)) for unit in q]
    beta = [0.]*k
    for i in reversed(range(k)):
        beta[i] = (rhs[i]-math.fsum(r[i][j]*beta[j] for j in range(i+1, k)))/r[i][i]
    coefficients = [0.]*6
    for j, value in zip(support, beta):
        coefficients[j] = value
    sse = math.fsum((y-math.fsum(c*v for c, v in zip(coefficients, row)))**2 for y, row in zip(outcomes, design))
    if not all(math.isfinite(v) for v in coefficients+[sse]):
        raise ArithmeticError('nonfinite fit result')
    return dict(support=list(support), coefficients=coefficients, sse=sse,
                complexity=k, formula=formula(coefficients, support))


def select_model(models, tolerance=1e-12):
    minimum = min(model['score'] for model in models)
    return min((model for model in models if model['score']-minimum <= tolerance),
               key=lambda model: (model['complexity'], model['support']))


def fit_committee(observations, sigma=.05, max_terms=3, rank_tolerance=1e-10, tie_tolerance=1e-12):
    """Only observed (x,u,y) triples and supplied numeric settings enter fitting."""
    if sigma <= 0 or not math.isfinite(sigma):
        raise ValueError('positive finite noise scale required')
    design = [basis(x, u) for x, u, _ in observations]
    outcomes = [y for _, _, y in observations]
    models, skipped = [], []
    for support in supports(max_terms):
        try:
            model = least_squares(design, outcomes, support, rank_tolerance)
        except ArithmeticError as exc:
            if str(exc) != 'rank-deficient support':
                raise
            skipped.append(list(support))
            continue
        model['score'] = model['sse']/sigma**2 + model['complexity']*math.log(len(outcomes))
        models.append(model)
    minimum = min(m['score'] for m in models)
    weights = [math.exp(-.5*(m['score']-minimum)) for m in models]
    total = math.fsum(weights)
    for model, weight in zip(models, weights):
        model['weight'] = weight/total
    selected = dict(select_model(models, tie_tolerance))
    return dict(selected=selected, models=models, skipped_supports=skipped,
                top3=sorted(models, key=lambda m: (-m['weight'], m['complexity'], m['support']))[:3],
                maximum_heuristic_weight=max(m['weight'] for m in models))


def fit_methods(observations, config):
    design = [basis(x, u) for x, u, _ in observations]
    outcomes = [y for _, _, y in observations]
    fitted = {}
    for method, support in [('constant', (0,)), ('linear', (0, 1, 2)), ('dense', tuple(range(6)))]:
        start = time.perf_counter()
        fitted[method] = least_squares(design, outcomes, support, config['rank_tolerance'])
        fitted[method]['fit_seconds'] = time.perf_counter()-start
    start = time.perf_counter()
    committee = fit_committee(observations, config['sigma'], config['max_terms'], config['rank_tolerance'], config['tie_tolerance'])
    fitted['sparse'] = dict(committee['selected'], committee=committee, fit_seconds=time.perf_counter()-start)
    return fitted


def world_catalog(seed, config):
    rng = random.Random(config['law_seed_offset']+seed)
    def polynomial(support):
        coefficients = [0.]*6
        for j in support:
            coefficients[j] = rng.choice([-1, 1])*rng.uniform(*config['coefficient_magnitude'])
        return dict(kind='polynomial', support=list(support), coefficients=coefficients,
                    formula=formula(coefficients, support))
    affine = polynomial((0, 1, 2))
    size = rng.choice([1, 2, 3])
    choices = [s for s in itertools.combinations(range(6), size) if any(j >= 3 for j in s)]
    quadratic = polynomial(rng.choice(choices))
    return dict(affine=affine, sparse_quadratic=quadratic,
                sine=dict(kind='sine', formula='sin(pi*x)+0.5*u', support=None, coefficients=None),
                exponential=dict(kind='exponential', formula='exp(x)+0.5*u', support=None, coefficients=None),
                noise_only=dict(kind='polynomial', formula='0', support=[], coefficients=[0.]*6))


def true_mean(world, x, u):
    if world['kind'] == 'polynomial':
        return predict(world['coefficients'], x, u)
    if world['kind'] == 'sine':
        return math.sin(math.pi*x)+.5*u
    if world['kind'] == 'exponential':
        return math.exp(x)+.5*u
    raise ValueError('unknown world')


def shared_streams(seed, config):
    inputs = random.Random(config['input_seed_offset']+seed)
    noise = random.Random(config['train_noise_seed_offset']+seed)
    audit_inputs = random.Random(config['audit_input_seed_offset']+seed)
    audit_noise = random.Random(config['audit_noise_seed_offset']+seed)
    sites = [(inputs.uniform(-1, 1), inputs.uniform(-1, 1)) for _ in range(config['train_sites'])]
    training = [(x, u, noise.gauss(0, config['sigma'])) for x, u in sites for _ in range(config['replicates'])]
    audit = [(audit_inputs.uniform(-1, 1), audit_inputs.uniform(-1, 1), audit_noise.gauss(0, config['sigma']))
             for _ in range(config['audit_sites'])]
    return dict(training=training, audit=audit)


def query_grids():
    inside = [(-9+2*i)/10 for i in range(10)]
    outside = [i/2 for i in range(-4, 5)]
    return dict(interpolation=list(itertools.product(inside, repeat=2)),
                extrapolation=[(x, u) for x, u in itertools.product(outside, repeat=2) if max(abs(x), abs(u)) > 1])


def evaluate_queries(coefficients, world, points):
    return statistics.mean((predict(coefficients, x, u)-true_mean(world, x, u))**2 for x, u in points)


def audit_predictions(predictions, outcomes, sigma):
    if not predictions or len(predictions) != len(outcomes):
        raise ValueError('aligned nonempty audit required')
    mse = statistics.mean((p-y)**2 for p, y in zip(predictions, outcomes))
    return dict(audit_mse=mse, audit_rejected=mse > 4*sigma**2)


def episode_record(seed, name, world, streams, config):
    training = [(x, u, true_mean(world, x, u)+noise) for x, u, noise in streams['training']]
    # All fits finish before audit outcomes are constructed or inspected.
    methods = fit_methods(training, {key: config[key] for key in ('sigma', 'max_terms', 'rank_tolerance', 'tie_tolerance')})
    audit_points = [(x, u) for x, u, _ in streams['audit']]
    predictions = {name: [predict(model['coefficients'], x, u) for x, u in audit_points] for name, model in methods.items()}
    audit = [(x, u, true_mean(world, x, u)+noise) for x, u, noise in streams['audit']]
    grids = query_grids()
    for method, model in methods.items():
        metrics = {key+'_mse': evaluate_queries(model['coefficients'], world, points) for key, points in grids.items()}
        metrics.update(audit_predictions(predictions[method], [y for _, _, y in audit], config['sigma']))
        metrics.update(exact_support=None, coefficient_rmse=None, false_inclusion=None)
        if world['support'] is not None:
            metrics.update(exact_support=model['support'] == world['support'],
                           coefficient_rmse=math.sqrt(statistics.mean((a-b)**2 for a, b in zip(model['coefficients'], world['coefficients']))),
                           false_inclusion=bool(set(model['support'])-set(world['support'])))
        model.update(metrics=metrics, audit_predictions=predictions[method])
    return dict(schema_version=1, seed=seed, world=name, evaluator_only=world,
                training=training, audit=audit, methods=methods)


def wilson(successes, n, z=1.959963984540054):
    if not n:
        return None
    p = successes/n
    denominator = 1+z*z/n
    center = (p+z*z/(2*n))/denominator
    radius = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denominator
    return [center-radius, center+radius]


def paired_stats(rows, z):
    values = [row['difference'] for row in rows]
    mean = statistics.mean(values)
    se = statistics.stdev(values)/math.sqrt(len(values)) if len(values) > 1 else None
    return dict(mean_difference=mean, seed_se=se, normal95=None if se is None else [mean-z*se, mean+z*se], per_seed=rows)


def summarize(episodes, config):
    cells, paired = [], []
    for world in WORLDS:
        rows = [e for e in episodes if e['world'] == world]
        if not rows:
            continue
        for method in METHODS:
            models = [e['methods'][method] for e in rows]
            metrics = [m['metrics'] for m in models]
            proportions = {}
            for key in ('exact_support', 'false_inclusion', 'audit_rejected'):
                values = [m[key] for m in metrics if m[key] is not None]
                proportions[key] = dict(count=sum(values), n=len(values), rate=sum(values)/len(values),
                                         wilson95=wilson(sum(values), len(values), config['normal_interval_z'])) if values else None
            nonzero = sum(m['complexity'] > 0 for m in models)
            proportions['nonzero_selection'] = dict(count=nonzero, n=len(models), rate=nonzero/len(models),
                                                      wilson95=wilson(nonzero, len(models), config['normal_interval_z']))
            cells.append(dict(world=world, method=method, n=len(rows), proportions=proportions,
                means={key: statistics.mean(m[key] for m in metrics if m[key] is not None)
                       for key in ('interpolation_mse', 'extrapolation_mse', 'audit_mse', 'coefficient_rmse')
                       if any(m[key] is not None for m in metrics)},
                mean_complexity=statistics.mean(m['complexity'] for m in models),
                total_fit_seconds=sum(m['fit_seconds'] for m in models)))
        for comparator in ('linear', 'dense'):
            for metric in ('interpolation_mse', 'extrapolation_mse'):
                differences = [dict(seed=e['seed'], difference=e['methods']['sparse']['metrics'][metric]-e['methods'][comparator]['metrics'][metric]) for e in rows]
                paired.append(dict(world=world, comparator=comparator, metric=metric,
                                   **paired_stats(differences, config['normal_interval_z'])))
    return dict(completed_keys=[[e['seed'], e['world']] for e in episodes], cells=cells, paired=paired,
                interval_scope='descriptive variation in declared development seeds, not general law discovery')


def decision(summary, config, complete):
    expected = {(seed, world) for seed in config['seeds'] for world in WORLDS}
    observed = [tuple(key) for key in summary['completed_keys']]
    complete = bool(complete and len(observed) == len(expected) and set(observed) == expected)
    cells = {c['world']: c for c in summary['cells'] if c['method'] == 'sparse'}
    def count(world, key):
        return cells[world]['proportions'][key]['count']
    recovery, adequacy = {}, {}
    if all(world in cells for world in WORLDS):
        recovery = {world+'_support': count(world, 'exact_support') >= config['minimum_support_recoveries'] for world in ('affine', 'sparse_quadratic')}
        recovery.update(sparse_false_inclusion=count('sparse_quadratic', 'false_inclusion') <= config['maximum_false_inclusions'],
                        noise_nonzero=count('noise_only', 'nonzero_selection') <= config['maximum_noise_nonzero'])
        for world in WORLDS:
            rejects = count(world, 'audit_rejected')
            adequacy[world] = (rejects <= config['maximum_false_rejections'] if world in ('affine', 'sparse_quadratic', 'noise_only')
                               else cells[world]['n']-rejects <= config['maximum_missed_rejections'])
    return dict(complete=complete, recovery_pass=bool(complete and len(recovery) == 4 and all(recovery.values())),
                adequacy_pass=bool(complete and len(adequacy) == 5 and all(adequacy.values())),
                recovery_conditions=recovery, adequacy_conditions=adequacy,
                limitation='supplied grammar, noise scale and observation domain; heuristic weights; no novelty or true-law claim')


def fixed_config():
    return dict(schema_version=1, seeds=list(range(600, 620)), smoke_seeds=[590], worlds=list(WORLDS), methods=list(METHODS),
        basis=list(TERMS), max_terms=3, sigma=.05, train_sites=12, replicates=2, audit_sites=16,
        coefficient_magnitude=[.5, 1.5], sparse_support_sizes=[1, 2, 3],
        law_seed_offset=9100001, input_seed_offset=9200003, train_noise_seed_offset=9300007,
        audit_input_seed_offset=9400009, audit_noise_seed_offset=9500011,
        rank_tolerance=1e-10, tie_tolerance=1e-12, normal_interval_z=1.959963984540054,
        minimum_support_recoveries=14, maximum_false_inclusions=6, maximum_noise_nonzero=8,
        maximum_false_rejections=2, maximum_missed_rejections=4,
        timeout_seconds=120, external_timeout_seconds=150, max_output_bytes=50000000,
        smoke_safety_factor=1.5, smoke_projection_limit_seconds=60, smoke_projection_limit_bytes=40000000,
        loop_order='seed,world', audit_threshold_multiplier=4,
        interpolation_axis=[(-9+2*i)/10 for i in range(10)], extrapolation_axis=[i/2 for i in range(-4, 5)],
        outside_formulas={'sine':'sin(pi*x)+0.5*u','exponential':'exp(x)+0.5*u'},
        score='SSE/sigma^2 + k*log(n)', heuristic_weight='exp(-0.5*(score-min_score))/sum',
        support_sampling='uniform size then uniform lexicographic subset containing a quadratic term',
        coefficient_sampling='ordered support: choice([-1,1]) then uniform(0.5,1.5)')


def validate_config(config):
    if config != fixed_config():
        raise ValueError('fixed protocol parameters differ')


def output_scope(output):
    output, runs = Path(output).resolve(), (ROOT/'results/runs').resolve()
    if ROOT not in runs.parents or output.parent != runs or not output.name.startswith('equation_discovery_'):
        raise ValueError('use fresh results/runs/equation_discovery_<label>')
    if output.exists():
        raise FileExistsError('output exists')
    return output


def source_hashes():
    paths = [Path(__file__).resolve(), ROOT/'tests/test_equation_discovery.py',
             ROOT/'experiments/equation_discovery_v0.md', ROOT/'artificial_scientist/run.py']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def verify_smoke(path, config_hash, sources, config):
    path = Path(path).resolve()
    if ROOT not in path.parents:
        raise ValueError('smoke outside repository')
    meta = json.loads((path/'metadata.json').read_text())
    if (meta.get('status') != 'completed' or meta.get('mode') != 'smoke' or meta.get('completed_episodes') != 5
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
    factor = config['smoke_safety_factor']*100/5
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
    try:
        with (output/'episodes.jsonl').open('w') as handle:
            for seed in meta['seeds']:
                worlds, streams = world_catalog(seed, config), shared_streams(seed, config)
                for name in WORLDS:
                    if time.perf_counter()-start > config['timeout_seconds']:
                        raise TimeoutError('internal deadline reached')
                    episode = episode_record(seed, name, worlds[name], streams, config)
                    text = json.dumps(episode, separators=(',', ':'), allow_nan=False)+'\n'
                    if sum(p.stat().st_size for p in output.iterdir() if p.is_file())+len(text.encode()) > config['max_output_bytes']-2000000:
                        raise RuntimeError('output cap reserve reached')
                    handle.write(text)
                    handle.flush()
                    episodes.append(episode)
        meta['status'] = 'completed'
    except Exception as exc:
        error = exc
        meta.update(status='failed_partial', error=type(exc).__name__+': '+str(exc))
    finally:
        meta['sources_unchanged'] = sources == source_hashes() and hashlib.sha256(config_path.read_bytes()).hexdigest() == config_hash
        if not meta['sources_unchanged']:
            meta['status'] = 'invalid_source_changed'
        expected = 5 if smoke else 100
        if len(episodes) != expected and meta['status'] == 'completed':
            meta['status'] = 'incomplete'
        summary = summarize(episodes, config)
        result = decision(summary, config, meta['status'] == 'completed' and not smoke)
        write('summary.json', summary)
        write('decision.json', result)
        meta.update(completed_episodes=len(episodes), expected_episodes=expected, completed_observations=len(episodes)*40,
                    elapsed_seconds=time.perf_counter()-start)
        meta['artifact_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()
                                  if p.is_file() and p.name != 'metadata.json'}
        other_bytes = sum(p.stat().st_size for p in output.iterdir() if p.is_file() and p.name != 'metadata.json')
        meta['artifact_bytes'] = 0
        for _ in range(20):
            if smoke:
                factor = config['smoke_safety_factor']*100/5
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
    parser.add_argument('--config', type=Path, default=Path('experiments/equation_discovery_v0.json'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--smoke-evidence', type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output, args.smoke, args.smoke_evidence), indent=2))
