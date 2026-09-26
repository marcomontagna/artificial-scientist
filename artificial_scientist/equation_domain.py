"""Fixed-quadratic predictive checks on paired local and wider audit domains."""
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
from .run import git_info

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ('affine', 'sparse_quadratic', 'noise_only', 'exponential', 'cubic', 'sine')
ARMS = ('local', 'wide')
CONTROLS = WORLDS[:3]


def training_r(design, tolerance=1e-10):
    """Same twice-orthogonalized MGS and relative rank rule as the frozen fitter."""
    if not design or any(len(row) != 6 for row in design):
        raise ValueError('six-column nonempty design required')
    q, r = [], [[0.]*6 for _ in range(6)]
    for j in range(6):
        vector = [row[j] for row in design]
        original = math.sqrt(math.fsum(x*x for x in vector))
        for _ in range(2):
            for i, unit in enumerate(q):
                projection = math.fsum(a*b for a, b in zip(unit, vector))
                r[i][j] += projection
                vector = [a-projection*b for a, b in zip(vector, unit)]
        norm = math.sqrt(math.fsum(x*x for x in vector))
        if original == 0 or norm <= tolerance*original or not math.isfinite(norm):
            raise ArithmeticError('rank-deficient or invalid design')
        r[j][j] = norm
        q.append([x/norm for x in vector])
    return r


def solve_lower(matrix, vector):
    answer = []
    for i, value in enumerate(vector):
        answer.append((value-math.fsum(matrix[i][j]*answer[j] for j in range(i)))/matrix[i][i])
    if not all(math.isfinite(x) for x in answer):
        raise ArithmeticError('nonfinite triangular solve')
    return answer


def predictive_covariance(r, audit_design, sigma):
    transpose = [list(row) for row in zip(*r)]
    z = [solve_lower(transpose, row) for row in audit_design]
    return [[sigma**2*((1. if i == j else 0.)+math.fsum(a*b for a, b in zip(zi, zj)))
             for j, zj in enumerate(z)] for i, zi in enumerate(z)]


