# Results

## Three equation studies — September 26

The [short overnight report](research/overnight_equation_report.md) covers840development datasets across three separately reviewed runs;90tests pass. Stage1 recovery **failed**:9/20noise cases produced nonzero formulas. Stage2 confirmation passed: noise false-claim datasets fell32/100→0/100 and quadratic15/100→0/100, with198/200true quadratic terms retained. Stage3 domain challenge passed: uncertainty-aware rejection rose10/40→40/40 for exponential and26/40→40/40 for cubic; correct-model controls stayed2/40 perarm. Crude wide-domain rejection was29/40 on those controls.

Supplied grammar, known Gaussian noise, fixed outside-family functions and correlated controls limit the conclusions. The stages are distinct components: confirmation filters claims, and fixed-full-model domain-test guarantees do not apply automatically to selected sparse formulas. No active acquisition, grammar revision, neural/RL training or novelty was demonstrated in this sequence. All three runs and numerical evidence were independently audited; the original failure is preserved. [Study1](research/equation_stage1_result.md) · [Study2](research/equation_stage2_result.md) · [Study3](research/equation_stage3_result.md) · [Reproduction](research/equation_reproduction.md).

## Stateful room — September 26

The [reviewed stateful learner](research/stateful_room_result.md) completed640episodes/61,440actions from clean source`e6978fd`;65tests pass. Mean primary prediction loss: two-step planning0.50067, greedy0.51214, random0.60726nats. Both pooled thresholds and all six per-world harm guards pass. The noise control is worse than random; fixed cycle is best in two designed worlds but fails coverage in the third. Hidden-memory stress remains incompletely modeled.

The learner estimates transition probabilities without a supplied door-rule library; its state representation and table form remain supplied. This demonstrates bounded shallow coverage-planning benefit, not new scientific reasoning, neural representation learning or novel RL. Claude reviewed the protocol; separate agents reviewed implementation and results. [Recorded room replay](visualization/stateful_room.html) · [next steps](NEXT_STEPS.md).

## Interactive laboratory — September 25

The [first active-learning prototype](research/interactive_lab_result.md) completed960episodes/46,080experiments in6.249seconds;54tests pass. Mean excess query loss over the four supplied-library worlds improved by0.02018nats versus random and0.01394 versus round-robin. Both fixed primary thresholds pass; descriptive seed-level intervals are reported in the full result.

The fair-random control is worse under active acquisition. The supplied flexible fallback helps on the out-of-library majority world but does not discover its symbolic rule; flexibility also costs performance in the well-specified worlds. No RL-policy training, novelty or calibration claim. Claude reviewed the plan; separate agents reviewed implementation and independently audited all metrics. [Offline replay](visualization/interactive_lab.html) now shows real action choices and posterior changes. Earlier component studies remain below as historical evidence.

## Finite-sample causal diagnostic — September 25

The [reviewed study](research/causal_diagnostic_result.md) completed 6,000 episodes and 2.4 million observations in 24.309 seconds from clean committed source `5d77412`. All 45 tests passed. The prespecified structured mixture detected strong model failures in 198–200/200 trials per cell, versus 6–16/200 for KT; all six primary lower Wilson bounds exceed 0.80. Medium cases yielded only 8–15/200 detections, weak cases zero, and the biased-common-cause stress case zero for the primary. All null cells had zero observed alarms; this does not prove uniform validity.

The diagnostic benefits from a supplied family of explanations. It learns mixture weights/probabilities but does not choose experiments, invent models or establish novelty. No tuning followed results. Next is a reviewed tiny interactive universe focused on understanding without requiring a win/lose reward. [Full summaries](results/causal_diagnostic_v0/summary.json) and [current next steps](NEXT_STEPS.md).

## Causal-world feasibility — September 25

The [reviewed calculation](research/causal_feasibility_result.md) passed all 65 population comparisons across 13 worlds and five fixed action mixtures, enumerating all 25 observed-only DAGs. Passive and pair-only designs have zero separation; informative mixtures have positive separation for nonzero confounding. The in-class controls remain zero. This matches the independently derived mathematical reference; it is code/foundations validation, not novel science or learned behavior.

All 37 tests passed. One full calculation completed in 0.118 seconds from clean source `14e7227`; source/config/artifact hashes are preserved. At that population-check stage there were no samples or seeds, finite-sample power experiment, adaptive causal policy, or causal model repair. Claude reviewed design/code and a separate Codex reviewer verified fixes. Its proposed finite-sample follow-up is now completed above; adaptive action policies remain unimplemented.

## Current decision — selector line frozen

Claude’s independent review and Codex’s [preserved reproduction](research/selector_review_response.md) support freezing v1/v2 and deferring further selector tuning/factorial studies. On 80 return-to-simple worlds, v2 contracts in all 80 but predicts worse than the matched mixture in 79. Its mean final-phase log loss is 0.528574 versus 0.516833. Faster checks reduce earlier penalties without establishing a new method.

