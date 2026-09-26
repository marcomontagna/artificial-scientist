"""Evaluator-owned revision challenges, independently authored before tuning.

The learner must never receive this module, a world object, or variant labels.
The inherited tool contract is identical to the frozen first laboratory.
"""
from collections import deque

from .lab_world import _World, make_world


class _RevisionWorld(_World):
    def __init__(self, seed, variant):
        self._revision_variant = variant
        self._pending = deque([(0.0, 0.0)] * 11)
        # Inherit the development sensor process and all public tool semantics.
        super().__init__(seed, 'development')

    def _advance(self, ux, uy):
        vx, vy = self._vx, self._vy
        if self._revision_variant == 'challenge':
            # A fixed, damped momentum coupling; simultaneous updates matter.
            self._vx = 0.72 * vx - 0.18 * vy + 0.38 * ux
            self._vy = 0.22 * vx + 0.65 * vy + 0.38 * uy
        else:
            # A delayed actuator, not a law switch or world-ID-dependent hint.
            dx, dy = self._pending.popleft()
            self._pending.append((ux, uy))
            self._vx = 0.65 * vx + 0.30 * ux - 0.22 * dy
            self._vy = 0.65 * vy + 0.30 * uy + 0.22 * dx
        self._x += self._vx
        self._y += self._vy

    def step(self, action):
        # The superclass validates and checks budget before any mutation. Clear
        # latent actuator state only after a successful reset, never on rejection.
        observation = super().step(action)
        if action.kind == 'reset':
            self._pending.clear()
            self._pending.extend([(0.0, 0.0)] * 11)
        return observation


def make_revision_world(seed: int, variant: str = 'control'):
    """Return a world with initial, step(Action), consumed and an 80-unit cap.

    Noise is seeded and not rewound on reset. All latent physical state is
    rehomed by reset; global time and accumulated cost continue. Variants are
    evaluator labels, never learner observations. No learner execution occurs.
    """
    if type(seed) is not int:
        raise ValueError('seed must be an integer')
    if type(variant) is not str or variant not in ('control', 'challenge', 'stress'):
        raise ValueError('unknown evaluator world')
    if variant == 'control':
        return make_world(seed, 'development')
    return _RevisionWorld(seed, variant)