def cholesky(matrix):
    n = len(matrix)
    lower = [[0.]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            value = matrix[i][j]-math.fsum(lower[i][k]*lower[j][k] for k in range(j))
            if i == j:
                if not math.isfinite(value) or value <= 0:
                    raise ArithmeticError('covariance is not positive definite')
                lower[i][j] = math.sqrt(value)
            else:
                lower[i][j] = value/lower[j][j]
    return lower


def quadratic_form(lower, residual):
    white = solve_lower(lower, residual)
    value = math.fsum(x*x for x in white)
    if not math.isfinite(value) or value < -1e-10:
        raise ArithmeticError('invalid quadratic form')
    return max(0., value)


def log_survival(q):
    if not math.isfinite(q) or q < -1e-10:
        raise ArithmeticError('invalid chi-square statistic')
    if q <= 0:
        return 0.
    z = q/2
    logs = [k*math.log(z)-math.lgamma(k+1) for k in range(8)]
    maximum = max(logs)
    return min(0., -z+maximum+math.log(math.fsum(math.exp(v-maximum) for v in logs)))


def critical_value():
    low, high = 0., 128.
    for _ in range(80):
        middle = (low+high)/2
        if log_survival(middle) > math.log(.05):
            low = middle
        else:
            high = middle
    return (low+high)/2


def gamma_cdf_integer(shape, z):
    """Positive Poisson-tail series with an absolute geometric remainder bound."""
    if shape < 1 or z < 0 or not math.isfinite(z):
        raise ValueError('invalid gamma arguments')
    if z == 0:
        return 0.
    term = math.exp(-z+shape*math.log(z)-math.lgamma(shape+1))
    terms = [term]
    k = shape
    for _ in range(1000):
        ratio = z/(k+1)
        if ratio < 1 and term*ratio/(1-ratio) < 1e-15:
            return checked_probability(math.fsum(terms))
        term *= ratio
        terms.append(term)
        k += 1
    raise ArithmeticError('gamma positive series did not converge')


def checked_probability(value):
    if not math.isfinite(value) or value < -1e-12 or value > 1+1e-12:
        raise ArithmeticError('invalid probability')
    return min(1., max(0., value))


def theoretical_power(noncentrality, critical=None):
    if noncentrality < -1e-10 or not math.isfinite(noncentrality):
        raise ArithmeticError('invalid noncentrality')
    critical = critical_value() if critical is None else critical
    z = critical/2
    if noncentrality <= 0:
        return checked_probability(1-gamma_cdf_integer(8, z))
    rate = noncentrality/2
    components = [math.exp(-rate+j*math.log(rate)-math.lgamma(j+1))*gamma_cdf_integer(8+j, z)
                  for j in range(129)]
    return checked_probability(1-math.fsum(components))


def truth(world, x, u):
    return .3*x**3+.5*u if world['kind'] == 'cubic' else ed.true_mean(world, x, u)


def audit_streams(seed, config):
    sites = random.Random(config['audit_input_seed_offset']+seed)
    noise = random.Random(config['audit_noise_seed_offset']+seed)
    base = [(sites.uniform(-1, 1), sites.uniform(-1, 1)) for _ in range(16)]
    errors = [noise.gauss(0, config['sigma']) for _ in range(16)]
    return {arm: [(scale*x, scale*u, error) for (x, u), error in zip(base, errors)]
            for arm, scale in [('local', 1), ('wide', 2)]}


def prepare_design(seed, config):
    stage1 = ed.fixed_config()
    streams = ed.shared_streams(seed, stage1)
    training = streams['training']
    design = [ed.basis(x, u) for x, u, _ in training]
    r = training_r(design, config['rank_tolerance'])
    audits = audit_streams(seed, config)
    prepared = {}
    for arm, data in audits.items():
        a = [ed.basis(x, u) for x, u, _ in data]
        covariance = predictive_covariance(r, a, config['sigma'])
        lower = cholesky(covariance)
        trace = math.fsum(covariance[i][i] for i in range(16))
        prepared[arm] = dict(data=data, lower=lower, variance_trace=trace,
                             coefficient_variance_trace=trace-16*config['sigma']**2,
                             minimum_cholesky_diagonal=min(lower[i][i] for i in range(16)))
    ratio = min(abs(r[i][i]) for i in range(6))/max(abs(r[i][i]) for i in range(6))
    return dict(training=training, design=design, arms=prepared, r_diagonal_ratio=ratio)


def episode_record(seed, name, world, prepared, config, critical):
    observations = [(x, u, truth(world, x, u)+error) for x, u, error in prepared['training']]
    fitted = ed.least_squares(prepared['design'], [y for _, _, y in observations], range(6), config['rank_tolerance'])
    # Freeze observed-data predictions before constructing audit outcomes or evaluator-only diagnostics.
    predictions = {arm: [ed.predict(fitted['coefficients'], x, u) for x, u, _ in values['data']]
                   for arm, values in prepared['arms'].items()}
    arms = {}
    for arm, values in prepared['arms'].items():
        observed = [(x, u, truth(world, x, u)+error) for x, u, error in values['data']]
        residuals = [y-p for (_, _, y), p in zip(observed, predictions[arm])]
        q = quadratic_form(values['lower'], residuals)
        log_p = log_survival(q)
        arms[arm] = dict(observations=observed, predictions=predictions[arm], residuals=residuals,
            q=q, log_p=log_p, p_value=math.exp(log_p), uncertainty_rejected=log_p <= math.log(config['alpha']),
            **ed.audit_predictions(predictions[arm], [y for _, _, y in observed], config['sigma']),
            variance_trace=values['variance_trace'], coefficient_variance_trace=values['coefficient_variance_trace'],
            minimum_cholesky_diagonal=values['minimum_cholesky_diagonal'])
    # Hidden means enter only this evaluator block, never fitting or rejection above.
    noiseless = ed.least_squares(prepared['design'], [truth(world, x, u) for x, u, _ in observations], range(6), config['rank_tolerance'])
    grids = ed.query_grids()
    evaluation = dict(world=world, noiseless_coefficients=noiseless['coefficients'],
        **{key+'_mse': statistics.mean((ed.predict(fitted['coefficients'], x, u)-truth(world, x, u))**2 for x, u in points)
           for key, points in grids.items()})
    for arm, values in prepared['arms'].items():
        delta = [truth(world, x, u)-ed.predict(noiseless['coefficients'], x, u) for x, u, _ in values['data']]
        noncentrality = quadratic_form(values['lower'], delta)
        arms[arm]['evaluator_only'] = dict(delta=delta, noncentrality=noncentrality,
                                          theoretical_power=theoretical_power(noncentrality, critical))
    return dict(schema_version=1, seed=seed, world=name, training=observations, fitted=fitted, arms=arms,
                evaluator_only=evaluation, r_diagonal_ratio=prepared['r_diagonal_ratio'],
                observations_per_arm=40, unique_observations=56)


def assert_controls(episodes, config):
    by = {e['world']:e for e in episodes}
    for arm in ARMS:
        values = [by[name]['arms'][arm]['q'] for name in CONTROLS]
        if not all(math.isclose(values[0], value, abs_tol=config['control_absolute_tolerance'],
                                rel_tol=config['control_relative_tolerance']) for value in values[1:]):
            raise ArithmeticError('shared-control Q equality failed')


def quantiles(values):
    values = sorted(values)
    result = []
    for probability in (0., .25, .5, .75, 1.):
        index = probability*(len(values)-1)
        lower = int(index)
        upper = min(lower+1, len(values)-1)
        result.append(values[lower]+(index-lower)*(values[upper]-values[lower]))
    return result


def summarize(episodes, config, control_equality_checked=False):
    cells, paired = [], []
    for world in WORLDS:
        rows = [e for e in episodes if e['world'] == world]
        if not rows:
            continue
        for arm in ARMS:
            audits = [e['arms'][arm] for e in rows]
            for rule, key in [('uncertainty', 'uncertainty_rejected'), ('crude', 'audit_rejected')]:
                count = sum(a[key] for a in audits)
                cells.append(dict(world=world, arm=arm, rule=rule, n=len(rows), rejections=count,
                    rejection_rate=count/len(rows), wilson95=ed.wilson(count, len(rows), config['normal_interval_z']),
                    mean_uncertainty_rule_theoretical_power=statistics.mean(a['evaluator_only']['theoretical_power'] for a in audits),
                    mean_noncentrality=statistics.mean(a['evaluator_only']['noncentrality'] for a in audits),
                    means={key:statistics.mean(a[key] for a in audits) for key in
                           ('audit_mse', 'variance_trace', 'coefficient_variance_trace', 'minimum_cholesky_diagonal')},
                    mean_r_diagonal_ratio=statistics.mean(e['r_diagonal_ratio'] for e in rows),
                    latent_mse={key:statistics.mean(e['evaluator_only'][key] for e in rows) for key in ('interpolation_mse', 'extrapolation_mse')},
                    p_quantiles=quantiles([a['p_value'] for a in audits])))
        for rule, key in [('uncertainty', 'uncertainty_rejected'), ('crude', 'audit_rejected')]:
            differences = [dict(seed=e['seed'], difference=int(e['arms']['wide'][key])-int(e['arms']['local'][key])) for e in rows]
            paired.append(dict(world=world, rule=rule, local_pass_wide_reject=sum(not e['arms']['local'][key] and e['arms']['wide'][key] for e in rows),
                               **ed.paired_stats(differences, config['normal_interval_z'])))
    return dict(completed_keys=[[e['seed'], e['world']] for e in episodes], cells=cells, paired=paired,
                effective_control_n_per_arm=len({e['seed'] for e in episodes if e['world'] == 'noise_only'}),
                control_equality_checked=control_equality_checked, interval_scope='random designs/noise for fixed functions, not a population of outside laws')


def decision(summary, config, complete):
    expected = {(s, w) for s in config['seeds'] for w in WORLDS}
    keys = [tuple(k) for k in summary['completed_keys']]
    complete = bool(complete and len(keys) == len(expected) and set(keys) == expected and summary['control_equality_checked'])
    cells = {(c['world'], c['arm']):c for c in summary['cells'] if c['rule'] == 'uncertainty'}
    guards = {w+'_'+a:cells[w, a]['rejections'] <= config['maximum_control_rejections'] for w in CONTROLS for a in ARMS if (w, a) in cells}
    gains = {w:cells[w, 'wide']['rejections']-cells[w, 'local']['rejections'] >= config['minimum_net_rejections']
             for w in ('exponential', 'cubic') if (w, 'wide') in cells and (w, 'local') in cells}
    return dict(complete=complete, passed=bool(complete and len(guards) == 6 and all(guards.values()) and len(gains) == 2 and all(gains.values())),
                control_guards=guards, gain_conditions=gains,
                limitation='known full-model Gaussian diagnostic; fixed outside functions; a local ceiling can fail the comparative gain screen')


def fixed_config():
    return dict(schema_version=1, seeds=list(range(850, 890)), smoke_seeds=[840], worlds=list(WORLDS), arms=list(ARMS),
        basis=list(ed.TERMS), train_sites=12, replicates=2, audit_sites=16, sigma=.05, alpha=.05,
        audit_input_seed_offset=10100009, audit_noise_seed_offset=10100011, arm_scales={'local':1, 'wide':2},
        stage1_law_seed_offset=9100001, stage1_input_seed_offset=9200003, stage1_train_noise_seed_offset=9300007,
        coefficient_magnitude=[.5, 1.5], sparse_support_sizes=[1, 2, 3], cubic_coefficient=.3,
        rank_tolerance=1e-10, negative_q_tolerance=1e-10, control_absolute_tolerance=1e-8, control_relative_tolerance=1e-10,
        normal_interval_z=1.959963984540054, minimum_net_rejections=12, maximum_control_rejections=4,
        chi_square_df=16, critical_bisections=80, critical_bracket=[0, 128], poisson_max_j=128,
        gamma_max_terms=1000, gamma_remainder_tolerance=1e-15, probability_clamp_tolerance=1e-12,
        timeout_seconds=120, external_timeout_seconds=150, max_output_bytes=50000000,
        smoke_safety_factor=1.5, smoke_projection_limit_seconds=60, smoke_projection_limit_bytes=40000000,
        observations_per_arm=40, unique_observations_per_pair=56, loop_order='seed,world',
        interpolation_axis=[(-9+2*i)/10 for i in range(10)], extrapolation_axis=[i/2 for i in range(-4, 5)])


def validate_config(config):
    if config != fixed_config():
        raise ValueError('fixed protocol parameters differ')


def output_scope(output):
    output, runs = Path(output).resolve(), (ROOT/'results/runs').resolve()
    if ROOT not in runs.parents or output.parent != runs or not output.name.startswith('equation_domain_'):
        raise ValueError('use fresh results/runs/equation_domain_<label>')
    if output.exists():
        raise FileExistsError('output exists')
    return output


def source_hashes():
    paths = [Path(__file__).resolve(), ROOT/'tests/test_equation_domain.py',
             ROOT/'experiments/equation_domain_v0.md', ROOT/'artificial_scientist/run.py', ROOT/'artificial_scientist/equation_discovery.py']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def verify_smoke(path, config_hash, sources, config):
    path = Path(path).resolve()
    if ROOT not in path.parents:
        raise ValueError('smoke outside repository')
    meta = json.loads((path/'metadata.json').read_text())
    if (meta.get('status') != 'completed' or meta.get('mode') != 'smoke' or meta.get('completed_episodes') != 6
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
    factor = config['smoke_safety_factor']*240/6
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
    critical = critical_value()
    meta['critical_value'] = critical
    meta['omitted_mixture_cdf_bound'] = 8.28e-88
    try:
        with (output/'episodes.jsonl').open('w') as handle:
            for seed in meta['seeds']:
                worlds = ed.world_catalog(seed, ed.fixed_config())
                worlds['cubic'] = dict(kind='cubic', formula='0.3*x^3+0.5*u')
                prepared = prepare_design(seed, config)
                seed_episodes = []
                for name in WORLDS:
                    if time.perf_counter()-start > config['timeout_seconds']:
                        raise TimeoutError('internal deadline reached')
                    episode = episode_record(seed, name, worlds[name], prepared, config, critical)
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
        expected = 6 if smoke else 240
        if len(episodes) != expected and meta['status'] == 'completed':
            meta['status'] = 'incomplete'
        controls_checked = bool(episodes and len(episodes) == 6*len(verified_control_seeds))
        meta['verified_control_seeds'] = verified_control_seeds
        summary = summarize(episodes, config, controls_checked)
        result = decision(summary, config, meta['status'] == 'completed' and not smoke)
        write('summary.json', summary)
        write('decision.json', result)
        meta.update(completed_episodes=len(episodes), expected_episodes=expected, completed_observations=len(episodes)*56, completed_audits=len(episodes)*2,
                    elapsed_seconds=time.perf_counter()-start)
        meta['artifact_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()
                                  if p.is_file() and p.name != 'metadata.json'}
        other_bytes = sum(p.stat().st_size for p in output.iterdir() if p.is_file() and p.name != 'metadata.json')
        meta['artifact_bytes'] = 0
        for _ in range(20):
            if smoke:
                factor = config['smoke_safety_factor']*240/6
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
    parser.add_argument('--config', type=Path, default=Path('experiments/equation_domain_v0.json'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--smoke-evidence', type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output, args.smoke, args.smoke_evidence), indent=2))
