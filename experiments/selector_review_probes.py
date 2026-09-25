"""Recreate Claude's described probes, not the unavailable original scratch script.

Reviewed by root Codex coordinator; code review and smoke checks completed.
Full probe run pending. Run as a module from the repository root.
"""
import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import time
from collections import Counter, deque
from pathlib import Path

from artificial_scientist.adaptive_state import AdaptiveContext, SparsePredictor
from artificial_scientist.adaptive_state_v2 import CONDITIONS, ReversibleContext, generate, learners
from artificial_scientist.metrics import scores
from artificial_scientist.run import git_info
from artificial_scientist.sequence_worlds import probability_one

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {'original_dev': list(range(5)), 'claude_inspected_dev': list(range(100, 120))}
MAX_SECONDS = 540
MAX_OUTPUT_BYTES = 20_000_000


def source_hashes():
    paths = sorted((ROOT / 'artificial_scientist').glob('*.py')) + [
        Path(__file__).resolve(), ROOT / 'experiments/adaptive_state_v2.json',
        ROOT / 'research/claude_independent_review.md']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def initial_history(seed):
    return deque(random.Random(seed + 3000001).choices((0, 1), k=5), maxlen=5)


def return_stream(seed, lag):
    """Evaluator-only stable -> structural -> stable with existing RNG offsets."""
    history, noise, result = initial_history(seed), random.Random(seed + 2000003), []
    for tick in range(1800):
        p = probability_one(history, 'structural', 600 <= tick < 1200, lag)
        outcome = int(noise.random() < p)
        result.append(outcome)
        history.append(outcome)
    return result


def models_for(config, lag):
    models = learners(config)
    kw = dict(discount=config['discount'], window=config['gain_window'], every=1,
              threshold=config['gain_threshold'])
    models['v1_every1'] = AdaptiveContext(**kw)
    models['v2_every1'] = ReversibleContext(**kw, fast_discount=config['fast_discount'])
    if lag > 1:
        # Privileged structure; learns from tick zero without change-time knowledge.
        models['correct_sparse_reference'] = SparsePredictor((1, lag), config['discount'])
    return models


def one_world(config, seed, condition, returning, deadline):
    lag = int(condition[-1]) if condition.startswith('structural') else 1
    stream = return_stream(seed, lag) if returning else generate(seed, condition, 1200, 600)[0]
    models, history, totals = models_for(config, lag), initial_history(seed), {}
    event_stats = {name: dict(counts=Counter(), first_expansion_tick=None,
                   first_contraction_after_return_tick=None, sparse_active_at_return=None)
                   for name in ('v1', 'v2', 'v1_every1', 'v2_every1')}
    for tick, outcome in enumerate(stream):
        if time.perf_counter() > deadline:
            raise TimeoutError('540-second experiment limit reached')
        phase = 'before' if tick < 600 else 'return' if returning and tick >= 1200 else 'after'
        changed = tick >= 600 and (not returning or tick < 1200)
        law = 'structural' if condition.startswith('structural') else condition
        predictions = [('oracle_probability_reference', probability_one(history, law, changed, lag))]
        predictions.extend((name, model.predict()) for name, model in models.items())
        for name, p in predictions:
            loss = scores(p, outcome)
            total = totals.setdefault((name, phase), [0, 0., 0.])
            total[0] += 1
            total[1] += loss['log_loss']
            total[2] += loss['brier']
        for name, model in models.items():
            if name in event_stats and tick == 1200:
                event_stats[name]['sparse_active_at_return'] = len(model.models[model.active].lags) == 2
            event = model.update(outcome)
            if event is not None:
                stats, kind = event_stats[name], event.get('kind', 'expand')
                stats['counts'][kind] += 1
                effective = event['effective_tick']
                if kind == 'expand' and stats['first_expansion_tick'] is None:
                    stats['first_expansion_tick'] = effective
                if (returning and kind == 'contract' and 1200 < effective < len(stream)
                        and stats['first_contraction_after_return_tick'] is None):
                    stats['first_contraction_after_return_tick'] = effective
        history.append(outcome)
    rows = [dict(seed=seed, condition=condition, baseline=name, phase=phase, n=v[0],
                 log_loss=v[1]/v[0], brier=v[2]/v[0]) for (name, phase), v in totals.items()]
    events = []
    for name, stats in event_stats.items():
        contraction = stats['first_contraction_after_return_tick']
        events.append(dict(seed=seed, condition=condition, baseline=name, **stats,
                           contraction_delay=None if contraction is None else contraction-1200))
    return rows, events


