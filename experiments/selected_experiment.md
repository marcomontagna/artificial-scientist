# Selected experiment: acquisition objectives under hidden shifts

Protocol v1, 2026-09-25. Author: Codex primary. Research design only; not implemented or run. This is a replication/stress test of known acquisition ideas, not evidence of a novel paradigm. Implementation begins tomorrow after user review. Any substantive revision must be logged before test evaluation.

## Question and preregistered decision

Does EPIG acquisition improve target-distribution prediction after a hidden probability change relative to EIG and uniform acquisition, when all use the same change-adaptive filter? Does the answer survive model misspecification without harming stationary performance?

Primary comparison: EPIG minus each of EIG and uniform in mean post-change expected log loss (nats), in the misspecified switching condition with q=(0.45,0.45,0.10). Practical success requires BOTH paired differences' 95% interval upper bounds below -0.01 and the stationary misspecified penalty upper bound no more than +0.01 against BOTH comparators. This is a conservative conjunctive decision; no selection of a winning comparator. Otherwise report failed or inconclusive, not supported. The 0.01 tolerance is a chosen engineering threshold, not a literature constant or power guarantee.

## Environment and information boundary

Three actions a=0,1,2 return a binary observation. Four candidate laws, known equally to all finite-model learners:

| h | p(y=1\|a=0) | a=1 | a=2 |
| --- | ---: | ---: | ---: |
| 0 | .20 | .20 | .50 |
| 1 | .80 | .20 | .50 |
| 2 | .20 | .80 | .90 |
| 3 | .80 | .80 | .10 |

Episodes last 400 ticks. One training query per tick, unit cost, no stopping early. Switching conditions choose ordered distinct law indices; stationary conditions keep the initial index. The evaluator owns actual index, time and probability vector; learner methods never receive them. The learner receives q, candidate table, its own query/outcome history and fixed hyperparameters. This gives a known model family, not discovery of the laws themselves.

Four conditions: stationary/matched, switching/matched, stationary/misspecified, switching/misspecified. Here matched means likelihood-matched only: a single scheduled switch or no switch differs from the filter’s geometric-reset process, so all conditions retain temporal-model mismatch. In misspecified conditions add a fixed 0.10*d offset to every true vector within an episode, clipping to [.05,.95]; the model table is unchanged. Development uses d=(+1,-1,+1); held-out evaluation uses d=(+1,+1,-1) and (-1,+1,+1), reported separately and equally weighted for the primary aggregate. Misspecification means the conditional law is not one of the four hypotheses, not that no mixture can approximate its mean.

Development: seeds 0–9; all 12 ordered law pairs; switching at tick 200. Stationary episodes use each initial law once per seed. Evaluation: seeds 1000–1039; same balanced law pairs but a fresh per-episode change time uniformly drawn from integers 160–240; stationary uses evaluator-only pseudo-change time from that range for equal windows. These are held-out noise/schedules/misspecification directions, NOT held-out law families. q uniform is a separate sensitivity analysis; it does not alter the primary decision. Use shared evaluator uniforms U(seed,condition,pair,d,t,a) across policies and independent policy RNG streams; same action at same tick yields same observation across methods. Do not count actions or ticks as independent statistical replicates.

## Matched inference and acquisition

The four-state filter begins uniform. Before each tick, mix previous posterior with uniform prior: w_minus(h)=(1-hazard)*w(h)+hazard/4; predict with w_minus. After one selected observation, multiply by its Bernoulli likelihood and normalize. Hazard is a reset probability that permits returning to the same state, not a known switch indicator. No oracle resets. Choose ONE shared hazard from {0.005,0.02,0.05} using uniform acquisition's full-episode mean development expected log loss under primary q=(0.45,0.45,0.10), averaged within each condition and then equally across all four development conditions; ties select the smaller hazard. Freeze for all finite-filter policies, q settings and evaluation directions. This isolates acquisition choice; it is not a claim of globally optimal policy-specific tuning.

