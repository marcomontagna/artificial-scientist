# Recreated selector review probes

Status: Code and note independently reviewed by the root Codex coordinator; full probe run completed by the coordinator; see [response and results](selector_review_response.md). Author: Codex research worker. Root smoke checks matched existing seed-0 structural-lag-2 means within 1e-12 and matched the return-world prefix exactly. This script recreates the described probes in sections 2.1–2.4 of `claude_independent_review.md`; it is not Claude's original scratch script and reported numerical findings agree at the original review’s displayed precision after execution and comparison.

Run from the repository root:

```sh
python3 -m experiments.selector_review_probes --output results/runs/selector_review_recreated_01
```

The output directory must be fresh, directly beneath `results/runs`, and start with `selector_review_`. Standard library only; one process; internal 540-second deadline checked every tick; 20 MB artifact cap. Source files and settings are hashed, Git revision/worktree state and Python/platform are saved, and a source change during execution invalidates the run. No full per-tick prediction table is retained.

The seven standard conditions use the existing generator and models, with seeds 0..4 and 100..119. These seeds are already inspected development data. The reference sparse predictor receives the true structural lag but trains from tick 0 without change knowledge. The probability oracle uses evaluator-only world history. Neither is an unprivileged competitor. Additional v1/v2 instances change only the check cadence from 64 to 1.

Return worlds use the existing probability rule and RNG offsets: stable ticks 0–599, structural 600–1199, stable 1200–1799, across seeds 100..119 and lags 2..5. All models see identical realized bits in each world. Predictions are scored before updates. Model events take effect on the next prediction. First post-return contraction requires `effective_tick > 1200` and uses `effective_tick - 1200`. An event effective at tick 1200 used only pre-return observations and is excluded; a change at tick 1800 is also excluded because it never affects a scored prediction. Output also records whether the selector was sparse before the tick-1200 prediction, so contraction cannot be confused with never expanding.

Artifacts retain seed × condition × model × phase mean log loss/Brier, compact per-world event counts/first expansion/first return contraction, and paired comparisons against the matched mixture and probability oracle. Structural conditions are averaged within seed before computing SE across seeds; case win counts are descriptive and correlated. The reference gap measures this supplied correct-lag expert's gain, not a theorem bounding every possible dynamic selector or learner.

After execution, the coordinator must compare Claude's reported values with `comparisons.json`: correct-sparse/matched means, structural penalties/win counts, cadence differences, and return-phase means. Check contraction delays in `event_summary.json`. Report discrepancies; do not silently change settings to match. Additional before/structural phases and cadence models are recorded, but this is not a new search or preregistered confirmation. Full probes have not been run by the author.
