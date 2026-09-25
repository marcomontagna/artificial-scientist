"""Fixed-schedule causal diagnostic study; no learned policy or novelty claim."""
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

from .causal_feasibility import (
    ACTIONS, DAGS, STATES, confounded_world, context_index, graph_world,
    supported, validate_observation,
)
from .run import git_info

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('structured_mixture', 'kt')
PARENT_SETS = tuple((node, parents) for node in range(3)
                    for size in range(3)
                    for parents in itertools.combinations([i for i in range(3) if i != node], size))
GRAPH_SCORES = tuple(tuple(PARENT_SETS.index((node, parents))
                          for node, parents in enumerate(graph)) for graph in DAGS)
UPDATES = tuple(tuple(tuple((i, context_index(state, parents), state[node])
                           for i, (node, parents) in enumerate(PARENT_SETS)
                           if target is None or target[0] != node)
                     for state in STATES) for target in ACTIONS)


class NullMLE:
    """Exact DAG maximum via twelve incremental Bernoulli parent-set scores."""
    def __init__(self, max_steps=400):
        self.cells = [[[0, 0] for _ in range(2**len(parents))] for _, parents in PARENT_SETS]
        self.scores = [0.] * 12
        self.n = 0
        self.max_steps = max_steps
        self.nlogn = [0.] + [n*math.log(n) for n in range(1, max_steps+1)]
        self.log_likelihood = 0.

    def observe(self, action, outcome):
        validate_observation(action, outcome)
        if self.n >= self.max_steps:
            raise ValueError('history exceeds declared maximum')
        f = self.nlogn
        for i, context, bit in UPDATES[action][outcome]:
            cell = self.cells[i][context]
            count, total = cell[bit], cell[0]+cell[1]
            self.scores[i] += f[count+1]-f[count]-f[total+1]+f[total]
            cell[bit] += 1
        self.n += 1
        s = self.scores
        self.log_likelihood = max(s[i]+s[j]+s[k] for i, j, k in GRAPH_SCORES)
        return self.log_likelihood


class KT:
    def __init__(self, prior=.5):
        if not math.isfinite(prior) or prior <= 0:
            raise ValueError('positive KT prior required')
        self.prior = prior
        self.counts = [[0]*8 for _ in ACTIONS]
        self.totals = [0]*7
        self.log_q = 0.

    def predictive(self, action, outcome):
        validate_observation(action, outcome)
        k = 8 if action == 0 else 4
        return (self.counts[action][outcome]+self.prior)/(self.totals[action]+k*self.prior)

    def observe(self, action, outcome):
        self.log_q += math.log(self.predictive(action, outcome))
        self.counts[action][outcome] += 1
        self.totals[action] += 1
        return self.log_q


def mixture_tables(config):
    return tuple(confounded_world(pair, noise) for pair in config['pairs']
                 for noise in config['mixture_noise'])


def logsumexp(values):
    largest = max(values)
    return largest + math.log(math.fsum(math.exp(v-largest) for v in values))


class StructuredMixture:
    def __init__(self, config, tables=None):
        self.tables = mixture_tables(config) if tables is None else tables
        self.log_prior = -math.log(len(self.tables))
        self.component_log_likelihoods = [0.] * len(self.tables)
        # Structural zeros are never observed under the corresponding intervention.
        self.log_probabilities = tuple(tuple(tuple(math.log(w[a][y]) if w[a][y] else -math.inf
                                                   for w in self.tables) for y in range(8)) for a in range(7))
        self.log_q = 0.

    def predictive(self, action, outcome):
        validate_observation(action, outcome)
        normalizer = logsumexp(self.component_log_likelihoods)
        return math.fsum(math.exp(v-normalizer)*world[action][outcome]
                         for v, world in zip(self.component_log_likelihoods, self.tables))

    def observe(self, action, outcome):
        validate_observation(action, outcome)
        self.component_log_likelihoods = [v+p for v, p in zip(
            self.component_log_likelihoods, self.log_probabilities[action][outcome])]
        self.log_q = logsumexp(self.component_log_likelihoods)+self.log_prior
        return self.log_q


class DiagnosticPair:
    """Both normalized numerators consume exactly one shared observation history."""
    def __init__(self, config, tables=None):
        self.null = NullMLE(config['steps'])
        self.numerators = {'structured_mixture': StructuredMixture(config, tables),
                           'kt': KT(config['kt_prior'])}

    def observe(self, action, outcome):
        denominator = self.null.observe(action, outcome)
        return {name: numerator.observe(action, outcome)-denominator
                for name, numerator in self.numerators.items()}


