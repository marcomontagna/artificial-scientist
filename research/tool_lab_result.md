# First connected investigation — September 26, 2026

**The loop works. The experiment chooser is not yet consistently better than simple exploration.** One learner observes an unfamiliar simulated world, composes candidate formulas, predicts actions, selects a tool, receives an outcome and revises its models. No runtime LLM, neural network or trained RL policy. This is a bounded engineering demonstrator using known ideas, not a “Move 37” discovery.

## What it actually did

The active development run made 42 tool calls costing 80 units, proposed 24 new structures over the run (at most 8 live), and made 4 searches triggered by large prediction failures. Its final displacement predictor was:

`delta = 0.796573*v + 0.420284*u`, with `p_next = p + delta`, shared across x/y.

Here v is estimated motion from observed positions and u is the applied push component. The hidden development source uses 0.82 and 0.42; that structure is expressible in the supplied grammar. Matching it approximately validates this integration; sensor noise biases fitted coefficients, and source separation is not formal developer blinding.

## Fresh-intervention checks

Each exploration policy used 80 training cost units. Final formulas were frozen, then predicted the complete trajectories of three separately seeded intervention sequences starting at reset/home. No evaluation outcome entered the learner. Values below are mean **squared 2D position error**, averaged over 11 recorded action horizons, not statistical confidence estimates.

| World | Active learner | Random exploration | Coverage exploration | Persistence reference | Fixed home reference |
|---|---:|---:|---:|---:|---:|
| Development | 0.001237 | 0.000262 | 0.000675 | 0.484246 | 0.485540 |
| Challenge | 0.026477 | 0.231763 | 0.021288 | 0.379092 | 0.381625 |
| Noise | 0.118847 | 0.119577 | 0.118847 | 0.167248 | 0.120087 |

A fixed four-term linear reference fitted to each policy’s own training data is also recorded: active-data errors were 0.002781, 0.041424 and 0.164014 respectively. Full per-policy references and formulas are in the [summary](../results/tool_lab_v1/summary.json); per-horizon predictions remain in the raw traces and replay.

Development: random and coverage both beat active exploration. Challenge: active beats random, but coverage is better still. The challenge’s cross-axis/direction dependence lies outside our separable shared representation, so the learner gives an approximation rather than recovering the governing law. Noise: the active formula largely returns toward home; its tiny finite-run difference from fixed-home prediction is not a discovery or general advantage. Extra terms can fit noise.

All nine runs finished their budgets: 497 executed actions, 720 training cost units total, approximately 9.10 process CPU seconds including evaluation. Evaluation additionally consumed 44 tool cost units per policy/world (396 total), reported separately from training. One fixed seed per world, correlated prediction horizons, no tuning after the development run and no further sampling. No learned-policy superiority, calibration, physical-law recovery or novelty claim.

## What can be inspected

[Offline replay](../results/tool_lab_v1/replay.html): development/active actions, formulas as they were before acting, predictions, errors, model revisions, alternatives and scores. It is saved playback, not live training. The HTML is self-contained; download/open it locally. Browser preview was blocked for local file URLs; no workaround was attempted. Export safety/trace tests pass, but interactive playback has not been browser-verified.

[Exact implementation contract](tool_lab_implementation.md), [Claude plan review](claude_tool_lab_plan.md), [Claude code review](claude_tool_lab_code.md), [review log](review_log.md), [raw file hashes](../results/tool_lab_v1/raw_manifest.json). Twenty focused tests passed. Independent result audit status is recorded in the review log.

## Next engineering step

Improve this same agent’s choice of experiments, using the recorded decisions first. Compare which actions reduced fresh predictive error and where committee disagreement consumed budget without improving understanding. Review a concrete change before running it. The missing cross-axis representation is a separate known limitation; do not silently add the challenge’s exact formula as a supposed discovery. No new standalone statistical exercise is proposed.

## Reproduce

Frozen implementation commit: `92f50755847dbf67aeaad02a2165025239257eff`; world commit: `e6920e7`. Run from the repository root with existing local Python 3.9+:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m artificial_scientist.lab_run --variant development --output results/runs/my_fresh_development
```

Use a new output directory for each invocation. `--variant challenge` and `--variant noise` reproduce the two subsequent checks. Default seed 260926; no third-party runtime dependency. Raw traces, pre-action journals and all policy replays remain under `results/runs/tool_lab_v1_*` locally, not committed. The tracked active replay embeds its trace; the manifest fingerprints the remaining local evidence. Source hashes and clean-checkout status are saved in each run summary. Run evidence is reproducible up to timing fields.
