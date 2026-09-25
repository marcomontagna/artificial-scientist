# Artificial Scientist

Small, falsifiable experiments in how an artificial learner can understand an unknown environment by predicting, testing hypotheses, choosing interventions, and adapting when hidden laws change.

**This is a research experiment, not an AGI claim.** We are not training a frontier language model, claiming a novel architecture, or claiming that combining familiar techniques creates a new paradigm. A well-supported negative result is a successful outcome. The name describes the experimental learning loop, not demonstrated scientific autonomy.

## Current direction

The goal is a learner that investigates unfamiliar systems across **multiple procedurally generated universes**. Understanding is the objective: improve predictions, uncertainty and explanations by choosing informative experiments; a win/lose reward is optional. The passive context-selection line is now frozen after independent review; the next question must involve choosing informative actions, with strong baselines and a falsifiable benefit. Neural networks are an option, not a committed architecture. See [the concise direction](research/direction.md) and [next steps](NEXT_STEPS.md). The earlier EPIG/EIG plan is optional groundwork, not the active target. Novelty and effectiveness remain unproven.

## Current model and result

The learner is a set of small probabilistic predictors that learn conditional probabilities from observations. A selector chooses among supplied history features and learning speeds; it is not a neural network and does not invent features. The [v2 prototype](experiments/adaptive_state_v2.md) can reverse its choice. It eliminated parameter-only false expansions in this five-seed run, but delayed useful expansions and predicted worse than v1 on structural worlds. The matched mixture still predicts better. The v2 run passed its 29-test suite; see [results and limits](RESULTS.md). All trial models remain allocated, so no memory savings are demonstrated. [Claude’s review and Codex’s reproduced evidence](research/selector_review_response.md) support stopping selector iterations; the [completed research pass](research/research_reset.md) provisionally selects testing whether interventions can reveal wrong causal assumptions. The [causal-world feasibility check](research/causal_feasibility_result.md) now passes; the [finite-sample diagnostic](research/causal_diagnostic_result.md) now detects strong cases in 99–100% of trials, but fails the mismatched-family stress case. Next is an interactive learner that chooses experiments. Novelty is unverified.

## Finite-sample diagnostic check

The reviewed run completed 6,000 episodes in 24.31 seconds; all 45 tests pass. A mixture of supplied hypotheses detected strong model failures in 198–200/200 trials per cell, versus 6–16/200 for independent KT tables. Medium/weak signals and the biased-common-cause stress case expose limits. No observed null alarms, autonomous action choice or novelty claim. [Full evidence and caveats](research/causal_diagnostic_result.md).

## Earlier causal-world feasibility check

A separate deterministic calculation checks when interventions make hidden-common-cause worlds incompatible with the assumed observed-only causal models. All 65 declared cases match the expected mathematics; 37 tests pass. This is foundational code validation, not an active causal learning agent or a detection-power result. [Evidence and next step](research/causal_feasibility_result.md).

## Replay the recorded universes

Open the [v2 comparison report](visualization/v2_report.html) for outcomes, decisions and memory-selection timelines across all 35 worlds. It reads saved data and runs no learning job. Regenerate with `python3 visualization/export_v2_report.py` after reproducing the v2 run into `results/runs/adaptive_state_v2_dev_20260925`.

Open [the adaptive replay](visualization/adaptive_replay.html) in a browser to choose a world, seed and tick. See predictions, error, total logical storage and exactly when the learner activates an older lag. It is recorded data, not a live training job. Download/open the file locally; GitHub displays its source. The [original baseline replay](visualization/replay.html) is preserved.

Regenerate with `python3 visualization/export_adaptive_replay.py`. In a fresh clone, first run `python3 -m artificial_scientist.adaptive_state --config experiments/adaptive_state_v1.json --output results/runs/adaptive_state_v1_dev_20260925`. If reproducing into another fresh directory, pass it to the exporter with `--run`. No held-out data or paid service is needed.

## Questions worth testing

- Can probabilistic predictions remain calibrated under distribution shift?
- When does active experimentation or expected information gain help after accounting for intervention and compute budgets?
- Can explicit competing hypotheses improve sample efficiency over simple predictive baselines?
- When do learned latent representations help generalization rather than hide leakage or collapse?
- Which causal or world-model assumptions are identifiable from the available observations and interventions?
- How quickly can a learner adapt when an unannounced environment law changes, and at what cost on stationary tasks?

These are directions, not novelty claims. Start with [the research workflow](research/workflow.md), map the closest prior art, and select one narrow question before building a new method.

## Start locally

Python 3.9+ runs the standard-library scaffold; Python 3.11+ is recommended for future optional ML work. No GPU, MLX, model download, API key, or paid service is required.

```sh
python3 -m venv .venv
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m artificial_scientist.run --config experiments/smoke.json --output results/runs/smoke
```

Run from the repository root. The package works directly from this checkout; optional editable installation is `python -m pip install -e .` inside the virtual environment. Keep installations local. MLX is deliberately not a dependency: add an optional backend only when a selected experiment benefits from it, verify Apple Silicon/Python compatibility, and preserve a CPU baseline.

The smoke run compares a constant 0.5 predictor, a cumulative Beta-Bernoulli predictor, and a fixed-window Beta-Bernoulli predictor under a hidden probability change. Predictions are scored before updates. This validates plumbing; it does not implement active experiment selection, causal discovery, or representation learning and is not evidence of research novelty. The learner interface receives only the selected action and resulting binary observation; hidden laws are evaluator metadata. This is a protocol boundary, not a security sandbox.

## Layout

| Path | Purpose |
| --- | --- |
| `research/` | Literature map, candidate gaps, critique, experiment preregistration and review records |
| `environments/` | Environment specifications and assumptions |
| `baselines/` | Baseline definitions and fair-comparison requirements |
| `metrics/` | Scoring conventions and evaluation guidance |
| `experiments/` | Versioned run configurations and experiment plans |
| `artificial_scientist/` | Minimal executable environment, baselines, metrics, runner |
| `tests/` | Determinism, scoring, hidden-change, and artifact checks |
| `results/` | Small tracked smoke output and ignored per-run artifacts |
| `RESULTS.md` / `NEXT_STEPS.md` | Honest evidence summary and next decisions |
| `AGENTS.md` / `CLAUDE.md` | Codex and Claude Code working agreements |
| `visualization/` | Offline replay of recorded worlds and baseline predictions |

## Research standards

Map approximately 2016–2026 literature through the actual run date, plus foundational earlier work when relevant. Read primary papers and official repositories; record URLs, dates, assumptions, comparison points, and search limits. Never invent citations or infer novelty from an unsuccessful search.

Predefine the falsifier, baselines, primary metric, seed split, interventions, and compute budget before results. Separate development from held-out evaluation. Report seed-level outcomes, effect sizes and uncertainty, ablations, failures, and resource costs. Calibration requires reliability analysis; low log loss alone does not establish calibration. Observational prediction alone does not establish causality.

## Current workflow

Codex coordinates research and implementation directly, with a different agent reviewing each substantive artifact. Claude has independently reviewed the project; Codex verifies claims and records distinct reviewers honestly. Official Claude Code may run bounded research using verified subscription access with usage credits off. Give workers explicit file ownership.

## License

MIT; see [LICENSE](LICENSE). Third-party papers, datasets, and code retain their own licenses. Do not vendor them without checking redistribution terms.
