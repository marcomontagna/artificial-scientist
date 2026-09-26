"""Independently authored evaluator laws sealed after the learner was frozen.

Never import into learner code or expose labels, state, or coefficients through
observations. Reuses the original public tools and seeded sensor process.
"""
from collections import deque

from .lab_world import _World


class _TransferWorld(_World):
    def __init__(self, seed, variant):
        self._transfer_variant = variant
        self._inputs = deque([(0.0, 0.0)] * 16, maxlen=16)
        super().__init__(seed, 'development')

    def _advance(self, ux, uy):
        vx, vy = self._vx, self._vy
        if self._transfer_variant == 'transfer_a':
            own_delay = self._inputs[-3]
            cross_delay = self._inputs[-6]
            self._vx = 0.58*vx + 0.31*ux + 0.18*own_delay[0] + 0.25*cross_delay[1]
            self._vy = 0.74*vy + 0.43*uy - 0.23*own_delay[1] + 0.17*cross_delay[0]
        else:
            own_delay = self._inputs[-4]
            cross_delay = self._inputs[-9]
            self._vx = 0.54*vx + 0.16*vy + 0.27*ux + 0.24*own_delay[0] - 0.21*cross_delay[1]
            self._vy = 0.61*vy - 0.12*vx + 0.34*uy - 0.19*own_delay[1] + 0.26*cross_delay[0]
        self._inputs.append((ux, uy))
        self._x += self._vx
        self._y += self._vy

    def step(self, action):
        # Superclass rejects invalid/over-budget commands before mutation.
        observation = super().step(action)
        if action.kind == 'reset':
            self._inputs.clear()
            self._inputs.extend([(0.0, 0.0)] * 16)
        return observation


def make_transfer_world(seed: int, variant: str = 'transfer_a'):
    """Evaluator factory; immutable public observations and unchanged 80 cap."""
    if type(seed) is not int:
        raise ValueError('seed must be an integer')
    if type(variant) is not str or variant not in ('transfer_a', 'transfer_b'):
        raise ValueError('unknown transfer world')
    return _TransferWorld(seed, variant)
