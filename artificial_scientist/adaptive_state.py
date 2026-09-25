"""Exploratory, observation-only sparse-context activation with explicit overhead."""
import argparse
import csv
import hashlib
import json
import math
import platform
import statistics
import time
from collections import deque
from pathlib import Path

from .metrics import scores
from .run import git_info
from .sequence_worlds import CONDITIONS, ContextPredictor, OrderMixture, generate


class SparsePredictor(ContextPredictor):
    def __init__(self, lags, discount=0.99):
        self.lags = tuple(lags)
        if not self.lags or tuple(sorted(set(self.lags))) != self.lags or self.lags[0] < 1:
            raise ValueError('increasing positive lags required')
        super().__init__(max(self.lags), discount)

    def context(self):
        return tuple(self.history[-lag] if len(self.history) >= lag else -1
                     for lag in self.lags)

    def storage(self):
        return (len(self.lags) + 2) * len(self.counts) + self.order + len(self.lags)


def sparse_bank(discount):
    return [SparsePredictor((1,), discount)] + [
        SparsePredictor((1, k), discount) for k in range(2, 6)]


class SparseMixture(OrderMixture):
    def __init__(self, discount=0.99, share=0.01):
        super().__init__(discount, share)
        self.models = sparse_bank(discount)


class AdaptiveContext:
    """Activate one shadow expert using a trailing prequential gain window.

    Total storage includes all shadows from initialization. No allocation-saving
    claim follows from the active prediction using fewer features initially.
    """
    def __init__(self, discount=0.99, window=128, every=64,
                 threshold=math.log(400), enabled=True):
        if type(window) is not int or window <= 0 or type(every) is not int or every <= 0:
            raise ValueError('positive integer window/check period required')
        if not math.isfinite(threshold) or threshold < 0:
            raise ValueError('finite nonnegative threshold required')
        self.models = sparse_bank(discount)
        self.gains = [deque(maxlen=window) for _ in range(4)]
        self.window, self.every, self.threshold = window, every, threshold
        self.enabled = enabled
        self.active = self.observed = self.checks = 0

    @property
    def active_lag(self):
        return self.models[self.active].lags[-1]

    def predict(self):
        return self.models[self.active].predict()

    def storage(self):
        # All shadows, reserved gain buffers and seven decision/config scalars.
        return sum(m.storage() for m in self.models) + 4 * self.window + 7

    def update(self, outcome):
        if outcome not in (0, 1):
            raise ValueError('binary outcome required')
        # Score models BEFORE any model sees this outcome.
        losses = [scores(m.predict(), outcome)['log_loss'] for m in self.models]
        for gain, loss in zip(self.gains, losses[1:]):
            gain.append(losses[0] - loss)
        for model in self.models:
            model.update(outcome)
        self.observed += 1
        event = None
        if self.observed >= self.window and self.observed % self.every == 0:
            self.checks += 1
            totals = [sum(gain) for gain in self.gains]
            best = max(range(4), key=lambda i: totals[i])  # smallest lag wins a tie
            if self.enabled and self.active == 0 and totals[best] > self.threshold:
                self.active = best + 1
                event = dict(observed_tick=self.observed - 1,
                             effective_tick=self.observed, selected_lag=self.active_lag,
                             window_gain=totals[best])
        return event


def validate(config):
    steps, change, seeds = config['steps'], config['change_at'], config['seeds']
    if type(steps) is not int or type(change) is not int or not 0 < change < steps <= 10000:
        raise ValueError('require 0 < change_at < steps <= 10000')
    if (not isinstance(seeds, list) or not seeds or len(seeds) > 20
            or any(type(s) is not int or not 0 <= s < 1000 for s in seeds)
            or len(set(seeds)) != len(seeds)):
        raise ValueError('distinct development seeds in [0,1000) required')
    if steps * len(seeds) * len(CONDITIONS) * 6 > 300000:
        raise ValueError('bounded prototype supports at most 300000 prediction rows')
    if not 0 < config['discount'] <= 1 or not 0 <= config['share'] <= 1:
        raise ValueError('invalid discount/share')
    if (type(config['gain_window']) is not int or not 1 <= config['gain_window'] <= 2048
            or type(config['check_every']) is not int or not 1 <= config['check_every'] <= steps
            or not math.isfinite(config['gain_threshold']) or config['gain_threshold'] < 0):
        raise ValueError('invalid bounded gain settings')


