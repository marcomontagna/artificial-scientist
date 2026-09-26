"""Bounded arithmetic programs. No eval, exec, generated Python or simulator imports."""
import itertools
import math
import time
from dataclasses import dataclass, field
from typing import Tuple

# AST: variable name or (operator, children...). All values are clamped to
# prevent unstable recursive predictions from consuming unbounded resources.
LIMIT = 1000.0
VARIABLES = ('v', 'u', 'lag_u', 'p', 'one')


def nodes(term, depth=0):
    if depth > 12:
        raise ValueError("expression nesting exceeds budget")
    if isinstance(term, str):
        if term not in VARIABLES:
            raise ValueError('unknown variable')
        return 1
    if not isinstance(term, tuple) or not term:
        raise ValueError('invalid expression')
    op, *args = term
    if op not in ('abs', 'positive', 'mul') or len(args) != (2 if op == 'mul' else 1):
        raise ValueError('invalid operator or arity')
    return 1 + sum(nodes(arg, depth + 1) for arg in args)


def value(term, variables):
    nodes(term)  # validates every externally supplied expression
    if isinstance(term, str):
        result = variables[term]
    elif term[0] == 'abs':
        result = abs(value(term[1], variables))
    elif term[0] == 'positive':
        result = max(0.0, value(term[1], variables))
    else:
        result = value(term[1], variables) * value(term[2], variables)
    if not math.isfinite(result):
        raise ValueError('non-finite program input')
    return max(-LIMIT, min(LIMIT, result))


def expression(term):
    if isinstance(term, str):
        return '1' if term == 'one' else term
    if term[0] == 'mul':
        return '(' + expression(term[1]) + '*' + expression(term[2]) + ')'
    return term[0] + '(' + expression(term[1]) + ')'


def grammar():
    """Composed terms, not complete simulator laws; deterministic search order."""
    terms = list(VARIABLES)
    terms += [(op, var) for op in ('abs', 'positive') for var in ('v', 'u', 'p')]
    terms += [('mul', a, b) for a, b in itertools.combinations_with_replacement(('v', 'u', 'p'), 2)]
    terms += [('mul', a, ('abs', a)) for a in ('v', 'u', 'p')]
    return tuple(terms)


def complexity(terms):
    # Fitted coefficient multiplication counts as two additional nodes.
    return sum(nodes(term) + 2 for term in terms) + max(0, len(terms) - 1)


def program_id(terms):
    return '+'.join(expression(t) for t in terms) or 'zero'


def velocity(previous):
    if previous is None or previous.action.kind == 'reset':
        return (0.0, 0.0)
    dt = previous.after.tick - previous.before.tick
    return ((previous.after.x - previous.before.x) / dt,
            (previous.after.y - previous.before.y) / dt)


def impulse(action):
    if action.kind != 'push':
        return (0.0, 0.0)
    return (action.magnitude * math.cos(action.angle), action.magnitude * math.sin(action.angle))


