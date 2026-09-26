# Earlier hypotheses did not improve harder-world prediction

The scoring repair brings the motion-plus-push model forward from step 39 to step 11, but **does not improve final prediction in the harder world**. Keep `guided-partial` opt-in; enumeration remains the default. All six bounded runs are finished. No post-result tuning or additional sampling.

## What was wrong, and what changed

The saved harder-world trace already contained useful motion evidence at step 11. Input-related features crowded the shortlist: existing-model signal remained in the recorded residuals. Later evidence starvation also occurred, but it did not explain this first missed opportunity. Seen-structure exclusion did not block the new model.

Claude challenged a grouping draft and recommended removing the component associated with existing terms before scoring a new feature. We implemented that one change. The same saved prefix, using only observations through step 11, now proposes and retains `v+u`; its motion score rises from 0.743 to 0.926. Evidence retention, model language, fitting, planner and candidate-fit cap remain unchanged. [Exact design and objections](partial_proposal_design.md) · [Saved prefix diagnostic](../results/partial_v1/prefix_diagnosis.json).

## Completed comparison

Mean squared position error on the existing separate intervention evaluator; lower is better. Step numbers are zero-based trace indices, and indicate first addition to the model pool, not confirmed discovery.

| World | Original guided error | Conditioned guided error | First `v+u` step, old → new |
|---|---:|---:|---|
| Simple | 0.00028810 | 0.00026322 | 11 → 11 |
| Harder | 0.05317092 | 0.05379484 | 39 → 11 |
| Noise | 0.11967441 | 0.11975948 | 59 → never |

The harder-world final formula is `delta ≈ 0.769724*v + 0.293692*u`, applied per coordinate. It is close to the old result despite earlier availability. Earlier proposal timing was a real mechanism failure, but correcting it was insufficient to improve prediction. The noise-world final model remains position-based; absence of `v+u` there is not itself a failure.

All runs used 80 training and 44 evaluation tool units, totaling 354 actions, 480 training and 264 evaluation units. Candidate coefficient fits, old → new: simple 99 → 91, harder 55 → 76, noise 74 → 63. Conditioning adds base-feature evaluations and projection operations; it is not free and the harder-world run uses more candidate fits. [Complete counters, formulas and metrics](../results/partial_v1/summary.json).

These are six descriptive developmental runs using the already inspected seed 260926 and existing evaluator. No independent confirmation, significance, causal identification or novelty claim. The supplied two-term, per-axis model language and noise assumptions remain limits. Conditioning can also suppress useful correlated features. This result does not diagnose whether remaining error comes from representation, data collection or fitting.

## Reproduce and inspect

Source frozen at `3acb2ff357285859e2fff9aca100e153c6929019`; every run recorded a clean checkout. Raw files remain under ignored `results/runs/partial_v1_*`, with [hash manifest](../results/partial_v1/raw_manifest.json). For each of `development`, `challenge`, `noise`, run both modes with a fresh output path:

```sh
.venv/bin/python -m artificial_scientist.lab_run --variant challenge --proposal guided-partial --policies active --output results/runs/my_fresh_partial_check
```

[Harder-world replay](../results/partial_v1/replay.html) embeds the actual conditioned-run trace. Look at step 11 for the motion proposal. It replays a completed investigation; no learner is running. Browser playback remains unverified because local-file navigation was previously blocked; no workaround was attempted.

Thirty-two tests passed before execution. Claude Opus 5.5 reviewed the diagnosis/design; a separate Codex agent reviewed code and the prefix diagnostic before freezing. [Claude review](claude_partial_review.md) · [Provenance](partial_claude_provenance.json) · [Review log](review_log.md).

Next: inspect why earlier availability does not translate into better predictions in this same laboratory. Compare the retained models, their subsequent evidence and chosen experiments before selecting another repair. Do not assume a neural network, bigger search or changed evidence retention is the answer.
