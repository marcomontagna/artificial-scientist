"""Public, simulator-independent tool records for the investigation laboratory.

Validation failures are rejected commands, not executed experiments: they do
not consume time, budget, or noise draws. Angles are radians. Only wait uses
``ticks``; reset has a fixed eight-tick cost despite its default ticks field.
"""
from dataclasses import dataclass
import math


def _finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


@dataclass(frozen=True)
class Action:
    kind: str
    angle: float = 0.0
    magnitude: float = 0.0
    ticks: int = 1

    def __post_init__(self):
        self.validate()

    def validate(self):
        if type(self.kind) is not str or self.kind not in ('observe', 'push', 'wait', 'reset'):
            raise ValueError('unknown tool')
        if not _finite_number(self.angle) or not _finite_number(self.magnitude):
            raise ValueError('angle and magnitude must be finite numbers')
        if type(self.ticks) is not int:
            raise ValueError('ticks must be an integer')
        if self.kind == 'wait':
            if not 1 <= self.ticks <= 8:
                raise ValueError('wait ticks must be between 1 and 8')
        elif self.ticks != 1:
            raise ValueError('only wait accepts nondefault ticks')
        if self.kind == 'push':
            if not 0 <= self.magnitude <= 1:
                raise ValueError('push magnitude must be between 0 and 1')
        elif self.angle != 0 or self.magnitude != 0:
            raise ValueError('only push accepts angle or magnitude')

    @property
    def cost(self):
        self.validate()
        return 8 if self.kind == 'reset' else self.ticks


@dataclass(frozen=True)
class Observation:
    tick: int
    x: float
    y: float


@dataclass(frozen=True)
class Transition:
    before: Observation
    action: Action
    after: Observation