def learners_for(config):
    discount, share = config['discount'], config['share']
    kw = dict(discount=discount, window=config['gain_window'], every=config['check_every'],
              threshold=config['gain_threshold'])
    return dict(order1=ContextPredictor(1, discount), order5=ContextPredictor(5, discount),
                order_mixture=OrderMixture(discount, share),
                sparse_mixture=SparseMixture(discount, share),
                monitor_only=AdaptiveContext(**kw, enabled=False),
                adaptive=AdaptiveContext(**kw))


def simulate(config):
    validate(config)
    rows, summary, events, timings = [], [], [], []
    steps, change = config['steps'], config['change_at']
    for seed in config['seeds']:
        for condition in CONDITIONS:
            outcomes, lag = generate(seed, condition, steps, change)
            learners = learners_for(config)
            durations = {name: 0.0 for name in learners}
            groups = {(name, phase): [] for name in learners for phase in ('before', 'after')}
            for tick, outcome in enumerate(outcomes):
                phase = 'before' if tick < change else 'after'
                for name, learner in learners.items():
                    started = time.perf_counter()
                    probability = learner.predict()
                    durations[name] += time.perf_counter() - started
                    adaptive = isinstance(learner, AdaptiveContext)
                    row = dict(seed=seed, condition=condition, tick=tick, phase=phase,
                               baseline=name, outcome=outcome, probability=probability,
                               logical_slots=learner.storage(),
                               active_width=(1 if learner.active == 0 else 2) if adaptive else '',
                               active_lag=learner.active_lag if adaptive else '',
                               checks=learner.checks if adaptive else '',
                               **scores(probability, outcome))
                    rows.append(row)
                    groups[name, phase].append(row)
                    started = time.perf_counter()
                    event = learner.update(outcome)
                    durations[name] += time.perf_counter() - started
                    if event is not None:
                        events.append(dict(seed=seed, condition=condition, baseline=name,
                                           evaluator_lag=lag, **event))
            for (name, phase), group in groups.items():
                summary.append(dict(seed=seed, condition=condition, baseline=name,
                                    phase=phase, n=len(group), evaluator_lag=lag,
                                    **{key: statistics.mean(r[key] for r in group)
                                       for key in ('log_loss', 'brier', 'logical_slots')}))
            timings.extend(dict(seed=seed, condition=condition, baseline=name,
                                prediction_update_seconds=duration)
                           for name, duration in durations.items())
    return rows, summary, events, timings


def diagnostic(summary, events, seeds):
    def differences(condition, reference):
        by = {(r['seed'], r['baseline']): r['log_loss'] for r in summary
              if r['condition'] == condition and r['phase'] == 'after'}
        return [by[seed, reference] - by[seed, 'adaptive'] for seed in seeds]
    structural = differences('structural', 'order1')
    stable_penalties = [-v for v in differences('stable', 'order1')]
    stable_activations = sum(e['condition'] == 'stable' for e in events)
    return dict(label='exploratory engineering screen; not statistical confirmation',
                structural_gain_vs_order1_by_seed=structural,
                structural_gain_vs_sparse_mixture_by_seed=differences('structural', 'sparse_mixture'),
                stable_penalty_by_seed=stable_penalties,
                stable_activations=stable_activations,
                screen_passed=(statistics.mean(structural) >= .02 and
                               statistics.mean(stable_penalties) <= .01 and
                               stable_activations / len(seeds) <= .2))


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
    rows, summary, events, timings = simulate(config)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'config.json').write_bytes(raw)
    with (output / 'predictions.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for name, value in [('summary', summary), ('events', events), ('timings', timings),
                        ('diagnostic', diagnostic(summary, events, config['seeds']))]:
        (output / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n')
    sources = sorted((root / 'artificial_scientist').glob('*.py'))
    sources.append(root / 'experiments/adaptive_state_v1.md')
    metadata = dict(git_info(root), python=platform.python_version(), platform=platform.platform(),
                    elapsed_seconds=time.perf_counter() - started,
                    config_sha256=hashlib.sha256(raw).hexdigest(),
                    predictions_sha256=hashlib.sha256((output / 'predictions.csv').read_bytes()).hexdigest(),
                    source_sha256={str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sources},
                    purpose='exploratory sparse-context activation; no novelty/efficiency claim')
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return summary, events


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('experiments/adaptive_state_v1.json'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.config, args.output)
    print('Saved adaptive development experiment:', args.output)