def replay_history(actions, outcomes, config):
    if len(actions) != len(outcomes):
        raise ValueError('action/outcome lengths differ')
    pair, history = DiagnosticPair(config), []
    for a, y in zip(actions, outcomes):
        history.append(pair.observe(int(a), int(y)))
    return history


def inverse_cdf(probabilities, uniform, action):
    if not math.isfinite(uniform) or not 0 <= uniform < 1:
        raise ValueError('uniform must be in [0,1)')
    if len(probabilities) != 8 or any(not math.isfinite(p) or p < 0 for p in probabilities):
        raise ValueError('eight nonnegative probabilities required')
    if type(action) is not int or not 0 <= action < 7:
        raise ValueError('invalid action')
    if any(p > 0 and not supported(action, STATES[y]) for y, p in enumerate(probabilities)):
        raise ValueError('distribution violates intervention support')
    if not math.isclose(math.fsum(probabilities), 1., rel_tol=0., abs_tol=1e-12):
        raise ValueError('probabilities must sum to one')
    cumulative, last_positive = 0., None
    for outcome, p in enumerate(probabilities):
        if p > 0:
            last_positive = outcome
            cumulative += p
            if uniform < cumulative:
                return outcome
    # A rounding shortfall must never send an observation into a trailing zero.
    return last_positive


def biased_confounding(pair, noise, u_probability, third_probability):
    result = []
    for action, target in enumerate(ACTIONS):
        row = []
        for state in STATES:
            if not supported(action, state):
                row.append(0.)
                continue
            row.append(math.fsum((u_probability if u else 1-u_probability)*math.prod(
                (1-noise if state[node] == u else noise) if node in pair else
                (third_probability if state[node] else 1-third_probability)
                for node in range(3) if target is None or node != target[0]) for u in (0, 1)))
        result.append(row)
    return result


def world_catalog(seed, config):
    worlds = []
    for pair in config['pairs']:
        for noise in config['noise']:
            worlds.append(dict(name=f'pair{pair[0]}{pair[1]}_e{noise:g}', null=False,
                kind='fair_confounding', pair=pair, noise=noise,
                probabilities=confounded_world(pair, noise)))
    nulls = config['nulls']
    def add_graph(name, graph, cpts, **extra):
        worlds.append(dict(name=name, null=True, kind='observed_dag', parents=graph,
                           cpts=cpts, probabilities=graph_world(graph, cpts), **extra))
    add_graph('null_fair', ((), (), ()), [[p] for p in nulls['fair_roots']])
    add_graph('null_biased', ((), (), ()), [[p] for p in nulls['biased_roots']])
    e = nulls['fork_noise']
    add_graph('null_fork', ((), (0,), (0,)), [[nulls['fork_root']], [e, 1-e], [e, 1-e]])
    add_graph('null_boundary', ((), (0,), (0,)),
              [[nulls['boundary_root']]] + nulls['boundary_children'])
    rng = random.Random(seed+config['stream_offsets']['world'])
    index = rng.randrange(len(DAGS))
    graph = DAGS[index]
    cpts = [[rng.uniform(*nulls['random_cpt_range']) for _ in range(2**len(parents))]
            for parents in graph]
    add_graph('null_random', graph, cpts, dag_index=index)
    stress = config['stress']
    worlds.append(dict(name='stress_biased_u', null=False, kind='biased_confounding',
        **stress, probabilities=biased_confounding(**stress)))
    return worlds


def sampled_history(world, seed, schedule, config):
    if schedule not in config['schedules']:
        raise ValueError('undeclared schedule')
    observation = random.Random(seed+config['stream_offsets']['observation'])
    action_rng = random.Random(seed+config['stream_offsets']['action'])
    for tick in range(config['steps']):
        action = action_rng.randrange(7) if schedule == 'random7' else tick % 7
        yield action, inverse_cdf(world['probabilities'][action], observation.random(), action)