One reviewed recreation completed in 23.81 seconds; all 29 tests present at that stage passed. [Seed status](research/seed_registry.md): 0–4 and 100–119 are inspected development data; reserved seeds 1000–1049 remain unused. The supplied correct-lag reference’s roughly 0.01 advantage is **not** a theoretical upper bound on all selectors. The original review is preserved with this explicit correction. No new learner or v3 was implemented.

[The research reset](research/research_reset.md) compares three Claude proposals and provisionally selects causal-model falsification for feasibility work only. At that research-reset stage, no new learner, active-intervention experiment or novelty clearance resulted; the later population check above adds mathematical/implementation evidence only.

The entries below record earlier stages. Their original next-step suggestions are superseded by [current next steps](NEXT_STEPS.md).

## Reversible-context v2 — September 25

**What learns:** these are probabilistic count-table predictors, not neural networks. Observations update their conditional probabilities; a hand-written selector chooses among a supplied set of history features and learning speeds. V2 adds a faster lag-1 expert and reversible choice. It does not invent features or choose experiments. [Design fixed before running](experiments/adaptive_state_v2.md).

All 29 tests and the original smoke check passed. One reviewed run scored 252,000 predictions across 35 worlds: five seeds × three controls, plus five seeds × four explicitly balanced structural lags. Runtime about 2.93 seconds. Seeds and noise streams are shared across conditions, so the 35 cases are correlated development cases, not independent replications. The original v1 outputs remain unchanged; v1 was also evaluated on the expanded world set for a paired comparison.

Mean post-change log loss (lower is better; structural row averages all 20 seed–lag cases equally):

| World | Slow lag 1 | Fast lag 1 | V1 | Original sparse mixture | Matched mixture | V2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Stable | 0.5056 | 0.5317 | 0.5056 | 0.5062 | 0.5072 | 0.5066 |
| Parameter change | 0.5795 | 0.5542 | 0.5804 | 0.5647 | 0.5400 | 0.5613 |
| Noise | 0.7125 | 0.7211 | 0.7125 | 0.7117 | 0.7091 | 0.7143 |
| Structural, all lags | 0.7127 | 0.7106 | 0.5568 | 0.5475 | 0.5472 | 0.5653 |

**Improvement:** parameter worlds with any unnecessary expansion fell from 5/5 in v1 to 0/5 in v2. V2 had zero sparse selections in stable/noise controls, and the correct structural lag was active before the final observation in 20/20 structural worlds. No sparse selection preceded the hidden change.

**Tradeoff:** v2 activated useful memory at tick 704 in nine structural worlds and tick 768 in eleven; v1 did so at 704 in nineteen and 768 in one. Consequently, correct-lag occupancy after the change fell from 82.13% to 76.80%, and structural prediction was worse than both v1 and the matched mixture. Stable/noise loss also slightly worsened versus v1. The narrow predefined screen passes (aggregate structural penalty 0.01814 <=0.02); this does not mean v2 is the best predictor. For structural lag 2 alone, its penalty versus matched mixture is about 0.02023, above that threshold if applied per lag rather than as preregistered aggregate.

**Decisions and cost:** v2 made 20 expansions and 57 slow/fast switches, with no observed contraction or sparse-lag reselection. Contraction passes a controlled unit test; neither contraction nor sparse-lag reselection was observed in this run. There is no explicit sparse-to-different-sparse reselection test yet. At this stage return-to-simple and changed-lag behavior had not been tested; the later review reproduction above tests the former. Per-world switches, mean dwell time and correct-lag occupancy are in [decisions](results/adaptive_state_v2_dev/decisions.json); all changes are in [events](results/adaptive_state_v2_dev/events.json). Average structural post-change storage was 915.6 logical slots for v2 versus 147.6 for the matched mixture and 649.6 for v1. All shadows/loss buffers are counted; no RAM or efficiency claim.

[Config](results/adaptive_state_v2_dev/config.json), [per-lag/seed summaries](results/adaptive_state_v2_dev/summary.json), [screen](results/adaptive_state_v2_dev/diagnostic.json), [timings](results/adaptive_state_v2_dev/timings.json), [provenance](results/adaptive_state_v2_dev/metadata.json). Clean source revision `ef425ff`, all package/protocol/config/CSV hashes preserved. Raw CSV stays in ignored `results/runs/adaptive_state_v2_dev_20260925`. Reproduce into a fresh directory:

```sh
python3 -m artificial_scientist.adaptive_state_v2 --config experiments/adaptive_state_v2.json --output results/runs/adaptive_v2_reproduction
```

No settings changed after this run, no reserved seeds used, no novel-method/causal-diagnosis claim. The original follow-up proposal was return-to-simple/changed-lag worlds and a factorial comparison; the later review decision supersedes it. Mixture prediction remains the stronger comparison here.

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

No threshold was adjusted after this run. Existing development seeds were already inspected in v0; all findings are exploratory. Held-out seeds remain unused. There is no neural learner, active intervention, transfer, calibrated inadequacy test, learned feature generator, recurrent comparison or faithful context-tree reproduction. At that stage the proposed next experiment was to distinguish ordinary parameter adaptation from a need for more history.

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
