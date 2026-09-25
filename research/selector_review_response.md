# Response to Claude's selector review — September 25, 2026

**Decision: freeze v1/v2.** Keep the worlds, baselines, tests and recorded viewers. Do not pursue a v3 selector or the previously proposed factorial ablation as a research contribution. This is a decision about this design and evidence, not proof that adaptive representations cannot help.

Claude independently wrote [the original review](claude_independent_review.md), preserved unchanged. Codex agrees with its practical recommendation. Its numerical probes have now been recreated and agree at the reported precision. One theoretical interpretation needs correction: the correct-lag reference is not an upper bound on every time-varying selector or learner. Expert-tracking theory also does not guarantee that this particular mixture beats every selector on every finite sequence.

## Reproduced evidence

[Reviewed recreation](../experiments/selector_review_probes.py), [method/provenance notes](probe_reproduction_notes.md), and [saved comparisons](../results/selector_review_dev/comparisons.json). These are recreated probes. Claude subsequently supplied claimed transcript-recovered script text in [its candidate report](claude_research_candidates.md); byte identity to old scratch files was not independently verified. All numbers below are mean log loss; lower is better.

| Structural post-change | Seeds 0–4 | Seeds 100–119 |
| --- | ---: | ---: |
| Matched mixture | 0.547171 | 0.551509 |
| Supplied correct-lag reference | 0.537354 | 0.542219 |
| V1 | 0.556825 | 0.562289 |
| V2 | 0.565313 | 0.567117 |
| V1 checking every tick | 0.548165 | 0.553900 |
| V2 checking every tick | 0.552128 | 0.557680 |

The reference is told the true lag, trains from tick zero and has no change-time knowledge. Its roughly 0.01-nat advantage is an empirical comparison, **not a maximum possible improvement**. Faster checks reduce selector penalties, but these inspected development results do not justify another tuning round.

On 80 return worlds (20 seeds × four lags), stable → structural at tick 600 → stable at tick 1200, v2 contracts in 80/80 cases after 80–144 ticks. Its final-phase loss is 0.528574 versus mixture 0.516833 and simple slow learner 0.515880; v2 is worse than the mixture in 79/80 cases. V1 scores 0.533675 and every-tick v2 0.525967. Contraction exists; predictive benefit is not demonstrated here. Changed-lag reselection remains untested and is deferred.

## What was completed

One standard-library run finished in 23.81 seconds, retaining phase means, event summaries, paired seed-level comparisons, source hashes and settings. The 255 world episodes comprise 175 single-change and 80 return episodes; conditions share randomness and are correlated. Seed-level uncertainty averages structural lags within seed first. Source files stayed unchanged during execution. All 29 existing tests passed; a smoke comparison reproduced an existing seed/condition and verified the return-world prefix. Initial sandbox-only test failures were filesystem permissions, resolved by granting project-scoped test writes.

[Per-case scores](../results/selector_review_dev/seed_condition_means.json), [events](../results/selector_review_dev/event_summary.json), [metadata](../results/selector_review_dev/metadata.json). The source revision is 7660d32 with uncommitted recreation files; exact hashes identify the executed sources. The script header records its pre-run review status; this report records completion. Local full artifacts remain under results/runs/selector_review_recreated_01. No original learner code or previous result was changed.

Seeds 100–119 were already used in Claude's review and are now explicitly inspected development data. Reserved sequence-world seeds 1000–1049 remain unused. No held-out confirmation, calibrated uncertainty, memory saving, scientific autonomy or novel learning mechanism is established. The next step is the separately reviewed research-question decision, not selector implementation.
