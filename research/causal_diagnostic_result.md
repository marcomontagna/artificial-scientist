# Finite-sample causal diagnostic — September 25, 2026

**The prespecified strong-case feasibility gate passes.** This validates one diagnostic component under supplied assumptions; it is not an autonomous scientist, a learned experiment policy or a novelty result.

## What was tested

Two normalized predictive models share each observed history: a Bayesian mixture of 30 supplied hidden-common-cause worlds (primary), and per-intervention KT probability tables (comparison). Each divides its joint predictive probability by the maximum likelihood over all 25 observed-only DAGs. Alarm threshold and 400-observation budget were fixed before sampling. Rejection challenges the joint observed-only/stationary/perfect-intervention assumptions; it does not uniquely identify a hidden cause.

The [reviewed protocol](../experiments/causal_diagnostic_v0.md) fixes 15 world cells, two non-adaptive schedules, and 200 development seeds per cell. Both learners update from observations, but neither chooses actions or invents its candidate family.

## Results at 400 observations

Counts below are alarms out of 200, shown separately for each cell. Intervals are pointwise 95% Wilson intervals; shared seeds correlate cells, so these are not pooled independent trials.

| Strong world | Schedule | Structured mixture, count [interval] | KT count | Structured mean capped alarm time |
| --- | --- | --- | --- | --- |
| pair01_e0.05 | random7 | 198 [0.964, 0.997] | 14 | 162.03 |
| pair01_e0.05 | roundrobin7 | 200 [0.981, 1.000] | 12 | 155.04 |
| pair02_e0.05 | random7 | 200 [0.981, 1.000] | 6 | 158.16 |
| pair02_e0.05 | roundrobin7 | 198 [0.964, 0.997] | 16 | 146.61 |
| pair12_e0.05 | random7 | 198 [0.964, 0.997] | 13 | 163.89 |
| pair12_e0.05 | roundrobin7 | 199 [0.972, 0.999] | 10 | 152.94 |

Every primary lower bound exceeds the preregistered 0.80 target (minimum 0.964); required count was 172/200 in each of six cells. Mean capped times include every seed, with non-detections assigned 401.

- **Medium signal (noise 0.20):** structured mixture detects 8–15/200 (4–7.5%) across the six cells; KT detects zero in each.
- **Weak signal (noise 0.35):** both detect zero in every cell.
- **Biased-common-cause stress:** structured mixture detects 0/200 under both schedules; KT detects 0/200 random and 1/200 round-robin. The structured numerator cannot claim robustness beyond its supplied family.
- **All five null controls:** zero alarms in each schedule/numerator cell, each with interval [0, 0.0188]. These observations do not establish a uniform false-alarm guarantee; the mathematical guarantee has explicit assumptions and an exact-arithmetic qualification.

All 60 cell summaries, horizons 100/200/400, censoring, capped times and prequential losses are in [summary.json](../results/causal_diagnostic_v0/summary.json). Log loss compares numerator predictions only on the same world's schedule-selected observations; it is not an independent-query score or a calibration result. Weak/stress failures were retained without tuning.

## Execution and review

One full run completed in **24.309 seconds**, 6,000 episodes, 2.4 million observations, approximately 10.18 MB of output. Source commit `5d77412be4f8ada5682201f101d3b91c92d8e55b` was clean and unchanged throughout. All **45 tests passed** before execution. The required 20-episode smoke completed in 0.113217 seconds; its fixed conservative projection was 42.456 seconds against a 350-second resource gate. No extra dependencies or spending.

Claude Opus 5.5 reviewed the plan; Codex addressed its runtime, passive-cell and configuration findings. A distinct Codex worker implemented the code; the coordinator reviewed source/tests before execution. A separate reviewer audits the final evidence, as recorded in [review_log.md](review_log.md). The unchanged Claude review and hashed provenance are retained alongside this report.

[Config](../results/causal_diagnostic_v0/config.json), [gate](../results/causal_diagnostic_v0/gate.json), [metadata](../results/causal_diagnostic_v0/metadata.json). These four compact artifacts are tracked. Raw `episodes.jsonl` and `worlds.jsonl` remain local under `results/runs/causal_diagnostic_v0_20260925`; hashes are tracked, but a fresh clone must reproduce them to audit individual paths. Seeds 190–194 (smoke) and 200–399 (study) are inspected development data, not held-out confirmation.

To reproduce, choose two fresh output directories and use the repository-local Python environment:

```sh
.venv/bin/python -B -m artificial_scientist.causal_diagnostic --config experiments/causal_diagnostic_v0.json --output results/runs/causal_diagnostic_smoke_reproduction --smoke
.venv/bin/python -B -m artificial_scientist.causal_diagnostic --config experiments/causal_diagnostic_v0.json --output results/runs/causal_diagnostic_reproduction --smoke-evidence results/runs/causal_diagnostic_smoke_reproduction
```

The runner enforces the 500-second internal deadline and 100-MB cap; the recorded study was additionally wrapped in a 540-second subprocess timeout. New full runs require matching smoke source/config hashes and the fixed resource gate. Incomplete runs cannot pass. No adaptive policy, transfer, hidden law change, neural representation or model repair was tested.

## Decision

Stop this component study here. The supplied family makes strong cases easy and the stress case exposes its limits. Next design a tiny interactive universe in which the learner chooses actions to improve predictions and uncertainty on independent experiments, compared with random/round-robin actions at equal budgets. Understanding is the objective; environmental rewards and winning are optional. Keep a deliberately wrong-family control and a route to revising explanations, without calling a known baseline novel. Do not tune this completed version after inspecting its results.
