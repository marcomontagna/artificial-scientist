# Results

## Adaptive-context prototype — September 25

The [reviewed v1 design](experiments/adaptive_state_v1.md) is implemented and has run once. It starts predicting from the latest bit, monitors four sparse history alternatives, and activates one extra history feature when its trailing prediction advantage crosses a fixed threshold. All 22 tests and the original smoke check passed. Five development seeds, four worlds and six learners produced 144,000 predictions in approximately 1.68 seconds. The experiment finished; the viewer replays its recorded data.

Mean post-change log loss (lower is better):

| World | Short memory | Long memory | Dense mixture | Sparse mixture | Adaptive |
| --- | ---: | ---: | ---: | ---: | ---: |
| Stable | 0.5056 | 0.5438 | 0.5112 | 0.5062 | 0.5056 |
| Parameter change | 0.5795 | 0.5691 | 0.5509 | 0.5647 | 0.5804 |
| Noise | 0.7125 | 0.7267 | 0.7130 | 0.7117 | 0.7125 |
| Added history dependency | 0.7130 | 0.5681 | 0.5668 | 0.5458 | 0.5532 |

The monitor-only ablation exactly matches short-memory predictions, while paying the same monitoring storage as the adaptive learner. Every condition and seed is retained in the [summaries](results/adaptive_state_v1_dev/summary.json).

**Decisions:** all five structural worlds activated the correct supplied lag (4 or 5), first used at tick 704, after the hidden change at tick 600. No premature structural activation. All five parameter-change worlds unnecessarily activated lag 2 (three at tick 640, two at 704), even though their rule still needs only lag 1; mean error slightly worsened. No activation in any stable or noise world (ten no-activation cases). No evidence yet for structural lags 2/3: these five seeds happened to use only 4/5. See [all ten events](results/adaptive_state_v1_dev/events.json).

**Verdict:** the narrow predefined engineering screen passes: structural gain over short memory is 0.1598 nats, stable penalty is zero, and stable activations are 0/5. However, the sparse mixture is better in every structural seed (mean advantage 0.0073 nats), and parameter-only changes fool the trigger into adding history. Passing that limited screen does not establish reliable diagnosis of insufficient memory, novelty, or superiority.

**Cost:** the adaptive learner maintains every shadow model and a 512-value gain-buffer capacity from the start. Average post-change storage is about 650 logical slots versus 136 for the sparse mixture and 10 for short memory; active feature count is not total memory. Aggregate measured predict/update time over all 20 worlds was about 0.205 seconds for adaptive and 0.234 seconds for sparse mixture; a single tiny timing sample does not establish speed superiority. These counts omit Python object overhead and are not RAM measurements. There is no demonstrated resource saving.

[Config](results/adaptive_state_v1_dev/config.json), [diagnostic](results/adaptive_state_v1_dev/diagnostic.json), [timings](results/adaptive_state_v1_dev/timings.json), and [provenance](results/adaptive_state_v1_dev/metadata.json). The run used clean source commit `bb87ef3`; metadata also hashes all package sources, the protocol, config and raw predictions. Full CSV is kept locally in ignored `results/runs/adaptive_state_v1_dev_20260925`. Reproduce with a fresh output directory:

```sh
python3 -m artificial_scientist.adaptive_state --config experiments/adaptive_state_v1.json --output results/runs/adaptive_v1_reproduction
```

No threshold was adjusted after this run. Existing development seeds were already inspected in v0; all findings are exploratory. Held-out seeds remain unused. There is no neural learner, active intervention, transfer, calibrated inadequacy test, learned feature generator, recurrent comparison or faithful context-tree reproduction. The most useful next experiment is to distinguish ordinary parameter adaptation from a need for more history.

## Multi-universe development run — September 25

Implemented the reviewed [v0 protocol](experiments/state_revision_v0.md): four sequence-world types, short/long context predictors and a discounted fixed-share order mixture. All 14 unit tests passed; the existing smoke run also completed. Independent Codex research and code reviewers approved the protocol and implementation. No Claude execution is attributed.

Five development seeds × four conditions × 1,200 observations × three baselines = 72,000 scored predictions. Approximate runner time: 0.59 seconds. Mean post-change log loss (lower is better; descriptive development results):

| World | Order 1 | Order 5 | Order mixture |
| --- | ---: | ---: | ---: |
| Stable | 0.5056 | 0.5438 | 0.5112 |
| Parameter change | 0.5795 | 0.5691 | 0.5509 |
| Noise | 0.7125 | 0.7267 | 0.7130 |
| Added history dependency | 0.7130 | 0.5681 | 0.5668 |

The structural worlds expose a weakness of short context; long context has a cost in stable worlds. This motivates a comparison but does not demonstrate a new adaptive learner, statistical superiority, calibration, cross-family generalization or resource savings. The mixture maintains all component models. At the v0 stage, no neural model, expansion trigger, active experimentation or transfer had been implemented. Held-out seeds were not used.

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

## Completed research decision phase

At the user’s request, Codex completed the decision-oriented research now and deferred implementation until tomorrow. The [focused novelty check](research/focused_prior_art.md) and [independent adversarial critique](research/critique.md) close the immediate controlled-sensing, dual-control, bandit and predictive-acquisition follow-ups. Broad diagnostic-action novelty is rejected; EPIG and robustness to active-learning bias already have close prior art, including a 2026 method.

[Exactly three candidate questions](research/candidate_gaps.md) were compared: diagnostic sensing, predictive versus parameter information under misspecification, and representation revision. [Decision](research/decision.md): select the second as a replication/stress test, not a novel method. The [pre-experiment protocol](experiments/selected_experiment.md) specifies shared filtering, acquisition policies, law table, hidden shifts, matched/misspecified conditions, held-out schedules, metric, falsifier, seed-level uncertainty, and resource caps. A separate Codex critic reviewed sources and design; timing, tuning and recovery ambiguities were corrected.

The historical three-candidate comparison, research decision and protocol are complete. The literature search remains bounded, not exhaustive. At that historical stage no new algorithm or experiment was implemented or run; the multi-universe run at the top of this report now adds empirical development evidence. No additional paid services were initiated.
