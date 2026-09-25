"""Proper binary prediction scores; lower is better."""
import math


def scores(probability, outcome):
    if not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("finite probability in [0, 1] required")
    if outcome not in (0, 1):
        raise ValueError("binary outcome required")
    p = min(1 - 1e-12, max(1e-12, probability))
    return {"brier": (probability - outcome) ** 2,
            "log_loss": -math.log(p if outcome else 1 - p)}