Policies: uniform random; round-robin; EIG; EPIG; EPIG with probability .10 replaced by a uniform action. Break acquisition ties uniformly using policy RNG. EIG maximizes I(H;Y_a) under w_minus. EPIG maximizes sum_b q_b I(Y_a;Y_b*) where Y_a and Y_b* are independent draws conditional on the SAME hypothesized state: joint mass for y,z is sum_h w_minus(h) Bern(y;p_ha) Bern(z;p_hb). Even for a=b, use distinct conditionally independent draws; do not set Y_b*=Y_a. This is a one-step frozen-state acquisition surrogate, not an optimal long-horizon changing-state design. Use exact binary sums and natural logs, handling zero terms as zero.

Model-flexibility control: per-action Beta(1,1) with last W observations per action and uniform queries, W in {10,20,50} selected on the same development objective; ties choose the smaller W. This is a robustness comparator, not part of the acquisition-only causal attribution. A true-probability oracle provides an evaluator entropy floor only, never training data. No neural networks, MLX, architecture search, or external models needed.

## Metrics, leakage and uncertainty

At each tick, BEFORE the training query/update, evaluator computes expected log loss across every action using hidden true p and the learner's predictions: sum_a q_a[-p_a log(pred_a)-(1-p_a)log(1-pred_a)]. This exact expectation removes evaluation sampling noise and policy sampling bias; truth and scores never go back to the learner. Clip predictions at 1e-12 for scoring, matching existing conventions. Excess log loss subtracts the same true entropy floor. Primary per-episode endpoint: mean loss for 100 ticks beginning at the hidden change or stationary pseudo-change. Average pairs/directions within each seed first. Keep full episode-level results as well.

Use 2,000 paired bootstrap resamples of the 40 seed-cluster means, fixed bootstrap seed 20260925, percentile 95% intervals. Report both primary comparisons and every condition/direction, even unfavorable ones. Small effective sample size and toy-law dependence remain limitations; do not manufacture power claims.

Secondary: expected Brier, whole-episode loss, per-action error, query allocation, wall time, and recovery defined as the first 20-tick moving mean excess loss <=.02 using only post-change ticks (first eligible window ends at tick tau+19); count nonrecoveries as censored by horizon and report their fraction. Show curves; this criterion is not a detection-alarm metric. Calibration is descriptive only: 10 fixed bins of prequential predictions, weighted by q across all actions; show bin counts and weighted true frequencies from simulator expectations. Do not call proper scores or this toy reliability plot a calibration guarantee. No causal-identification claim.

## Tomorrow's implementation and stop rules

1. Add a separate runner/config; preserve existing smoke code and results. Unit tests: normalized Bayesian updates, entropy/MI sanity, nonnegative MI, distinct same-action EPIG draws, prediction-before-update, hidden-state nonleakage, shared RNG and deterministic reproduction. Have another agent review code and protocol adherence.
2. Run a development microbenchmark (2 seeds, <=50 ticks) and tests. If projected full evaluation exceeds 10 minutes per process or 60 minutes aggregate, split into bounded seed batches without changing protocol, or stop and report feasibility failure. Do not silently reduce seeds after viewing outcomes. Keep <=2 GB memory and <=500 MB new disk; stream logs.
3. Tune only the specified development hyperparameters. Freeze config, source revision, seed list, q, endpoint, thresholds and analysis before evaluating held-out seeds. No modifications in response to test results without a new exploratory protocol/version.
4. Record machine/Python, commands, config/source hashes, all failures, selected hyperparameters, all metrics and per-seed data. One experiment process at a time; no downloads or paid compute.

Existing verification command: `python3 -m unittest discover -s tests -v`. No new experiment command exists yet; the implementing agent must record its actual runnable command when created. A negative result is useful: stop adding architecture and first determine whether known sensing/inference tradeoffs explain the outcome.
