"""Bounded demonstration harness; hidden worlds stay on this side of the API."""
import argparse
import hashlib
import json
import math
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from .lab_api import Action, Observation, Transition
from .lab_agent import Investigator, digest
from .lab_models import Model, fit, training_rows
from .lab_world import make_world

MAX_TRACE_BYTES = 10 * 1024 * 1024  # trace.json plus pre-action journal; replay is derived
WORLD_COMMIT = 'e6920e7'
# Fixed evaluator actions, declared before first demonstration. Distinct noise
# streams, same sequences for every policy, reset/home start for each sequence.
EVALUATION = (
    (Action('push', angle=.37, magnitude=.7), Action('wait', ticks=3), Action('push', angle=2.2, magnitude=.5), Action('wait', ticks=2)),
    (Action('push', angle=4.1, magnitude=.8), Action('push', angle=1.4, magnitude=.4), Action('wait', ticks=4)),
    (Action('push', angle=2.8, magnitude=.55), Action('wait', ticks=2), Action('push', angle=5.3, magnitude=.9), Action('wait', ticks=3)),
)


class LinearReference(Model):
    """Evaluator-only fixed four-term regression, outside search node budget."""
    def __post_init__(self):
        if self.terms != ('v', 'u', 'lag_u', 'one') or len(self.coefficients) != 4:
            raise ValueError('fixed reference only')
        if not all(math.isfinite(c) for c in self.coefficients):
            raise ValueError('nonfinite reference')


def frozen_rollout(model, initial, sequence):
    observation = initial
    previous = Transition(initial, Action('reset'), initial)
    predictions = []
    carried_velocity = (0.0, 0.0)
    for action in sequence:
        (x, y), carried_velocity = model.predict_state(observation, previous, action, carried_velocity)
        next_observation = Observation(observation.tick + action.cost, x, y)
        predictions.append(asdict(next_observation))
        previous = Transition(observation, action, next_observation)
        observation = next_observation
    return predictions


def evaluate(model, rows, variant, seed, deadline):
    linear_terms = ('v', 'u', 'lag_u', 'one')
    references = dict(learned=model, persistence=Model((), ()), home=Model(('p',), (-1.0,)),
                      linear=LinearReference(linear_terms, fit(linear_terms, rows)))
    records = []
    for index, sequence in enumerate(EVALUATION):
        if time.process_time() >= deadline:
            raise TimeoutError('evaluation CPU cap')
        world = make_world(seed + 100000 + index * 1009, variant)
        initial = world.step(Action('reset'))
        predictions = {name: frozen_rollout(m, initial, sequence) for name, m in references.items()}
        # The whole open-loop prediction tape is frozen before any evaluated
        # action. Evaluation never calls accept(), propose(), or fit() on results.
        prediction_hash = digest(predictions)
        actual = [asdict(world.step(action)) for action in sequence]
        errors = {name: [(p['x'] - a['x']) ** 2 + (p['y'] - a['y']) ** 2 for p, a in zip(tape, actual)] for name, tape in predictions.items()}
        records.append(dict(sequence=index, initial=asdict(initial), actions=[asdict(a) for a in sequence],
                            predictions=predictions, prediction_hash=prediction_hash,
                            actual=actual, squared_errors=errors, cost=world.consumed))
    metrics = {}
    for name in references:
        values = [error for r in records for error in r['squared_errors'][name]]
        metrics[name] = sum(values) / len(values)
    return dict(kind='frozen open-loop fresh interventions, descriptive single-seed comparison',
                mean_squared_position_error=metrics, records=records,
                formulas={name: m.formula for name, m in references.items()},
                warning='Scores assess observed-position prediction, not recovery of a physical law. Differencing sensor noise biases coefficients.')


