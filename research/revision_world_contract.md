# Independently authored revision worlds

Evaluator source independently reviewed by the root coordinator, for a scoped freeze before learner tuning or execution. Learner thresholds were drafted concurrently; this does not imply a blind threshold selection. No learner was run and no study seed was inspected. This is source separation, not formal blinding: the coordinator and reviewer can inspect the code. There is no claim of new physical science or of universal model inadequacy.

## Public contract

`make_revision_world(seed, variant)` returns an evaluator-owned object with `initial`, `step(Action)` and `consumed`. The runtime learner receives only the existing immutable `Observation(tick,x,y)` and action contract. Do not pass the object, variant label, hidden states or source into model search or planning.

Exactly the existing tools and costs apply: observe/push cost one tick, wait costs 1–8 ticks, reset costs eight. An 80-unit ceiling rejects an unaffordable action before any mutation. Invalid commands raise ValueError and are not executed experiments. Initial is a cached observation, not a source of free repeated readings. A push applies once. Every elapsed tick consumes sensor noise, even intermediate unobserved wait ticks. Reset holds the object at home/rest for eight ticks, clears any hidden physical memory, retains the law, and does not rewind noise or global time. No evaluator result changes the learner's budget.

The implementation reuses the frozen `lab_world.py` tool engine and `lab_api.py`. Both are provenance dependencies and must be hashed with `revision_world.py`. Sensor standard deviation is 0.01 in every variant; only noisy positions and ticks are public. Seeds vary sensor noise, not law families. Pairing a seed across variants/policies creates shared randomness, not independent replications.

## Evaluator specification — not learner inputs

- **Control:** the exact existing development law, unchanged, via a wrapper.
- **Challenge:** a fixed stable two-dimensional momentum coupling with identical current-input gain on both coordinates. It requires relaxing independent-coordinate/shared-coefficient modeling assumptions. It is not the old challenge law. Exact coefficients are frozen in source rather than supplied to the learner.
- **Stress:** a damped system with a fixed delayed actuator contribution stored in hidden physical memory. Instantaneous visible motion and a very short input history do not explicitly contain that pending drive. A predictor with sufficient history or suitable latent state could model it; this is a stress test of a declared short-memory language, not impossibility for every learner. Exact finite-history limitations must be checked against the eventual learner specification. Long waits may conceal the intervening motion. No change time, label or special error message reveals the mechanism.

All laws remain fixed through the run. Velocities are stable under bounded input; positions may drift in the unbounded plane. Reset's full-state restoration is an explicit experimental privilege. There is no scripted winning trajectory, success reward or teacher hint. These worlds were selected to test modeling assumptions, so passing them would not demonstrate generalization to arbitrary worlds or an unscripted conceptual breakthrough.

## Verification and freeze

Only synthetic fixture seeds 7/11 are used for tests: deterministic repeatability, original-control equality, wait batching, reset/noise/timing semantics, whole-action budget atomicity, delayed/cross-coordinate responses, and finite bounded-budget execution. These are simulator tests, not learner evaluations. Following root source review, the author will commit only this contract, `artificial_scientist/revision_world.py` and `tests/test_revision_world.py` after a different agent reviews them. Record the resulting commit before learner tuning or demonstrations; no coefficient adjustment based on learner outcomes is permitted.
