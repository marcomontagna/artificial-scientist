# Artificial Scientist

Small, falsifiable experiments in how an artificial learner can understand an unknown environment by predicting, testing hypotheses, choosing interventions, and adapting when hidden laws change.

**This is a research experiment, not an AGI claim.** We are not training a frontier language model, claiming a novel architecture, or claiming that combining familiar techniques creates a new paradigm. A well-supported negative result is a successful outcome. The name describes the experimental learning loop, not demonstrated scientific autonomy.

## Current direction

The goal is a learner that investigates unfamiliar systems across **multiple procedurally generated universes**. First test whether it can recognize insufficient predictive state and selectively add useful memory/state. Neural networks are an option, not a committed architecture. See [the concise direction](research/direction.md) and [next steps](NEXT_STEPS.md). The earlier EPIG/EIG plan is optional groundwork, not the active target. Novelty and effectiveness remain unproven.

## Questions worth testing

- Can probabilistic predictions remain calibrated under distribution shift?
- When does active experimentation or expected information gain help after accounting for intervention and compute budgets?
- Can explicit competing hypotheses improve sample efficiency over simple predictive baselines?
- When do learned latent representations help generalization rather than hide leakage or collapse?
- Which causal or world-model assumptions are identifiable from the available observations and interventions?
- How quickly can a learner adapt when an unannounced environment law changes, and at what cost on stationary tasks?

These are directions, not novelty claims. Start with [the overnight brief](research/overnight_brief.md), map the closest prior art, and select one narrow question before building a new method.

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
| `research/` | Literature map, candidate gaps, critique, experiment preregistration, coordination |
| `environments/` | Environment specifications and assumptions |
| `baselines/` | Baseline definitions and fair-comparison requirements |
| `metrics/` | Scoring conventions and evaluation guidance |
| `experiments/` | Versioned run configurations and experiment plans |
| `artificial_scientist/` | Minimal executable environment, baselines, metrics, runner |
| `tests/` | Determinism, scoring, hidden-change, and artifact checks |
| `results/` | Small tracked smoke output and ignored per-run artifacts |
| `RESULTS.md` / `NEXT_STEPS.md` | Honest evidence summary and next decisions |
| `AGENTS.md` / `CLAUDE.md` | Codex and Claude Code working agreements |
| `HERMES_OVERNIGHT_PROMPT.md` | Paste-ready research-director instructions |

## Research standards

Map approximately 2016–2026 literature through the actual run date, plus foundational earlier work when relevant. Read primary papers and official repositories; record URLs, dates, assumptions, comparison points, and search limits. Never invent citations or infer novelty from an unsuccessful search.

Predefine the falsifier, baselines, primary metric, seed split, interventions, and compute budget before results. Separate development from held-out evaluation. Report seed-level outcomes, effect sizes and uncertainty, ablations, failures, and resource costs. Calibration requires reliability analysis; low log loss alone does not establish calibration. Observational prediction alone does not establish causality.

## Overnight workflow

Use [the Hermes prompt](HERMES_OVERNIGHT_PROMPT.md). Hermes directs; Codex maps prior work and builds reusable infrastructure; Claude critiques the proposal and tests its claims. Give each agent explicit file ownership. If a tool or agent is unavailable, record that honestly and continue the feasible work. No agent is launched merely by creating this repository.

## License

MIT; see [LICENSE](LICENSE). Third-party papers, datasets, and code retain their own licenses. Do not vendor them without checking redistribution terms.