def episode_record(world, seed, schedule, config, deadline=math.inf, tables=None):
    pair = DiagnosticPair(config, tables)
    threshold = math.log(1/config['alpha'])+config['alarm_guard']
    metrics = {name: dict(first_alarm=None, max_log_e=-math.inf, snapshots={}) for name in NAMES}
    actions, outcomes = [], []
    for n, (action, outcome) in enumerate(sampled_history(world, seed, schedule, config), 1):
        if n % 16 == 1 and time.perf_counter() > deadline:
            raise TimeoutError('internal experiment deadline reached')
        evidence = pair.observe(action, outcome)
        actions.append(str(action))
        outcomes.append(str(outcome))
        for name, value in evidence.items():
            record = metrics[name]
            record['max_log_e'] = max(record['max_log_e'], value)
            if record['first_alarm'] is None and value >= threshold:
                record['first_alarm'] = n
            if n in config['snapshots']:
                record['snapshots'][str(n)] = value
    for name, record in metrics.items():
        alarm = record['first_alarm']
        record.update(censored=alarm is None,
                      capped_time=config['censor_cap'] if alarm is None else min(alarm, config['censor_cap']),
                      mean_prequential_log_loss=-pair.numerators[name].log_q/config['steps'])
    return dict(world=world['name'], null=world['null'], seed=seed, schedule=schedule,
                steps=config['steps'], actions=''.join(actions), outcomes=''.join(outcomes), numerators=metrics)


def wilson(successes, n, z):
    if n <= 0 or not 0 <= successes <= n:
        raise ValueError('valid binomial counts required')
    p, z2 = successes/n, z*z
    center = (p+z2/(2*n))/(1+z2/n)
    radius = z*math.sqrt(p*(1-p)/n+z2/(4*n*n))/(1+z2/n)
    return [max(0., center-radius), min(1., center+radius)]


def summarize(episodes, config):
    cells = {}
    for episode in episodes:
        for name, metrics in episode['numerators'].items():
            cells.setdefault((episode['world'], episode['schedule'], name, episode['null']), []).append(metrics)
    result = []
    for (world, schedule, name, null), values in sorted(cells.items()):
        detections = {}
        for horizon in config['snapshots']:
            count = sum(v['first_alarm'] is not None and v['first_alarm'] <= horizon for v in values)
            detections[str(horizon)] = dict(count=count, rate=count/len(values),
                                           wilson=wilson(count, len(values), config['wilson_z']))
        result.append(dict(world=world, schedule=schedule, numerator=name, null=null, n=len(values),
                           detections=detections, mean_capped_time=statistics.mean(v['capped_time'] for v in values),
                           censored=sum(v['censored'] for v in values),
                           mean_prequential_log_loss=statistics.mean(v['mean_prequential_log_loss'] for v in values)))
    return result


def study_gate(episodes, summary, config, completed):
    names = [w['name'] for w in world_catalog(0, config)]
    expected = {(s, w, a) for s in config['seeds'] for w in names for a in config['schedules']}
    observed = {(e['seed'], e['world'], e['schedule']) for e in episodes}
    complete = (completed and observed == expected and len(episodes) == len(expected)
                and all(e['steps'] == config['steps'] and len(e['actions']) == config['steps']
                        and len(e['outcomes']) == config['steps'] and set(e['numerators']) == set(NAMES)
                        for e in episodes))
    last = str(config['steps'])
    primary = [r for r in summary if r['world'] in config['gate_worlds'] and r['numerator'] == config['primary']]
    required = len(config['gate_worlds'])*len(config['schedules'])
    power_pass = len(primary) == required and all(
        r['n'] == config['gate_n'] and r['detections'][last]['wilson'][0] >= config['power_target']
        and r['detections'][last]['count'] >= config['gate_required_detections'] for r in primary)
    debug = [dict(world=r['world'], schedule=r['schedule'], numerator=r['numerator'],
                  rate=r['detections'][last]['rate']) for r in summary
             if r['null'] and r['detections'][last]['rate'] > config['null_debug_rate']]
    return dict(passed=bool(complete and power_pass and not debug), complete=bool(complete),
                primary_power_pass=bool(power_pass), null_audit_required=bool(debug), null_debug_cells=debug,
                completed_episodes=len(episodes), expected_episodes=len(expected),
                interpretation='exploratory supplied-family diagnostic feasibility; not novelty or action-policy evidence')


