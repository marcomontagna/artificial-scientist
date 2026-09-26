"""Bounded assumption revision; only public observations and action history."""
import json
import math
import random
from dataclasses import asdict

from .lab_api import Action, Transition
from .revision_models import VectorModel, fit_model, propose


def experiments():
    return tuple([(Action('push', angle=i*math.pi/2, magnitude=m), Action('observe'))
                  for m in (.3, 1.0) for i in range(4)] + [(Action('observe'), Action('observe'))])


def clone(value):
    return json.loads(json.dumps(value, allow_nan=False))


class RevisionInvestigator:
    def __init__(self, initial, policy='active', seed=0, check_rule='original', proposal_mode='ordinary'):
        if policy not in ('active', 'random', 'coverage', 'no-revision'):
            raise ValueError('unknown revision policy')
        if check_rule not in ('original', 'pooled', 'confirm_short', 'confirm_long'):
            raise ValueError('unknown check rule')
        if proposal_mode not in ('ordinary', 'history'):
            raise ValueError('unknown proposal mode')
        self.proposal_mode = proposal_mode
        self.check_rule = check_rule
        self.policy = policy
        self.rng = random.Random(seed)
        self.observation = initial
        self.history = []
        self.incumbent = VectorModel(('v', 'u'), True, (0.0, 0.0))
        self.noise = max(1e-4, (initial.x**2 + initial.y**2)/2)
        self.threshold = max(.0025, 12*self.noise)
        self.visits = [0]*9
        self.steps = 0
        self.recent = []
        self.last_check_end = -100
        self.cycle = None
        self.cycles = []
        self.pending = None
        self.work = dict(candidate_fits=0, refits=0, feature_evaluations=0)

    def plan(self, remaining):
        if self.pending is not None:
            raise RuntimeError('pending experiment must finish first')
        if remaining < 2:
            raise ValueError('experiment needs two tool units')
        models = self.cycle['models'] if self.cycle else [self.incumbent]
        options = []
        for index, sequence in enumerate(experiments()):
            predictions = [{'model_id':m.id, 'tape':m.predict_tape(self.observation, self.history, sequence)} for m in models]
            variance = 0.0
            for k in range(2):
                mx = sum(p['tape'][k][0] for p in predictions)/len(models)
                my = sum(p['tape'][k][1] for p in predictions)/len(models)
                variance += sum((p['tape'][k][0]-mx)**2+(p['tape'][k][1]-my)**2 for p in predictions)/len(models)/2
            coverage = .02/(1+self.visits[index])
            options.append(dict(index=index, actions=[asdict(a) for a in sequence], predictions=predictions,
                                disagreement=variance, coverage=coverage,
                                score=(min(1.0,max(0.0,variance-2*self.noise))+coverage)/2))
        if self.steps < 6 or self.policy in ('coverage', 'no-revision') or (self.policy == 'active' and self.cycle is None):
            index = max(range(9), key=lambda i:(options[i]['coverage'], -i))
            reason = 'coverage warmup' if self.steps < 6 else 'coverage'
        elif self.policy == 'random':
            index = self.rng.randrange(9); reason = 'uniform experiment sampling'
        else:
            index = max(range(9), key=lambda i:(options[i]['score'], -i))
            reason = 'frozen-model disagreement above assumed noise plus coverage per cost'
        confirmation = self.cycle.get('confirmation_plan') if self.cycle else None
        offset = 2*(len(self.cycle['check_steps'])-4) if confirmation else None
        chosen_predictions = options[index]['predictions']
        prediction_origin = 'current_observed_start'
        if confirmation:
            index = confirmation['experiment_indexes'][offset//2]
            chosen_predictions = options[index]['predictions']
            reason = 'precommitted coverage confirmation; outcomes cannot change suffix actions'
            if self.check_rule == 'confirm_long':
                chosen_predictions = [dict(model_id=p['model_id'], tape=p['tape'][offset:offset+2])
                                      for p in confirmation['predictions']]
                prediction_origin = 'confirmation_start_frozen_tape'
        self.pending = clone(dict(step=self.steps, before=asdict(self.observation),
            phase='check' if self.cycle else 'explore', cycle_id=self.cycle['id'] if self.cycle else None,
            incumbent_id=self.incumbent.id, models=[m.snapshot() for m in models],
            chosen=index, actions=options[index]['actions'], predictions=chosen_predictions,
            options=options, reason=reason, failure_threshold=self.threshold, home_variance=self.noise,
            proposal_mode=self.proposal_mode, check_rule=self.check_rule, check_stage=('confirmation' if confirmation else 'screening') if self.cycle else 'explore',
            confirmation_plan=confirmation, confirmation_offset=offset,
            prediction_origin=prediction_origin, option_prediction_origin='current_observed_start'))
        return clone(self.pending)

    def accept(self, outcomes, deadline=float('inf')):
        self._partial = None
        try:
            return self._accept(outcomes, deadline)
        except TimeoutError as exc:
            if self._partial is None:
                raise
            result = clone(self._partial)
            result.update(incomplete=str(exc), incumbent_after=self.incumbent.snapshot())
            self.pending=None
            return result

    def _accept(self, outcomes, deadline=float('inf')):
        if self.pending is None or len(outcomes) != 2:
            raise ValueError('two outcomes required for pending experiment')
        actions = [Action(**a) for a in self.pending['actions']]
        before = self.observation
        for action, outcome in zip(actions, outcomes):
            if outcome.tick != before.tick + action.cost:
                raise ValueError('outcome timing does not match experiment')
            before = outcome
        position_losses = {p['model_id']:[(xy[0]-o.x)**2+(xy[1]-o.y)**2
                           for xy,o in zip(p['tape'], outcomes)] for p in self.pending['predictions']}
        losses = {ident:sum(values)/2 for ident,values in position_losses.items()}
        self._partial = dict(losses=losses, revision=None)
        before = self.observation
        for action, outcome in zip(actions, outcomes):
            self.history.append(Transition(before, action, outcome)); before = outcome
        self.observation = outcomes[-1]
        self.visits[self.pending['chosen']] += 1
        self.steps += 1
        change = None
        if self.cycle:
            for ident, error in losses.items():
                self.cycle['losses'][ident].append(error)
            self.cycle.setdefault('position_losses', {m.id:[] for m in self.cycle['models']})
            for ident, values in position_losses.items():
                self.cycle['position_losses'][ident].extend(values)
            self.cycle['check_steps'].append(self.steps-1)
            if self.check_rule != 'original':
                if len(self.cycle['check_steps']) == 4:
                    self._prepare_confirmation()
                    change = dict(screening_complete=True, cycle_id=self.cycle['id'],
                                  screening=clone(self.cycle['screening']),
                                  confirmation_plan=clone(self.cycle['confirmation_plan']))
                    self._partial['revision'] = clone(change)
                elif len(self.cycle['check_steps']) == 8:
                    change = self._finish_confirmation(deadline)
            elif len(self.cycle['check_steps']) == 4:
                means = {k:sum(v)/len(v) for k,v in self.cycle['losses'].items()}
                incumbent = self.cycle['models'][0]
                alternatives = self.cycle['models'][1:]
                best = min(alternatives, key=lambda m:(means[m.id], m.id))
                margin = max(.15*means[incumbent.id], .0001*max(1,best.parameter_count-incumbent.parameter_count))
                accepted = means[incumbent.id]-means[best.id] > margin
                self.incumbent = best if accepted else incumbent
                record = dict(id=self.cycle['id'], trigger=self.cycle['trigger'], models=self.cycle['snapshots'],
                    proposal_audit=self.cycle['audit'], check_steps=self.cycle['check_steps'],
                    mean_squared_error=means, incumbent_id=incumbent.id, best_alternative=best.id,
                    required_margin=margin, accepted=accepted, selected_id=self.incumbent.id,
                    decision_before_refit=True, frozen_through_history_length=len(self.history),
                    check_rule=self.check_rule, position_losses=clone(self.cycle['position_losses']))
                self._partial['revision'] = clone(record)
                self.cycles.append(clone(record)); change = clone(record)
                self.cycle = None; self.recent=[]; self.last_check_end=self.steps
                self._refit(deadline)
        else:
            self.recent = (self.recent+[losses[self.incumbent.id]])[-5:]
            self._refit(deadline)
            enough = len(self.recent)==5 and sum(e>self.threshold for e in self.recent)>=3
            if (self.policy!='no-revision' and self.steps>=6 and enough and len(self.cycles)<2
                    and self.steps-self.last_check_end>=6 and 80-2*self.steps>=(8 if self.check_rule=='original' else 16)):
                trigger = dict(after_step=self.steps-1, history_length=len(self.history),
                               recent_errors=list(self.recent), threshold=self.threshold)
                audit={}
                self._partial['revision'] = dict(trigger=trigger, proposal_audit=audit, incomplete='proposal search')
                try:
                    if self.proposal_mode == 'history':
                        candidates, audit = propose(self.incumbent, self.history, deadline=deadline, audit=audit, proposal_mode='history')
                    else:
                        candidates, audit = propose(self.incumbent, self.history, deadline=deadline, audit=audit)
                finally:
                    self.work['candidate_fits'] += audit.get('candidate_fits',0)
                    self.work['feature_evaluations'] += audit.get('feature_evaluations',0)
                if candidates:
                    models=[self.incumbent]+candidates
                    self.cycle=dict(id=len(self.cycles), models=models, snapshots=[m.snapshot() for m in models],
                        trigger=trigger, audit=audit, losses={m.id:[] for m in models}, check_steps=[])
                    change=dict(started_cycle=len(self.cycles), trigger=trigger, models=self.cycle['snapshots'], proposal_audit=audit)
                else:
                    change=dict(id=len(self.cycles), trigger=trigger, accepted=False, reason='no new candidates', proposal_audit=audit, models=[])
                    self.cycles.append(clone(change));self.last_check_end=self.steps;self.recent=[]
        self.pending=None
        return dict(losses=losses, revision=change, incumbent_after=self.incumbent.snapshot())

    @staticmethod
    def _margin(incumbent, alternative, means):
        return max(.15*means[incumbent.id],
                   .0001*max(1,alternative.parameter_count-incumbent.parameter_count))

    def _prepare_confirmation(self):
        """Freeze the screening winner and all eight future actions before use."""
        cycle = self.cycle
        means = {k:sum(v)/len(v) for k,v in cycle['losses'].items()}
        incumbent = cycle['models'][0]
        winner = min(cycle['models'][1:], key=lambda m:(means[m.id],m.id))
        margin = self._margin(incumbent,winner,means)
        cycle['screening'] = dict(winner_id=winner.id, mean_squared_error=means,
            required_margin=margin, passed=means[incumbent.id]-means[winner.id]>margin,
            position_losses=clone(cycle['position_losses']))
        visits = list(self.visits)
        indexes = []
        for _ in range(4):
            index = min(range(9),key=lambda i:(visits[i],i))
            indexes.append(index);visits[index]+=1
        actions = tuple(a for index in indexes for a in experiments()[index])
        cycle['confirmation_plan'] = clone(dict(
            start=asdict(self.observation), history_length=len(self.history),
            previous_transition=asdict(self.history[-1]) if self.history else None,
            visits_before=list(self.visits), visits_after_virtual=visits,
            experiment_indexes=indexes, actions=[asdict(a) for a in actions],
            models=[m.snapshot() for m in cycle['models']],
            predictions=[dict(model_id=m.id,tape=m.predict_tape(self.observation,self.history,actions))
                         for m in cycle['models']],
            interpretation='fixed actions; full tape is scored only by confirm_long'))

    def _finish_confirmation(self, deadline):
        cycle = self.cycle
        incumbent = cycle['models'][0]
        pooled = {k:sum(v)/len(v) for k,v in cycle['losses'].items()}
        suffix = {k:sum(v[4:])/4 for k,v in cycle['losses'].items()}
        if self.check_rule == 'pooled':
            winner = min(cycle['models'][1:],key=lambda m:(pooled[m.id],m.id))
            decision_means = pooled
        else:
            winner = next(m for m in cycle['models'] if m.id==cycle['screening']['winner_id'])
            decision_means = suffix
        margin = self._margin(incumbent,winner,decision_means)
        passed = decision_means[incumbent.id]-decision_means[winner.id]>margin
        accepted = passed and (self.check_rule=='pooled' or cycle['screening']['passed'])
        self.incumbent = winner if accepted else incumbent
        record = dict(id=cycle['id'],trigger=cycle['trigger'],models=cycle['snapshots'],
            proposal_audit=cycle['audit'],check_steps=cycle['check_steps'],
            check_rule=self.check_rule,mean_squared_error=decision_means,
            pooled_mean_squared_error=pooled,confirmation_mean_squared_error=suffix,
            screening=cycle['screening'],confirmation_plan=cycle['confirmation_plan'],
            position_losses=cycle['position_losses'],
            confirmation_position_losses={k:v[8:] for k,v in cycle['position_losses'].items()},
            incumbent_id=incumbent.id,best_alternative=winner.id,
            required_margin=margin,decision_batch_passed=passed,
            confirmation_required_margin=self._margin(incumbent,winner,suffix),
            confirmation_passed=suffix[incumbent.id]-suffix[winner.id]>self._margin(incumbent,winner,suffix),
            accepted=accepted,selected_id=self.incumbent.id,decision_before_refit=True,
            frozen_through_history_length=len(self.history))
        self._partial['revision'] = clone(record)
        self.cycles.append(clone(record))
        self.cycle=None;self.recent=[];self.last_check_end=self.steps
        self._refit(deadline)
        return clone(record)

    def _refit(self, deadline):
        audit={}
        try:
            self.incumbent = fit_model(self.incumbent, self.history, deadline=deadline, audit=audit)
        finally:
            self.work['refits'] += audit.get('candidate_fits',0)
            self.work['feature_evaluations'] += audit.get('feature_evaluations',0)

    def explanation_status(self):
        if self.cycle:
            return 'incomplete_check'
        if len(self.recent)<5:
            return 'insufficient_recent_evidence'
        return 'unresolved' if sum(e>self.threshold for e in self.recent)>=3 else 'no_recent_failure_detected'
