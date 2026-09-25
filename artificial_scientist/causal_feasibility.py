"""Exact tiny-world feasibility and sequential arithmetic; no learned action policy."""
import argparse
import hashlib
import itertools
import json
import math
import platform
import time
from pathlib import Path

from .run import git_info

ROOT = Path(__file__).resolve().parents[1]
STATES = tuple(itertools.product((0, 1), repeat=3))
ACTIONS = (None,) + tuple((i, v) for i in range(3) for v in (0, 1))
CONFIG = dict(noise=[0.5, 0.35, 0.2, 0.05], pairs=[[0, 1], [0, 2], [1, 2]],
              null_fork_noise=0.2, zero_tolerance=1e-10, separation_tolerance=1e-8)


def dag_bank():
    edges = tuple((i, j) for i in range(3) for j in range(3) if i != j)
    bank = []
    for bits in itertools.product((0, 1), repeat=6):
        parents = tuple(tuple(i for (i, j), on in zip(edges, bits) if on and j == node)
                        for node in range(3))
        seen = set()
        for _ in range(3):
            seen.update(i for i in range(3) if set(parents[i]) <= seen)
        if len(seen) == 3:
            bank.append(parents)
    return tuple(bank)


DAGS = dag_bank()


def supported(action, state):
    target = ACTIONS[action]
    return target is None or state[target[0]] == target[1]


def validate_observation(action, outcome):
    if type(action) is not int or not 0 <= action < 7:
        raise ValueError('action index must be an integer in [0,7)')
    if type(outcome) is not int or not 0 <= outcome < 8 or not supported(action, STATES[outcome]):
        raise ValueError('outcome must be a feasible state index for the action')


def confounded_world(pair, noise):
    if len(pair) != 2 or len(set(pair)) != 2 or any(i not in range(3) for i in pair):
        raise ValueError('two distinct observed variables required')
    if not math.isfinite(noise) or not 0 <= noise <= 0.5:
        raise ValueError('noise must lie in [0,0.5]')
    regimes = []
    for action, target in enumerate(ACTIONS):
        probabilities = []
        for state in STATES:
            if not supported(action, state):
                probabilities.append(0.)
                continue
            probabilities.append(math.fsum(.5 * math.prod(
                (1-noise if state[i] == u else noise) if i in pair else .5
                for i in range(3) if target is None or i != target[0]) for u in (0, 1)))
        regimes.append(probabilities)
    return regimes


def context_index(state, parents):
    return sum(state[p] << bit for bit, p in enumerate(parents))


def graph_world(graph, cpts):
    regimes = []
    for a, target in enumerate(ACTIONS):
        row = []
        for state in STATES:
            p = 0. if not supported(a, state) else 1.
            for i, parents in enumerate(graph):
                if target is None or target[0] != i:
                    q = cpts[i][context_index(state, parents)]
                    p *= q if state[i] else 1-q
            row.append(p)
        regimes.append(row)
    return regimes


def fit_graph(counts, graph):
    """Exact MLE CPTs from fractional or integer regime/state counts."""
    cpts, log_likelihood = [], 0.
    for node, parents in enumerate(graph):
        cells = [[0., 0.] for _ in range(2**len(parents))]
        for action, target in enumerate(ACTIONS):
            if target is not None and target[0] == node:
                continue
            for state, count in zip(STATES, counts[action]):
                cells[context_index(state, parents)][state[node]] += count
        rates = []
        for n0, n1 in cells:
            n = n0+n1
            p = n1/n if n else .5
            rates.append(p)
            if n0:
                log_likelihood += n0*math.log(n0/n)
            if n1:
                log_likelihood += n1*math.log(n1/n)
        cpts.append(rates)
    return cpts, log_likelihood


def null_log_likelihood(counts):
    return max(fit_graph(counts, graph)[1] for graph in DAGS)


def weighted_kl(true, predicted, weights):
    terms = []
    for a, w in enumerate(weights):
        if w == 0:
            continue
        for p, q in zip(true[a], predicted[a]):
            if p:
                if q == 0:
                    return math.inf
                terms.append(w*p*math.log(p/q))
    return math.fsum(terms)


def project_world(world, weights):
    if len(weights) != 7 or any(not math.isfinite(w) or w < 0 for w in weights):
        raise ValueError('seven finite nonnegative weights required')
    if not math.isclose(math.fsum(weights), 1., abs_tol=1e-12):
        raise ValueError('weights must sum to one')
    counts = [[weights[a]*p for p in row] for a, row in enumerate(world)]
    fits = []
    for graph in DAGS:
        cpts, _ = fit_graph(counts, graph)
        fits.append(dict(parents=graph, cpts=cpts,
                         kl=weighted_kl(world, graph_world(graph, cpts), weights)))
    return fits


