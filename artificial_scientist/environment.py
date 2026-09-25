"""Evaluator-owned hidden-law binary environment."""
import random


class SwitchingBernoulli:
    def __init__(self, seed, before, after, change_at):
        if not before or len(before) != len(after):
            raise ValueError("law vectors must have matching nonzero length")
        if any(not 0 <= p <= 1 for p in (*before, *after)):
            raise ValueError("probabilities must lie in [0, 1]")
        if not isinstance(change_at, int) or change_at < 0:
            raise ValueError("change_at must be a nonnegative integer")
        self._rng = random.Random(seed)
        self._before, self._after = tuple(before), tuple(after)
        self._change_at = change_at
        self._step = 0

    def step(self, action):
        if not isinstance(action, int) or not 0 <= action < len(self._before):
            raise ValueError("invalid action")
        law = self._before if self._step < self._change_at else self._after
        outcome = int(self._rng.random() < law[action])
        self._step += 1
        return outcome
