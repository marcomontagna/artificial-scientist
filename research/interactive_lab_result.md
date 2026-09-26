# Interactive laboratory v0 — September 25, 2026

**The first action-selecting learner now runs.** It chooses switch experiments, predicts the lamp, observes the outcome, and updates a Bayesian model. The prespecified primary screen passes in this finite supplied-library toy. This is active learning/experimental design, not a trained RL policy or a novel scientist architecture.

## What learns

There are 35 supplied rule/noise hypotheses and a flexible fallback that learns independent Beta-Bernoulli probabilities for eight switch settings. Bayesian evidence changes the weight assigned to each explanation. The primary policy chooses the action with highest expected predictive information about future lamp observations, a known [EPIG](https://proceedings.mlr.press/v206/bickfordsmith23a.html) principle. The world rule and evaluator queries never update the learner directly. The separate noise action is known to be irrelevant and excluded for every policy; its avoidance is not a discovery.

For data D and experiment a, the action score is the mean over eight future query settings b of I(Y_a;Y_b* | D). The future outcome is a separate draw, including when a=b. The fallback therefore needs the Beta second moment E[p²], not merely E[p]². Unit tests and independent calculations check this distinction. Posterior weights use pre-observation likelihoods. No environmental reward, neural network, new symbolic rule generation or long-horizon planning is present.

## Results

The primary score is the mean excess query log loss over post-update steps1–48 (nats per query-cell per step), averaged equally across four worlds and then40 development seeds. Queries cover every switch setting analytically; they are not held-out rule families. Lower is better.

| World | Predictive information + fallback | Random switches | Round-robin | Structured-only information |
| --- | ---: | ---: | ---: | ---: |
| lamp_a | 0.04513 | 0.06401 | 0.05758 | 0.03595 |
| and_ab | 0.04624 | 0.06807 | 0.06203 | 0.04123 |
| xor_ab | 0.05357 | 0.06704 | 0.06414 | 0.04757 |
| or_ac | 0.04628 | 0.07282 | 0.06321 | 0.03480 |
| random | 0.08502 | 0.05575 | 0.06288 | 0.09789 |
| majority | 0.17247 | 0.23311 | 0.18599 | 0.30543 |
| Four primary worlds, equal mean | 0.04781 | 0.06799 | 0.06174 | 0.03989 |

Paired primary differences, averaging the four worlds within each seed before computing uncertainty:

- Versus hybrid_random: **-0.02018 nats**, descriptive95% normal interval [-0.02824, -0.01212], seed SE 0.00411.
- Versus hybrid_roundrobin: **-0.01394 nats**, descriptive95% normal interval [-0.02122, -0.00665], seed SE 0.00372.

Both means beat the fixed −0.01 threshold. Intervals are descriptive, not held-out confirmation. These four worlds exactly match supplied hypotheses/noise levels, and the primary acquisition targets the evaluation query distribution. Equal sample budgets do not imply equal compute.

**Failures and tradeoffs:** predictive information is worse than both matched baselines on the fair-random lamp. The structured-only learner has lower mean primary loss than the hybrid, exposing the cost of flexibility in well-specified worlds. On the majority world outside the library, the hybrid improves substantially over structured-only: final mean excess loss0.06878 versus0.30836, with mean fallback mass0.99865. It learns a lookup-table predictor; it does not invent the majority rule. No calibration, transfer or universal discovery claim follows.

Acquisition compute across all six worlds and40seeds: hybrid_epig: 1.6645s, hybrid_random: 0.0055s, hybrid_roundrobin: 0.0033s, structured_epig: 1.6865s. Separate prediction/update timing is in the summaries. These component timings exclude evaluator queries, serialization and other run overhead; total runtime is6.249seconds. All noise-action counts are zero by design.

## Evidence, reproduction and visualization

One full run: **960episodes,46,080experiments;54tests passed**. Clean source `0eb4d09a4ca462d3f3250aa21f302e41bd76311c`, unchanged throughout. Smoke:24episodes,0.180668s, safety-adjusted projection9.033s against72s gate. Full output about40.52MB; internal120s/external150s caps. No dependencies, paid APIs or extra spending.

[Protocol](../experiments/interactive_lab_v0.md), [all seed/cell summaries](../results/interactive_lab_v0/summary.json), [decision](../results/interactive_lab_v0/decision.json), [metadata](../results/interactive_lab_v0/metadata.json). Six compact evidence files are tracked. Full trajectories remain locally in `results/runs/interactive_lab_v0_20260925`; fresh clones can reproduce them. Seeds400–439 are inspected development data; smoke390 was already inspected in earlier causal work. Sequence seeds1000–1049 remain unused.

The [offline replay](../visualization/interactive_lab.html) embeds the first three declared seeds for all worlds/policies (72episodes), with the full40seed overview. It shows real recorded experiments, pre-outcome predictions and information scores, post-update beliefs, and error curves only through the cursor. Truth is labeled evaluator-only. Play/slider controls replay evidence; no training job runs in the page.

```sh
.venv/bin/python -B -m artificial_scientist.interactive_lab --output results/runs/interactive_lab_smoke_reproduction --smoke
.venv/bin/python -B -m artificial_scientist.interactive_lab --output results/runs/interactive_lab_reproduction --smoke-evidence results/runs/interactive_lab_smoke_reproduction
.venv/bin/python -B visualization/export_interactive_lab.py --run results/runs/interactive_lab_reproduction
```

Use fresh run directories. The full runner requires matching smoke hashes and resource gate. Its internal deadline is120s; the recorded run additionally used a150s subprocess timeout. Claude Opus5.5 reviewed the plan; distinct Codex agents authored core and viewer, independently reviewed code, and audited results. The final audit recomputed all trajectories' evaluator metrics and summaries, and independently checked six saved trajectories' Bayesian/EPIG calculations without resampling. Root matched every embedded replay record and overview cell to raw evidence and tested browser controls. [Review record](review_log.md).

## What comes next

Keep this version fixed. Review a small stateful universe where actions affect future observations and legal actions must be learned. That can test whether planning or an intrinsically motivated RL policy adds value over this greedy active-learning baseline. First preserve the noise and wrong-model controls; the current success does not justify skipping them. Understanding remains the objective, with no required win/lose reward.
