# Results

> Current direction update: [multiple universes and adaptive predictive state](research/direction.md). The earlier EPIG selection below is historical optional groundwork. No new code, tests or experiments were run for this documentation update; the new candidate has no empirical result or novelty clearance.

## Scaffold validation

Seven unit tests passed with Python 3.9.6. A deterministic smoke run completed for five seeds, 200 observations per seed, and three predictors (3,000 scored predictions). This checks plumbing, not novelty, causal learning, or general intelligence.

Commands (from repository root):

```sh
python3 -m unittest discover -s tests -v
python3 -m artificial_scientist.run --config experiments/smoke.json --output results/scaffold_smoke
```

The recorded output already exists; reproduce into a fresh `results/runs/reproduction` directory. Tests cover deterministic paired observations, predict-before-update initialization, hidden-switch boundary, Bayesian updating/forgetting, score validation, artifact creation, overwrite protection and output scope.

| Baseline | Before Brier | After Brier | Before log loss | After log loss |
| --- | ---: | ---: | ---: | ---: |
| constant | 0.2500 | 0.2500 | 0.6931 | 0.6931 |
| cumulative_beta | 0.1530 | 0.3554 | 0.4801 | 0.9337 |
| windowed_beta | 0.1565 | 0.2023 | 0.4893 | 0.5938 |

Values are means of five seed-level phase averages. No confidence intervals or hypothesis tests were computed; the known change favors forgetting and is not a selected research result. No calibration or adaptation-time claim follows from these means.

Raw evidence: [config](results/scaffold_smoke/config.json), [predictions](results/scaffold_smoke/predictions.csv), [seed-level scores](results/scaffold_smoke/summary.json), [runtime metadata](results/scaffold_smoke/metadata.json). The recorded revision is the local pre-run scaffold commit; browser publication may assign a different commit ID. The committed source and config reproduce this run.

## Pending overnight work

A bounded first literature pass is complete: [12 primary-source anchors and four close comparisons](research/prior_art.md), with [search history and exclusions](research/search_log.md). A separate Codex reviewer checked the scaffold, reproduced the recorded results and reviewed the literature claims; see [review](research/scaffold_review.md). No supported novelty claim emerged. A candidate follow-up is diagnostic action selection under hidden changes, but active change detection, dual control and nonstationary bandits remain necessary prior-art checks.

Three fully assessed candidate gaps, independent Claude critique, research-question selection, preregistration, active interventions, causal/world-model methods and learned representations remain pending. The user reports Hermes and Claude are running; Codex prepared [a scoped handoff](HERMES_HANDOFF.md), but has not verified their acceptance or contributions. Codex used one research worker and one separate reviewer. No paid external agent run was initiated.

The initial first-phase pass is deliberately bounded to conserve tokens. The [Notion activity report](https://app.notion.com/p/3e61202c798281d3bb93d2e241f1f009) has a one-time update scheduled for September 26, 2026 at 8 p.m. America/Chicago. All further work must respect the user’s zero-additional-spending rule and independent-review requirement.

## Completed research decision phase

At the user’s request, Codex completed the decision-oriented research now and deferred implementation until tomorrow. The [focused novelty check](research/focused_prior_art.md) and [independent adversarial critique](research/critique.md) close the immediate controlled-sensing, dual-control, bandit and predictive-acquisition follow-ups. Broad diagnostic-action novelty is rejected; EPIG and robustness to active-learning bias already have close prior art, including a 2026 method.

[Exactly three candidate questions](research/candidate_gaps.md) were compared: diagnostic sensing, predictive versus parameter information under misspecification, and representation revision. [Decision](research/decision.md): select the second as a replication/stress test, not a novel method. The [pre-experiment protocol](experiments/selected_experiment.md) specifies shared filtering, acquisition policies, law table, hidden shifts, matched/misspecified conditions, held-out schedules, metric, falsifier, seed-level uncertainty, and resource caps. A separate Codex critic reviewed sources and design; timing, tuning and recovery ambiguities were corrected.

This supersedes the earlier pending-research section: the three-candidate comparison, research decision and protocol are now complete for tomorrow’s discussion. The literature search remains bounded, not exhaustive. No new algorithm or experiment was implemented or run; previous smoke numbers remain the only local empirical results. No additional paid services were initiated.
