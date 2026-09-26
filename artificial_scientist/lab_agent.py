"""Runtime investigator: receives public observations, never a world object."""
import hashlib
import json
import math
import random
from dataclasses import asdict
from .lab_api import Action, Transition
from .lab_models import Model, complexity, fit, propose, training_rows


def digest(record):
    return hashlib.sha256(json.dumps(record, sort_keys=True, allow_nan=False).encode()).hexdigest()


def actions():
    return tuple([Action('push', angle=a * math.pi / 2, magnitude=m)
                  for m in (0.3, 1.0) for a in range(4)] +
                 [Action('observe'), Action('wait', ticks=2), Action('wait', ticks=4), Action('reset')])


class Investigator:
    def __init__(self, initial, policy='active', seed=0):
        if policy not in ('active', 'random', 'coverage'):
            raise ValueError('unknown policy')
        self.policy = policy
        self.rng = random.Random(seed)
        self.observation = initial
        self.history = []
        self.models = [Model((), ()), Model(('v',), (1.0,))]
        self.visits = {}
        self.steps = 0
        self.pending = None
        self.seen_structures = {m.id for m in self.models}
        self.last_proposal_step = 0
        # Home is public (0,0), initially at rest. Constant independent sensor
        # noise is an explicit working assumption, NOT inferred from residuals.
        self.home_noise = [(initial.x ** 2 + initial.y ** 2) / 2]

    def plan(self, remaining):
        if self.pending is not None:
            raise RuntimeError('outcome required before planning again')
        previous = self.history[-1] if self.history else None
        options = []
        mature = [m for m in self.models if len(m.errors) >= 3]
        common = min((len(m.errors) for m in mature), default=0)
        evidence = {m.id: sum(m.errors[-common:]) / common for m in mature} if common else {}
        best_error = min(evidence.values(), default=0.0)
        noise = sum(self.home_noise) / len(self.home_noise)
        scale = max(2 * noise, best_error, 1e-6)
        raw_weights = [math.exp(-min(50.0, (evidence[m.id] - best_error) / scale)) if m.id in evidence else (0.25 if mature else 1.0) for m in self.models]
        weights = [w / sum(raw_weights) for w in raw_weights]
        for action in actions():
            if action.cost > remaining:
                continue
            predictions = [dict(model_id=m.id, formula=m.formula, coefficients=list(m.coefficients),
                                weight=weights[index], x=m.predict(self.observation, previous, action)[0],
                                y=m.predict(self.observation, previous, action)[1]) for index, m in enumerate(self.models)]
            mean_x = sum(p['weight'] * p['x'] for p in predictions)
            mean_y = sum(p['weight'] * p['y'] for p in predictions)
            disagreement = sum(p['weight'] * ((p['x'] - mean_x) ** 2 + (p['y'] - mean_y) ** 2) for p in predictions)
            key = json.dumps(asdict(action), sort_keys=True)
            coverage = 0.02 / (1 + self.visits.get(key, 0))
            # Weight caps avoid letting an unstable model monopolize exploration.
            score = (min(1.0, max(0.0, disagreement - 2 * noise)) + coverage) / action.cost
            options.append(dict(action=asdict(action), score=score, disagreement=disagreement,
                                coverage=coverage, predictions=predictions))
        if not options:
            raise ValueError('no affordable action')
        if self.policy == 'random':
            index = self.rng.randrange(len(options)); reason = 'uniform among affordable tools'
        elif self.policy == 'coverage' or self.steps < 4:
            index = max(range(len(options)), key=lambda i: (options[i]['coverage'] / Action(**options[i]['action']).cost, -i))
            reason = 'coverage policy' if self.policy == 'coverage' else 'four-action coverage warmup'
        else:
            index = max(range(len(options)), key=lambda i: (options[i]['score'], -i))
            reason = 'committee disagreement above provisional home-noise estimate plus coverage, per cost'
        chosen = options[index]
        plan = dict(before=asdict(self.observation), action=chosen['action'], predictions=chosen['predictions'],
                    choice=dict(reason=reason, selected_score=chosen['score'], options=options,
                                sensor_noise_variance_estimate=noise, home_readings=len(self.home_noise),
                                noise_limit='Few known-home readings; assumes stationary independent sensor noise. Model error remains unresolved.'))
        self.pending = json.loads(json.dumps(plan))  # no mutable alias across boundary
        return json.loads(json.dumps(plan))

    def accept(self, action, outcome, deadline=float('inf')):
        if self.pending is None or asdict(action) != self.pending['action']:
            raise RuntimeError('outcome does not match pending action')
        if outcome.tick != self.observation.tick + action.cost:
            raise ValueError('outcome timing violates public contract')
        errors = []
        mature = [m for m in self.models if len(m.errors) >= 3]
        prior_best = self.final_model() if mature else None
        prior_error = sum(prior_best.errors) / len(prior_best.errors) if prior_best else None
        for m, p in zip(self.models, self.pending['predictions']):
            error = (outcome.x - p['x']) ** 2 + (outcome.y - p['y']) ** 2
            m.record_error(error)
            errors.append(dict(model_id=m.id, squared_error=error))
        self.history.append(Transition(self.observation, action, outcome))
        self.observation = outcome
        self.steps += 1
        key = json.dumps(asdict(action), sort_keys=True)
        self.visits[key] = self.visits.get(key, 0) + 1
        if action.kind == 'reset':
            self.home_noise.append((outcome.x ** 2 + outcome.y ** 2) / 2)
        rows = training_rows(self.history)
        updated = []
        for model in self.models:
            coefficients = fit(model.terms, rows)
            if coefficients != model.coefficients:
                updated.append(dict(model_id=model.id, before=list(model.coefficients), after=list(coefficients)))
                model.coefficients = coefficients
        added, removed = [], []
        noise = sum(self.home_noise) / len(self.home_noise)
        best_latest = next((e['squared_error'] for e in errors if prior_best and e['model_id'] == prior_best.id), 0.0)
        surprise = prior_error is not None and best_latest > max(4 * prior_error, 8 * noise, 1e-4)
        trigger = 'prediction_failure' if surprise else 'scheduled_search'
        if (self.steps % 4 == 0 or surprise) and self.steps - self.last_proposal_step >= 2 and len(rows) >= 4:
            try:
                new = propose(rows, self.seen_structures, deadline=deadline)
            except TimeoutError:
                self.pending = None
                return errors, dict(added=[], removed=[], updated=updated, trigger=trigger, incomplete='proposal search CPU cap')
            # Every live model made the same most recent events. Rank only on
            # that common window, never compare a new fit to past predictions.
            common = min(len(m.errors) for m in self.models)
            ranked = sorted(self.models, key=lambda m: (sum(m.errors[-common:]) / common + 0.0001 * complexity(m.terms), m.id))
            retained = ranked[:8-len(new)]
            self.seen_structures.update(m.id for m in new)
            self.last_proposal_step = self.steps
            removed = [m.id for m in self.models if m not in retained]
            self.models = retained + new
            added = [m.snapshot() for m in new]
        self.pending = None
        return errors, dict(added=added, removed=removed, updated=updated, trigger=trigger if added else 'coefficient_update', surprise=surprise)

    def final_model(self):
        eligible = [m for m in self.models if len(m.errors) >= 3]
        if not eligible:
            return self.models[0]
        common = min(len(m.errors) for m in eligible)
        return min(eligible, key=lambda m: (sum(m.errors[-common:]) / common + 0.0001 * complexity(m.terms), m.id))
