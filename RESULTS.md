# Results

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

Literature mapping, three candidate gaps, independent Claude critique, research-question selection, preregistration, active interventions, causal/world-model methods and learned representations have not been completed. No overnight agents have been launched. Follow research/overnight_brief.md and replace this section with real findings, including failures and blockers.
