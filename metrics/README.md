# Metrics

Implemented in `artificial_scientist/metrics.py`: binary Brier score `(p-y)^2` and natural-log loss. Lower is better. For finite artifact values, log loss clips p to [1e-12, 1-1e-12]; Brier uses the original p. Reject invalid probabilities and outcomes. Score before observing/updating on the target.

Smoke summaries contain each seed, baseline and pre/post-change phase, sample count and mean scores. Full predictions support later diagnostics. This tiny run does not estimate calibration, confidence intervals or recovery time. Preregister reliability bins/counts, uncertainty, recovery criterion, intervention cost and sample-efficiency analyses for the selected experiment; never infer calibration from average loss alone.
