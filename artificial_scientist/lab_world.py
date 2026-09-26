"""Evaluator-owned motion worlds. Never import this module into the learner.

World laws are deliberately explicit here for source review, not runtime learner
inputs. Python object privacy is not a security sandbox: the coordinator must
pass only lab_api observations/actions across the learner boundary.
"""
import math
import random

from .lab_api import Action, Observation


class _World:
    def __init__(self, seed, variant):
        if type(seed) is not int:
            raise ValueError('seed must be an integer')
        if variant not in ('development', 'challenge', 'noise'):
            raise ValueError('unknown evaluator world')
        self._variant = variant
        self._noise = random.Random(seed)
        self._tick = self._consumed = 0
        self._x = self._y = self._vx = self._vy = 0.0
        self._initial = self._reading()

    @property
    def initial(self):
        return self._initial

    @property
    def consumed(self):
        return self._consumed

    def _reading(self):
        sigma = 0.25 if self._variant == 'noise' else 0.01
        return Observation(self._tick, self._x + self._noise.gauss(0, sigma),
                           self._y + self._noise.gauss(0, sigma))

    def _advance(self, ux, uy):
        if self._variant == 'noise':
            # An intentionally uninformative sensor process; inputs have no effect.
            self._x = self._y = self._vx = self._vy = 0.0
            return
        if self._variant == 'development':
            self._vx = 0.82 * self._vx + 0.42 * ux
            self._vy = 0.82 * self._vy + 0.42 * uy
        else:
            # Independently specified challenge: speed-dependent drag and a
            # direction-dependent actuator response, fixed for the entire run.
            drag = 0.88 / (1 + 0.3 * math.hypot(self._vx, self._vy))
            self._vx = drag * self._vx + 0.36 * ux + 0.10 * uy
            self._vy = drag * self._vy + 0.24 * uy
        self._x += self._vx
        self._y += self._vy

    def step(self, action):
        if type(action) is not Action:
            raise ValueError('step requires a public Action')
        action.validate()
        cost = action.cost
        if self._consumed + cost > 80:
            raise ValueError('tool budget exhausted')
        ux = action.magnitude * math.cos(action.angle) if action.kind == 'push' else 0.0
        uy = action.magnitude * math.sin(action.angle) if action.kind == 'push' else 0.0
        # Every elapsed tick consumes a noise pair, including unobserved waits.
        # Thus batching observations does not change the physical/noise timeline.
        for index in range(cost):
            if action.kind == 'reset':
                self._x = self._y = self._vx = self._vy = 0.0
            else:
                self._advance(ux if index == 0 else 0.0, uy if index == 0 else 0.0)
            self._tick += 1
            self._consumed += 1
            observation = self._reading()
        return observation


def make_world(seed: int, variant: str = 'development'):
    """Return an evaluator-owned world with initial/step and an 80-unit budget.

    Seeds control sensor noise only; reset preserves the RNG and hidden law.
    Reading initial repeatedly neither advances time nor provides new samples.
    A push applies its input once, then advances one tick. Reset occupies eight
    ticks held at home with zero velocity and returns the final noisy reading.
    """
    return _World(seed, variant)