def investigate(variant, policy, seed, output, budget=80, cpu_seconds=120, proposal='enumerate'):
    if type(budget) is not int or not 1 <= budget <= 80 or not 0 < cpu_seconds <= 120:
        raise ValueError('invalid resource budget')
    output = Path(output)
    if output.exists():
        raise FileExistsError('fresh output directory required')
    output.mkdir(parents=True)
    start = time.process_time()
    deadline = start + cpu_seconds
    world = make_world(seed, variant)
    agent = Investigator(world.initial, policy, seed + 700001, proposal=proposal)
    trace = dict(schema_version=1, variant=variant, policy=policy, seed=seed, proposal=proposal,
                 world_source_commit=WORLD_COMMIT, status='running', events=[],
                 initial=asdict(world.initial), assumptions='Shared coefficients, separable axes, limited grammar, noisy velocity proxy; scores are not calibrated probabilities.',
                 caps=dict(tool_units=budget, cpu_seconds=cpu_seconds, trace_bytes=MAX_TRACE_BYTES))
    journal_bytes = 0
    status = 'budget_complete'
    with (output / 'predictions_before_actions.jsonl').open('x') as journal:
        while world.consumed < budget:
            if time.process_time() >= deadline:
                status = 'incomplete_cpu_cap'; break
            plan = agent.plan(budget - world.consumed)
            if time.process_time() >= deadline:
                status = 'incomplete_cpu_cap'; break
            # Reserve space for revisions/outcome and final evaluation. Never
            # execute an action whose full record cannot fit the trace budget.
            stamp = dict(step=len(trace['events']), prediction_hash=digest(plan), plan=plan)
            journal_line = json.dumps(stamp, allow_nan=False) + '\n'
            if len(json.dumps(trace).encode()) + journal_bytes + len(journal_line.encode()) + len(json.dumps(plan).encode()) + 131072 >= MAX_TRACE_BYTES:
                status = 'incomplete_trace_cap'; break
            journal.write(journal_line); journal.flush()
            journal_bytes += len(journal_line.encode())
            action = Action(**plan['action'])
            before = time.monotonic_ns()
            outcome = world.step(action)
            errors, revision = agent.accept(action, outcome, deadline)
            if revision.get('incomplete') or time.process_time() >= deadline:
                status = 'incomplete_cpu_cap'
            event = dict(step=len(trace['events']), **plan, prediction_hash=stamp['prediction_hash'],
                         execution_started_ns=before, after=asdict(outcome), cost=action.cost, total_cost=world.consumed,
                         errors=errors, revision=revision, models_after=[m.snapshot() for m in agent.models])
            trace['events'].append(event)
            if status.startswith('incomplete'):
                break
    trace['status'] = status
    trace['final_models'] = [m.snapshot() for m in agent.models]
    trace['selected_model'] = agent.final_model().snapshot()
    trace['training_cost'] = world.consumed
    trace['search_cost'] = dict(agent.search_cost)
    trace['interpretation'] = 'Integration demonstration; no novelty, calibrated confidence, physical-law recovery or policy-superiority claim.'
    if not status.startswith('incomplete'):
        try:
            trace['evaluation'] = evaluate(agent.final_model(), training_rows(agent.history), variant, seed, deadline)
        except TimeoutError:
            trace['status'] = 'incomplete_evaluation_cpu_cap'
    if time.process_time() >= deadline and not trace['status'].startswith('incomplete'):
        trace['status'] = 'incomplete_cpu_cap'
    trace['cpu_seconds'] = time.process_time() - start
    encoded = json.dumps(trace, allow_nan=False).encode()
    if len(encoded) + journal_bytes > MAX_TRACE_BYTES:
        raise RuntimeError('trace byte cap violated')
    (output / 'trace.json').write_bytes(encoded)
    return trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', choices=('development', 'challenge', 'noise'), default='development')
    parser.add_argument('--seed', type=int, default=260926)
    parser.add_argument('--proposal', choices=('enumerate', 'guided', 'guided-partial'), default='enumerate')
    parser.add_argument('--policies', nargs='+', choices=('active', 'random', 'coverage'), default=['active', 'random', 'coverage'])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output must be a fresh directory')
    args.output.mkdir(parents=True)
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = 'unavailable'
    from .lab_replay import export_replay
    source_hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('artificial_scientist').glob('lab_*.py'))}
    summary = dict(variant=args.variant, seed=args.seed, proposal=args.proposal, source_commit=commit,
                   source_sha256=source_hashes, git_status=subprocess.check_output(['git','status','--porcelain'],text=True), policies={})
    for policy in dict.fromkeys(args.policies):
        trace = investigate(args.variant, policy, args.seed, args.output / policy, proposal=args.proposal)
        export_replay(trace, args.output / policy / 'replay.html')
        summary['policies'][policy] = dict(status=trace['status'], actions=len(trace['events']), training_cost=trace['training_cost'],
                                          formula=trace['selected_model']['formula'], search_cost=trace['search_cost'],
                                          metrics=trace.get('evaluation', {}).get('mean_squared_position_error'), cpu_seconds=trace['cpu_seconds'])
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
