"""Predictors receive actions and outcomes, never evaluator law metadata."""
from collections import deque


class Constant:
    def predict(self, action):
        return 0.5

    def update(self, action, outcome):
        pass


class BetaBernoulli:
    def __init__(self, n_actions, window=None):
        if n_actions < 1 or (window is not None and window < 1):
            raise ValueError("positive action count and window required")
        self.window = window
        self.history = [deque() for _ in range(n_actions)]
        self.successes = [0] * n_actions
        self.counts = [0] * n_actions

    def predict(self, action):
        return (self.successes[action] + 1) / (self.counts[action] + 2)

    def update(self, action, outcome):
        if outcome not in (0, 1):
            raise ValueError("binary outcome required")
        if self.window is not None:
            history = self.history[action]
            if len(history) == self.window:
                self.successes[action] -= history.popleft()
                self.counts[action] -= 1
            history.append(outcome)
        self.successes[action] += outcome
        self.counts[action] += 1