@dataclass
class Model:
    terms: Tuple
    coefficients: Tuple
    errors: list = field(default_factory=list)
    predictions: int = 0

    def __post_init__(self):
        if len(self.terms) > 2 or len(self.terms) != len(self.coefficients) or complexity(self.terms) > 12:
            raise ValueError('program exceeds declared grammar budget')
        for t in self.terms:
            nodes(t)
        if not all(math.isfinite(c) for c in self.coefficients):
            raise ValueError('non-finite coefficients')

    @property
    def id(self):
        return program_id(self.terms)

    @property
    def formula(self):
        rhs = ' + '.join('%.6g*%s' % (c, expression(t)) for c, t in zip(self.coefficients, self.terms)) or '0'
        return 'delta = ' + rhs + '; p_next = p + delta; v_next = delta (per axis)'

    def predict(self, observation, previous, action):
        return self.predict_state(observation, previous, action)[0]

    def predict_state(self, observation, previous, action, carried_velocity=None):
        if action.kind == 'reset':
            return ((0.0, 0.0), (0.0, 0.0))  # public reset contract
        pos = [observation.x, observation.y]
        vel = list(velocity(previous) if carried_velocity is None else carried_velocity)
        push = impulse(action)
        lag_push = impulse(previous.action) if previous is not None and previous.action.kind == 'push' else (0.0, 0.0)
        for tick in range(action.ticks if action.kind == 'wait' else 1):
            for axis in range(2):
                inputs = dict(p=pos[axis], v=vel[axis], u=push[axis] if tick == 0 else 0.0, lag_u=lag_push[axis] if tick == 0 else (push[axis] if tick == 1 else 0.0), one=1.0)
                delta = sum(c * value(t, inputs) for c, t in zip(self.coefficients, self.terms))
                delta = max(-LIMIT, min(LIMIT, delta))
                pos[axis] = max(-LIMIT, min(LIMIT, pos[axis] + delta))
                vel[axis] = delta
        return tuple(pos), tuple(vel)

    def record_error(self, error):
        self.predictions += 1
        self.errors.append(error)
        self.errors[:] = self.errors[-12:]

    def score(self):
        return (sum(self.errors) / len(self.errors) if self.errors else float('inf')) + 0.0001 * complexity(self.terms)

    def snapshot(self):
        return dict(id=self.id, formula=self.formula, coefficients=list(self.coefficients),
                    terms=self.terms, complexity=complexity(self.terms),
                    prequential_mse=sum(self.errors) / len(self.errors) if self.errors else None,
                    validated_predictions=self.predictions)


def training_rows(history):
    rows = []
    previous = None
    for transition in history:
        # Only consecutive one-tick observations furnish a one-tick velocity
        # proxy. A reset supplies v=0; a multi-tick average is not instantaneous.
        reliable_previous = previous is None or previous.action.kind == 'reset' or previous.after.tick - previous.before.tick == 1
        if transition.action.kind != 'reset' and transition.after.tick - transition.before.tick == 1 and reliable_previous:
            vel = velocity(previous)
            push = impulse(transition.action)
            for axis, key in enumerate(('x', 'y')):
                p = getattr(transition.before, key)
                lag = impulse(previous.action)[axis] if previous is not None and previous.action.kind == 'push' else 0.0
                rows.append((dict(p=p, v=vel[axis], u=push[axis], lag_u=lag, one=1.0), getattr(transition.after, key) - p))
        previous = transition
    return rows


def fit(terms, rows):
    if not terms or not rows:
        return tuple(0.0 for _ in terms)
    n = len(terms)
    matrix = [[0.0 for _ in range(n + 1)] for _ in range(n)]
    for inputs, target in rows:
        features = [value(t, inputs) for t in terms]
        for i in range(n):
            for j in range(n):
                matrix[i][j] += features[i] * features[j]
            matrix[i][n] += features[i] * target
    for i in range(n):
        matrix[i][i] += 1e-4
    for i in range(n):
        pivot = max(range(i, n), key=lambda j: abs(matrix[j][i]))
        matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
        divisor = matrix[i][i]
        if abs(divisor) < 1e-12:
            return tuple(0.0 for _ in terms)
        matrix[i] = [v / divisor for v in matrix[i]]
        for j in range(n):
            if i != j:
                factor = matrix[j][i]
                matrix[j] = [a - factor * b for a, b in zip(matrix[j], matrix[i])]
    return tuple(max(-10.0, min(10.0, matrix[i][n])) for i in range(n))


def propose(rows, excluded, count=2, deadline=float('inf')):
    terms = grammar()
    candidates = []
    for size in (1, 2):
        for chosen in itertools.combinations(terms, size):
            if time.process_time() >= deadline:
                raise TimeoutError('model search CPU cap')
            if complexity(chosen) > 12 or program_id(chosen) in excluded:
                continue
            coefficients = fit(chosen, rows)
            error = sum((sum(c * value(t, inputs) for c, t in zip(coefficients, chosen)) - target) ** 2 for inputs, target in rows) / max(1, len(rows))
            candidates.append((error + 0.0001 * complexity(chosen), program_id(chosen), chosen, coefficients))
    candidates.sort(key=lambda item: (item[0], item[1]))
    return [Model(item[2], item[3]) for item in candidates[:count]]
