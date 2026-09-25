# Results

## Multi-universe development run — September 25

Implemented the reviewed [v0 protocol](experiments/state_revision_v0.md): four sequence-world types, short/long context predictors and a discounted fixed-share order mixture. All 14 unit tests passed; the existing smoke run also completed. Independent Codex research and code reviewers approved the protocol and implementation. No Hermes or Claude execution is attributed.

Five development seeds × four conditions × 1,200 observations × three baselines = 72,000 scored predictions. Approximate runner time: 0.59 seconds. Mean post-change log loss (lower is better; descriptive development results):

| World | Order 1 | Order 5 | Order mixture |
| --- | ---: | ---: | ---: |
| Stable | 0.5056 | 0.5438 | 0.5112 |
| Parameter change | 0.5795 | 0.5691 | 0.5509 |
| Noise | 0.7125 | 0.7267 | 0.7130 |
| Added history dependency | 0.7130 | 0.5681 | 0.5668 |

The structural worlds expose a weakness of short context; long context has a cost in stable worlds. This motivates a comparison but does not demonstrate a new adaptive learner, statistical superiority, calibration, cross-family generalization or resource savings. The mixture maintains all component models. No neural model, expansion trigger, active experimentation or transfer has been implemented. Held-out seeds were not used.

Tracked [seed-level summaries](results/state_revision_v0_dev/summary.json), [configuration](results/state_revision_v0_dev/config.json) and [metadata](results/state_revision_v0_dev/metadata.json). Full predictions remain locally in ignored `results/runs/state_revision_v0_dev_20260925/predictions.csv`; reproduce using the command below with a fresh output path. Metadata records the precommit revision, dirty state and exact new module hash.

```sh
python3 -m unittest discover -s tests -v
python3 -m artificial_scientist.sequence_worlds --config experiments/state_revision_v0.json --output results/runs/state_revision_v0_reproduction
```

### Earlier activity (historical)

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

This supersedes the earlier pending-research section: the three-candidate comparison, research decision and protocol are now complete for tomorrow’s discussion. The literature search remains bounded, not exhaustive. At that historical stage no new algorithm or experiment was implemented or run; the multi-universe run at the top of this report now adds empirical development evidence. No additional paid services were initiated.
