"""Small procedural sequence worlds and known context-model baselines."""
import argparse
import csv
import hashlib
import json
import platform
import random
import statistics
import time
from collections import deque
from pathlib import Path

from .metrics import scores
from .run import git_info

CONDITIONS = ('stable', 'parameter', 'noise', 'structural')


def probability_one(history, condition, changed, lag):
    """Evaluator-only rule; history is oldest to newest, lag 1 is newest."""
    target, match = history[-1], 0.8
    if changed:
        if condition == 'structural':
            target ^= history[-lag]
        elif condition == 'parameter':
            match = 0.2
        elif condition == 'noise':
            match = 0.5
    return match if target else 1 - match


def generate(seed, condition, steps, change_at):
    if condition not in CONDITIONS:
        raise ValueError('unknown condition')
    history = deque((random.Random(seed + 3000001).choices((0, 1), k=5)), maxlen=5)
    lag = random.Random(seed + 1000003).randint(2, 5)
    noise = random.Random(seed + 2000003)
    observations = []
    for tick in range(steps):
        p = probability_one(history, condition, tick >= change_at, lag)
        outcome = int(noise.random() < p)
        observations.append(outcome)
        history.append(outcome)
    return observations, lag


class ContextPredictor:
    """Discount data counts, with fixed Beta(1,1) pseudocounts."""
    def __init__(self, order, discount=0.99):
        self.order, self.discount = order, discount
        self.history = deque(maxlen=order)
        self.counts = {}

    def context(self):
        return (-1,) * (self.order - len(self.history)) + tuple(self.history)

    def predict(self):
        success, failure = self.counts.get(self.context(), (0.0, 0.0))
        return (success + 1) / (success + failure + 2)

    def update(self, outcome):
        if outcome not in (0, 1):
            raise ValueError('binary outcome required')
        for counts in self.counts.values():
            counts[0] *= self.discount
            counts[1] *= self.discount
        counts = self.counts.setdefault(self.context(), [0.0, 0.0])
        counts[0 if outcome else 1] += 1
        self.history.append(outcome)

    def storage(self):
        # Logical slots include context keys, data counts and history capacity.
        return (self.order + 2) * len(self.counts) + self.order


class OrderMixture:
    def __init__(self, discount=0.99, share=0.01):
        self.models = [ContextPredictor(k, discount) for k in range(1, 6)]
        self.weights = [0.2] * 5
        self.share = share

    def predict(self):
        return sum(w * m.predict() for w, m in zip(self.weights, self.models))

    def update(self, outcome):
        likelihoods = [m.predict() if outcome else 1 - m.predict() for m in self.models]
        evidence = sum(w * p for w, p in zip(self.weights, likelihoods))
        self.weights = [(1 - self.share) * w * p / evidence + self.share / 5
                        for w, p in zip(self.weights, likelihoods)]
        for model in self.models:
            model.update(outcome)

    def storage(self):
        return len(self.weights) + sum(m.storage() for m in self.models)


def simulate(config):
    steps, change = config['steps'], config['change_at']
    seeds = config['seeds']
    if type(steps) is not int or type(change) is not int or not 0 < change < steps <= 10000:
        raise ValueError('require 0 < change_at < steps <= 10000')
    if (not isinstance(seeds, list) or not seeds or len(seeds) > 20
            or any(type(s) is not int or not 0 <= s < 1000 for s in seeds)
            or len(set(seeds)) != len(seeds)):
        raise ValueError('require 1..20 distinct development seeds in [0,1000)')
    rows, summary = [], []
    for seed in seeds:
        for condition in CONDITIONS:
            outcomes, lag = generate(seed, condition, steps, change)
            learners = {'order1': ContextPredictor(1), 'order5': ContextPredictor(5),
                        'order_mixture': OrderMixture()}
            groups = {(name, phase): [] for name in learners for phase in ('before', 'after')}
            for tick, outcome in enumerate(outcomes):
                phase = 'before' if tick < change else 'after'
                for name, learner in learners.items():
                    probability = learner.predict()
                    row = dict(seed=seed, condition=condition, tick=tick, phase=phase,
                               baseline=name, outcome=outcome, probability=probability,
                               logical_slots=learner.storage(), **scores(probability, outcome))
                    rows.append(row)
                    groups[name, phase].append(row)
                    learner.update(outcome)
            for (name, phase), group in groups.items():
                summary.append(dict(seed=seed, condition=condition, baseline=name,
                                    phase=phase, n=len(group), evaluator_lag=lag,
                                    **{key: statistics.mean(r[key] for r in group)
                                       for key in ('log_loss', 'brier', 'logical_slots')}))
    return rows, summary


def run(config_path, output):
    root = Path(__file__).resolve().parents[1]
    output = Path(output).resolve()
    if root not in output.parents:
        raise ValueError('output must be inside this repository')
    if output.exists():
        raise FileExistsError('choose a fresh output directory')
    raw = Path(config_path).read_bytes()
    config = json.loads(raw)
    started = time.perf_counter()
    rows, summary = simulate(config)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'config.json').write_bytes(raw)
    with (output / 'predictions.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    metadata = dict(git_info(root), python=platform.python_version(),
                    platform=platform.platform(), elapsed_seconds=time.perf_counter()-started,
                    config_sha256=hashlib.sha256(raw).hexdigest(),
                    purpose='development benchmark calibration; no novel learner or inference',
                    settings={'discount': 0.99, 'share': 0.01, 'orders': [1,2,3,4,5]},
                    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('experiments/state_revision_v0.json'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.config, args.output)
    print('Saved development benchmark:', args.output)