class SequentialDiagnostic:
    """Known likelihood-ratio statistic; validation utility, not action learner.

    Support-consistent histories always have positive null maximum likelihood.
    No clipping or plug-in alternative fit on its own scored outcome is used.
    """
    def __init__(self):
        self.counts = [[0]*8 for _ in ACTIONS]
        self.log_q = 0.

    def predictive(self, action, outcome):
        validate_observation(action, outcome)
        k = 8 if action == 0 else 4
        row = self.counts[action]
        return (row[outcome]+.5)/(sum(row)+k*.5)

    def observe(self, action, outcome):
        p = self.predictive(action, outcome)
        self.log_q += math.log(p)
        self.counts[action][outcome] += 1
        return self.log_q-null_log_likelihood(self.counts)


def designs(pair):
    indices = [a for a, target in enumerate(ACTIONS) if target and target[0] in pair]
    def uniform(active):
        return [1/len(active) if a in active else 0. for a in range(7)]
    return dict(passive=uniform([0]), uniform7=uniform(list(range(7))),
                uniform6do=uniform(list(range(1, 7))),
                privileged_pair_only=uniform(indices),
                privileged_passive_pair=uniform([0]+indices))


def calculate():
    worlds = [(f'pair{i}{j}_noise{e}', [i, j], e, confounded_world((i, j), e))
              for i, j in CONFIG['pairs'] for e in CONFIG['noise']]
    e = CONFIG['null_fork_noise']
    worlds.append(('null_fork', [1, 2], None,
                   graph_world(((), (0,), (0,)), [[.5], [e, 1-e], [e, 1-e]])))
    summaries, details = [], []
    for name, pair, noise, world in worlds:
        for design, weights in designs(pair).items():
            fits = project_world(world, weights)
            best = min(range(len(fits)), key=lambda i: fits[i]['kl'])
            zero = (name == 'null_fork' or noise == .5 or
                    design in ('passive', 'privileged_pair_only'))
            separation = fits[best]['kl']
            passed = (abs(separation) <= CONFIG['zero_tolerance'] if zero else
                      separation > CONFIG['separation_tolerance'])
            summaries.append(dict(world=name, pair=pair, noise=noise, design=design,
                                  privileged=design.startswith('privileged'), weights=weights,
                                  min_kl=separation, representative_graph=best,
                                  minimizing_graphs=[i for i, fit in enumerate(fits)
                                      if abs(fit['kl']-separation) <= CONFIG['zero_tolerance']],
                                  expected='zero' if zero else 'positive', passed=passed))
            details.append(dict(world=name, design=design, fits=fits))
    symmetry = all(max(values)-min(values) <= CONFIG['zero_tolerance']
                   for noise in CONFIG['noise'] for design in designs((0, 1))
                   for values in [[s['min_kl'] for s in summaries
                                   if s['noise'] == noise and s['design'] == design]])
    distribution_valid = all(abs(math.fsum(row)-1) <= 1e-12 and
                             all(p >= 0 and (supported(a, STATES[k]) or p == 0)
                                 for k, p in enumerate(row))
                             for _, _, _, w in worlds for a, row in enumerate(w))
    nonnegative = all(f['kl'] >= -CONFIG['zero_tolerance'] for d in details for f in d['fits'])
    gate = dict(passed=(all(s['passed'] for s in summaries) and symmetry and
                        distribution_valid and nonnegative and len(DAGS) == 25),
                checks=len(summaries), dag_count=len(DAGS), relabeling_agrees=symmetry,
                distributions_valid=distribution_valid, all_kl_nonnegative=nonnegative,
                meaning='population distinguishability and arithmetic only; no power or novelty claim',
                graph_labels='representative is arbitrary; ties do not identify a true graph')
    return summaries, details, gate


def run(output):
    output = Path(output).resolve()
    runs = (ROOT/'results/runs').resolve()
    if ROOT not in runs.parents or output.parent != runs or not output.name.startswith('causal_feasibility_'):
        raise ValueError('use fresh results/runs/causal_feasibility_<label>')
    if output.exists():
        raise FileExistsError('choose a fresh result directory')
    paths = [Path(__file__).resolve(), ROOT/'experiments/causal_feasibility_v0.md',
             ROOT/'tests/test_causal_feasibility.py']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    start = time.perf_counter()
    summaries, details, gate = calculate()
    elapsed = time.perf_counter()-start
    if elapsed > 60:
        raise TimeoutError('calculation exceeded 60-second budget')
    if any(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() != h for p, h in hashes.items()):
        raise RuntimeError('sources changed during calculation')
    output.mkdir(parents=True, exist_ok=False)
    for name, data in [('config', CONFIG), ('summary', summaries), ('graph_fits', details), ('gate', gate)]:
        (output/(name+'.json')).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')
    metadata = dict(git_info(ROOT), python=platform.python_version(), platform=platform.platform(),
                    elapsed_seconds=elapsed, source_sha256=hashes, sources_unchanged=True,
                    seeds='none; deterministic population distributions',
                    artifact_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in output.iterdir()})
    (output/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    return gate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output), indent=2))
