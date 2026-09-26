"""Runtime investigator: receives public observations, never a world object."""
import hashlib
import json
import math
import random
from dataclasses import asdict
from .lab_api import Action, Transition
from .lab_guided import guided_propose
from .lab_models import Model, complexity, fit, propose, training_rows


def digest(record):
    return hashlib.sha256(json.dumps(record, sort_keys=True, allow_nan=False).encode()).hexdigest()


def actions():
    return tuple([Action('push', angle=a * math.pi / 2, magnitude=m)
                  for m in (0.3, 1.0) for a in range(4)] +
                 [Action('observe'), Action('wait', ticks=2), Action('wait', ticks=4), Action('reset')])


class Investigator:
    def __init__(self, initial, policy='active', seed=0, proposal='enumerate'):
        if policy not in ('active', 'random', 'coverage'):
            raise ValueError('unknown policy')
        if proposal not in ('enumerate', 'guided', 'guided-partial'):
            raise ValueError('unknown proposal mode')
        self.proposal = proposal
        self.residual_records = []
        self.residual_incumbent = None
        self.residual_epoch = 0
        self.escape_cursor = 0
        self.origins = {}
        self.search_cost = dict(candidate_fits=0, feature_evaluations=0, projection_feature_evaluations=0, projection_calls=0, refits=0)
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
        hypothesis_links = []
        prediction_by_id = {p['model_id']: p for p in chosen['predictions']}
        for ident, origin in self.origins.items():
            if ident not in prediction_by_id:
                continue
            base_prediction = prediction_by_id.get(origin['base_model_id'])
            prediction = prediction_by_id[ident]
            gap = None if base_prediction is None else (prediction['x']-base_prediction['x'])**2 + (prediction['y']-base_prediction['y'])**2
            without_scores = []
            for option in options:
                remaining_predictions = [p for p in option['predictions'] if p['model_id'] != ident]
                mass = sum(p['weight'] for p in remaining_predictions)
                mx = sum(p['weight']*p['x'] for p in remaining_predictions) / mass
                my = sum(p['weight']*p['y'] for p in remaining_predictions) / mass
                variance = sum(p['weight']*((p['x']-mx)**2+(p['y']-my)**2) for p in remaining_predictions) / mass
                without_scores.append((min(1.0,max(0.0,variance-2*noise))+option['coverage'])/Action(**option['action']).cost)
            without_index = max(range(len(options)), key=lambda i: (without_scores[i], -i)) if self.policy == 'active' and self.steps >= 4 else index
            hypothesis_links.append(dict(origin, model_id=ident, base_present=base_prediction is not None,
                                         selected_action_separation_squared=gap,
                                         action_without_model=options[without_index]['action'],
                                         changes_active_choice=without_index != index,
                                         counterfactual_scope='Remove this predictor, renormalize fixed weights; one decision only, no retraining.'))
        plan = dict(before=asdict(self.observation), action=chosen['action'], predictions=chosen['predictions'],
                    choice=dict(reason=reason, hypothesis_links=hypothesis_links, selected_score=chosen['score'], options=options,
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
        incumbent = self.final_model()
        if self.proposal != 'enumerate' and incumbent.id != self.residual_incumbent:
            self.residual_records = []
            self.residual_incumbent = incumbent.id
            self.residual_epoch += 1
        incumbent_prediction = next(p for p in self.pending['predictions'] if p['model_id'] == incumbent.id)
        previous_row_count = len(training_rows(self.history)) if self.proposal != 'enumerate' else 0
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
        if self.proposal != 'enumerate':
            for axis, (inputs, target) in zip(('x', 'y'), rows[previous_row_count:]):
                self.residual_records.append(dict(step=self.steps-1, axis=axis, inputs=inputs,
                    model_id=incumbent.id, incumbent_epoch=self.residual_epoch, coefficient_version=incumbent_prediction['coefficients'],
                    residual=getattr(outcome, axis)-incumbent_prediction[axis],
                    prediction=incumbent_prediction[axis], observed=getattr(outcome, axis)))
        updated = []
        for model in self.models:
            self.search_cost['refits'] += 1
            coefficients = fit(model.terms, rows)
            if coefficients != model.coefficients:
                updated.append(dict(model_id=model.id, before=list(model.coefficients), after=list(coefficients)))
                model.coefficients = coefficients
        added, removed = [], []
        search = dict(mode=self.proposal, candidate_fits=0, feature_evaluations=0, projection_feature_evaluations=0, projection_calls=0)
        noise = sum(self.home_noise) / len(self.home_noise)
        best_latest = next((e['squared_error'] for e in errors if prior_best and e['model_id'] == prior_best.id), 0.0)
        surprise = prior_error is not None and best_latest > max(4 * prior_error, 8 * noise, 1e-4)
        trigger = 'prediction_failure' if surprise else 'scheduled_search'
        if (self.steps % 4 == 0 or surprise) and self.steps - self.last_proposal_step >= 2 and len(rows) >= 4:
            try:
                if self.proposal != 'enumerate':
                    new, self.escape_cursor = guided_propose(rows, self.seen_structures, incumbent,
                        self.residual_records, self.escape_cursor, deadline=deadline, audit=search, partial=self.proposal == 'guided-partial')
                else:
                    new = propose(rows, self.seen_structures, deadline=deadline, audit=search)
            except TimeoutError:
                for key in ('candidate_fits', 'feature_evaluations', 'projection_feature_evaluations', 'projection_calls'):
                    self.search_cost[key] += search[key]
                self.pending = None
                return errors, dict(added=[], removed=[], updated=updated, trigger=trigger, search=search, incomplete='proposal search CPU cap')
            for key in ('candidate_fits', 'feature_evaluations', 'projection_feature_evaluations', 'projection_calls'):
                self.search_cost[key] += search[key]
            if self.proposal != 'enumerate':
                for record in search['candidates']:
                    if record['selected']:
                        self.origins[record['model_id']] = dict(proposed_after_step=self.steps-1, base_model_id=incumbent.id, feature=record['feature'], origin=record['origin'])
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
        return errors, dict(added=added, removed=removed, updated=updated, trigger=trigger if added else 'coefficient_update', surprise=surprise, search=search)

    def final_model(self):
        eligible = [m for m in self.models if len(m.errors) >= 3]
        if not eligible:
            return self.models[0]
        common = min(len(m.errors) for m in eligible)
        return min(eligible, key=lambda m: (sum(m.errors[-common:]) / common + 0.0001 * complexity(m.terms), m.id))