def aggregate(rows):
    """Average conditions within seeds before computing seed-level SE."""
    result = []
    for group in GROUPS:
        for scenario in ('single_change', 'return_to_simple'):
            for phase in ('before', 'after', 'return'):
                selected = [r for r in rows if r['seed_group'] == group and r['scenario'] == scenario
                            and r['phase'] == phase]
                families = sorted(set('structural' if r['condition'].startswith('structural')
                                      else r['condition'] for r in selected))
                for family in families:
                    subset = [r for r in selected if r['condition'].startswith(family)]
                    by = {(r['seed'], r['condition'], r['baseline']): r['log_loss'] for r in subset}
                    for name in sorted(set(r['baseline'] for r in subset)):
                        cases = [r for r in subset if r['baseline'] == name]
                        for reference in ('matched_mixture', 'oracle_probability_reference'):
                            paired = [(r['seed'], r['log_loss']-by[r['seed'], r['condition'], reference])
                                      for r in cases]
                            means = [statistics.mean(d for s, d in paired if s == seed)
                                     for seed in sorted(set(s for s, _ in paired))]
                            result.append(dict(seed_group=group, scenario=scenario, phase=phase,
                                family=family, baseline=name, reference=reference,
                                mean_log_loss=statistics.mean(r['log_loss'] for r in cases),
                                mean_difference=statistics.mean(means),
                                seed_se=statistics.stdev(means)/math.sqrt(len(means)) if len(means)>1 else None,
                                seeds=len(means), cases=len(paired), worse_cases=sum(d>0 for _, d in paired),
                                tied_cases=sum(d==0 for _, d in paired)))
    return result


def save_json(output, name, value):
    text = json.dumps(value, indent=2, allow_nan=False) + '\n'
    used = sum(p.stat().st_size for p in output.iterdir() if p.is_file())
    if used + len(text.encode()) > MAX_OUTPUT_BYTES:
        raise RuntimeError('20 MB artifact cap exceeded')
    (output/name).write_text(text)


def run(output):
    output, runs = Path(output).resolve(), (ROOT/'results/runs').resolve()
    if ROOT not in runs.parents or output.parent != runs or not output.name.startswith('selector_review_'):
        raise ValueError('use fresh results/runs/selector_review_<label>')
    if output.exists():
        raise FileExistsError('output exists; choose a fresh label')
    config = json.loads((ROOT/'experiments/adaptive_state_v2.json').read_text())
    expected = dict(steps=1200, change_at=600, seeds=list(range(5)), discount=.99, fast_discount=.90,
                    share=.01, gain_window=128, check_every=64, gain_threshold=math.log(400))
    if config != expected:
        raise ValueError('tracked config differs from described settings; review before adapting')
    hashes = source_hashes()
    metadata = dict(git_info(ROOT), python=platform.python_version(), platform=platform.platform(),
                    source_sha256=hashes, settings=config, seed_groups=GROUPS,
                    provenance='Recreated from Claude description; original scratch script unavailable',
                    probability_oracle='privileged evaluator probability; not competitor',
                    sparse_reference='privileged correct lag; trained from tick 0; no change knowledge',
                    return_schedule={'steps':1800, 'structural_start':600, 'stable_return':1200},
                    seed_status='development/previously inspected; reserved seeds untouched',
                    timeout_seconds=MAX_SECONDS, output_limit_bytes=MAX_OUTPUT_BYTES,
                    aggregation='conditions averaged within seed; SE across seeds; case wins correlated',
                    status='running')
    output.mkdir(parents=True, exist_ok=False)
    started, rows, events = time.perf_counter(), [], []
    try:
        for group, seeds in GROUPS.items():
            for seed in seeds:
                for scenario in ('single_change', 'return_to_simple'):
                    if scenario == 'return_to_simple' and group != 'claude_inspected_dev':
                        continue
                    conditions = CONDITIONS if scenario == 'single_change' else CONDITIONS[3:]
                    for condition in conditions:
                        current, changes = one_world(config, seed, condition,
                                                     scenario=='return_to_simple', started+MAX_SECONDS)
                        for record in current + changes:
                            record.update(seed_group=group, scenario=scenario)
                        rows.extend(current)
                        events.extend(changes)
        metadata['status'] = 'completed'
    except Exception as exc:
        metadata.update(status='failed_partial', error=type(exc).__name__+': '+str(exc))
        raise
    finally:
        metadata['elapsed_seconds'] = time.perf_counter()-started
        metadata['sources_unchanged'] = hashes == source_hashes()
        if not metadata['sources_unchanged']:
            metadata['status'] = 'invalid_source_changed_during_run'
        save_json(output, 'seed_condition_means.json', rows)
        save_json(output, 'event_summary.json', events)
        save_json(output, 'comparisons.json', aggregate(rows))
        metadata['artifact_sha256'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                       for p in output.iterdir() if p.is_file()}
        save_json(output, 'metadata.json', metadata)
    if not metadata['sources_unchanged']:
        raise RuntimeError('source changed; outputs marked invalid')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    print('Saved recreated probes:', run(parser.parse_args().output))