def validate_config(config):
    # This version implements the reviewed fixed experiment, not a sweep interface.
    required = {'steps', 'seeds', 'alpha', 'alarm_guard', 'snapshots', 'schedules', 'noise', 'pairs',
        'mixture_noise', 'primary', 'power_target', 'null_debug_rate', 'timeout_seconds', 'max_output_bytes',
        'kt_prior', 'wilson_z', 'censor_cap', 'stream_offsets', 'nulls', 'stress', 'smoke_seeds',
        'smoke_worlds', 'external_timeout_seconds', 'smoke_projection_limit_seconds', 'smoke_safety_factor',
        'gate_worlds', 'gate_required_detections', 'gate_n', 'loop_order'}
    if set(config) != required:
        raise ValueError('config keys differ from reviewed schema')
    fixed = dict(steps=400, seeds=list(range(200, 400)), snapshots=[100, 200, 400],
                 schedules=['random7', 'roundrobin7'], pairs=[[0,1], [0,2], [1,2]],
                 noise=[.05,.2,.35], primary='structured_mixture', kt_prior=.5, censor_cap=401,
                 smoke_seeds=list(range(190,195)), smoke_worlds=['null_fair','pair01_e0.05'],
                 gate_n=200, gate_required_detections=172, loop_order='seed,world,schedule')
    if any(config[k] != v for k, v in fixed.items()):
        raise ValueError('fixed study layout differs from reviewed protocol')
    if (config['alpha'] != .05 or config['alarm_guard'] != 1e-9 or config['power_target'] != .8
            or config['null_debug_rate'] != .1 or config['timeout_seconds'] != 500
            or config['max_output_bytes'] != 100000000 or config['external_timeout_seconds'] != 540
            or config['smoke_projection_limit_seconds'] != 350 or config['smoke_safety_factor'] != 1.25
            or config['wilson_z'] != 1.959963984540054):
        raise ValueError('fixed threshold/resource constants differ')
    if config['mixture_noise'] != [.025+.05*k for k in range(10)]:
        raise ValueError('fixed mixture grid differs')
    if config['gate_worlds'] != ['pair01_e0.05','pair02_e0.05','pair12_e0.05']:
        raise ValueError('primary gate cells differ')
    if config['stream_offsets'] != dict(observation=1000003, action=2000003, world=3000003):
        raise ValueError('stream offsets differ')
    if config['nulls'] != dict(fair_roots=[.5,.5,.5], biased_roots=[.2,.5,.8], fork_root=.5,
            fork_noise=.2, boundary_root=.5, boundary_children=[[0,1],[1,0]], random_cpt_range=[.1,.9]):
        raise ValueError('null definitions differ')
    if config['stress'] != dict(pair=[0,1], u_probability=.2, noise=.05, third_probability=.5):
        raise ValueError('stress definition differs')


def output_scope(output):
    output, runs = Path(output).resolve(), (ROOT/'results/runs').resolve()
    if ROOT not in runs.parents or output.parent != runs or not output.name.startswith('causal_diagnostic_'):
        raise ValueError('use new results/runs/causal_diagnostic_<label>')
    if output.exists():
        raise FileExistsError('output exists; choose a fresh directory')
    return output


def source_hashes():
    paths = [Path(__file__).resolve(), ROOT/'artificial_scientist/causal_feasibility.py',
             ROOT/'artificial_scientist/run.py', ROOT/'tests/test_causal_diagnostic.py',
             ROOT/'experiments/causal_diagnostic_v0.md']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def verify_smoke(path, config_hash, sources, config):
    path = Path(path).resolve()
    if ROOT not in path.parents:
        raise ValueError('smoke evidence must be inside repository')
    meta = json.loads((path/'metadata.json').read_text())
    if (meta.get('status') != 'completed' or meta.get('mode') != 'smoke'
            or meta.get('completed_episodes') != 20 or not meta.get('sources_unchanged')
            or meta.get('config_sha256') != config_hash or meta.get('source_sha256') != sources):
        raise ValueError('smoke provenance/completion does not match source/config')
    for name, digest in meta['artifact_sha256'].items():
        if Path(name).name != name or hashlib.sha256((path/name).read_bytes()).hexdigest() != digest:
            raise ValueError('smoke artifact hash mismatch')
    elapsed = meta['elapsed_seconds']
    if not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed <= 0:
        raise ValueError('invalid smoke time')
    projection = config['smoke_safety_factor']*(elapsed/20)*6000
    if projection > config['smoke_projection_limit_seconds']:
        raise RuntimeError('smoke projects beyond fixed runtime gate; no automatic reduced study')
    return dict(path=str(path.relative_to(ROOT)), elapsed_seconds=elapsed,
                projected_full_seconds=projection, evidence_metadata_sha256=hashlib.sha256((path/'metadata.json').read_bytes()).hexdigest())


def run(config_path, output, smoke=False, smoke_evidence=None):
    config_path = Path(config_path).resolve()
    if ROOT not in config_path.parents:
        raise ValueError('config must be inside repository')
    raw = config_path.read_bytes()
    config = json.loads(raw)
    validate_config(config)
    output = output_scope(output)
    config_hash, sources = hashlib.sha256(raw).hexdigest(), source_hashes()
    evidence = None
    if not smoke:
        if smoke_evidence is None:
            raise ValueError('full run requires matching --smoke-evidence')
        evidence = verify_smoke(smoke_evidence, config_hash, sources, config)
    started = time.perf_counter()
    metadata = dict(git_info(ROOT), mode='smoke' if smoke else 'full', status='running',
        config_sha256=config_hash, source_sha256=sources, smoke_evidence=evidence,
        python=platform.python_version(), platform=platform.platform(),
        seeds=config['smoke_seeds'] if smoke else config['seeds'],
        seed_status='development, inspected after execution; not held-out',
        external_timeout_seconds=config['external_timeout_seconds'],
        interpretation='fixed schedules and supplied mixture family; no policy/novelty claim')
    output.mkdir(parents=True, exist_ok=False)
    used = 0
    def write_json(name, data):
        nonlocal used
        text = json.dumps(data, indent=2, allow_nan=False)+'\n'
        used += len(text.encode())
        if used > config['max_output_bytes']:
            raise RuntimeError('output cap reached')
        (output/name).write_text(text)
    def append_json(handle, value):
        nonlocal used
        text = json.dumps(value, separators=(',', ':'), allow_nan=False)+'\n'
        used += len(text.encode())
        # Reserve room for partial aggregates and failure metadata.
        if used > config['max_output_bytes']-5_000_000:
            raise RuntimeError('output cap reserve reached')
        handle.write(text)
        handle.flush()
    write_json('config.json', config)
    write_json('metadata.json', metadata)
    episodes, error = [], None
    try:
        tables = mixture_tables(config)
        with (output/'worlds.jsonl').open('w') as worlds_file, (output/'episodes.jsonl').open('w') as episode_file:
            for seed in metadata['seeds']:
                catalog = world_catalog(seed, config)
                append_json(worlds_file, dict(seed=seed, worlds=catalog))
                for world in catalog:
                    if smoke and world['name'] not in config['smoke_worlds']:
                        continue
                    for schedule in config['schedules']:
                        episode = episode_record(world, seed, schedule, config,
                                                 started+config['timeout_seconds'], tables)
                        append_json(episode_file, episode)
                        episodes.append(episode)
        metadata['status'] = 'completed'
    except Exception as exc:
        error = exc
        metadata.update(status='failed_partial', error=type(exc).__name__+': '+str(exc))
    finally:
        metadata['sources_unchanged'] = sources == source_hashes() and hashlib.sha256(config_path.read_bytes()).hexdigest() == config_hash
        if not metadata['sources_unchanged']:
            metadata['status'] = 'invalid_source_changed'
        expected = 20 if smoke else 6000
        if len(episodes) != expected and metadata['status'] == 'completed':
            metadata['status'] = 'incomplete'
        summary = summarize(episodes, config)
        gate = study_gate(episodes, summary, config, metadata['status'] == 'completed' and not smoke)
        write_json('summary.json', summary)
        write_json('gate.json', gate)
        metadata.update(completed_episodes=len(episodes), expected_episodes=expected,
                        completed_observations=sum(e['steps'] for e in episodes),
                        elapsed_seconds=time.perf_counter()-started)
        if smoke:
            metadata['projected_full_seconds'] = config['smoke_safety_factor']*(metadata['elapsed_seconds']/20)*6000
            metadata['resource_go'] = (metadata['status'] == 'completed' and
                                      metadata['projected_full_seconds'] <= config['smoke_projection_limit_seconds'])
        metadata['artifact_sha256'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.iterdir() if p.is_file() and p.name != 'metadata.json'}
        write_json('metadata.json', metadata)
    if error is not None:
        raise error
    if metadata['status'] != 'completed':
        raise RuntimeError('run invalid or incomplete; see saved metadata')
    return gate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('experiments/causal_diagnostic_v0.json'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--smoke-evidence', type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output, args.smoke, args.smoke_evidence), indent=2))
