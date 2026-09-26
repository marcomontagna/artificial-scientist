**Verdict: REVISE.** The design is sound and appropriately scoped. Three preregistration gaps need fixing before implementation.

## Correctness of acquisition
- The score is Hmean(current) − Σ_y p(y|a,D)·Hmean(after hypothetical update). With a uniform target, this is the mutual information between one experiment's outcome and a future query outcome under the hybrid posterior predictive, i.e. EPIG. It is non-negative and correctly credited to Bickford Smith et al.
- The hybrid update is coherent. The Beta fallback's sequential marginal likelihood is its current posterior-predictive probability, so "normalized pre-outcome likelihoods" gives the right mixture reweighting.
- The acquisition objective is the evaluation metric (uniform-query predictive entropy vs uniform-query log loss). That is legitimate, but the report must say so: the primary policy is directly optimizing what it is scored on, and the baselines are not.

## Blockers
1. **The AUC scale is undefined.** "Area under excess-query-log-loss curve over steps 1..48" could be a sum or a per-step mean, and these differ 48×. So the −0.01 nats screen has no fixed meaning. Specify the normalization, e.g. mean over steps 1..48 in nats per query-cell per step.
2. **Noise action vs tie tolerance.** Action8 scores exactly 0. The switch actions' EPIG can fall within 1e-12 of 0, or come out slightly negative from float error, once the posterior collapses. This is especially likely for structured-only, where there is no Beta residual uncertainty. Then action8 can win or tie, and the acquisition policies would silently spend observations on the noise lamp while baselines never do. Required:
   - Clamp scores ≥ 0 and compute them in log-space.
   - Preregister what happens in this case: either allow it and report it, or restrict to switch actions when all scores are ≤ tolerance.
   - Record how often action8 is chosen per policy and cell.
3. **No preregistered consequence for the screen.** "Save … decision" is stated, but pass and fail outcomes aren't mapped to anything. Say what each outcome licenses. For example: pass → only "EPIG beats random/round-robin in this well-specified finite toy"; fail → report it and do not iterate the acquisition function. Also state that the majority and fair-noise cells can't turn a failing primary into a pass.

## Evaluation fairness, uncertainty, controls
- **The worlds are built to favour the library.** All four primary worlds are exactly in the library, with matching noise levels of 0.05/0.20. Any win is expected by construction in a well-specified finite hypothesis space. It shows the integration works, not that the method copes with realistic conditions. Say this explicitly in RESULTS.
- **Round-robin is a strong baseline:** with 48 steps it samples each cell exactly 6 times, which is near-optimal for uniform-target prediction. A null result against it is plausible and should not be read as an implementation failure.
- **Correlation across worlds:** the noise uniforms are keyed by (seed, step, action), not by world, so the worlds are correlated within a seed. Averaging within each seed and then taking SE over 40 seeds handles this correctly. Also state whether the policy RNG is keyed by world.
- Normal intervals with n=40 are fine as descriptive intervals; t₃₉ would widen them by only about 3%.
- The majority cell only compares hybrid vs structured-only, which is reasonable. Also report both acquisition policies against random/round-robin there, so the cost of misspecification is visible.

## Optional improvements
- Add a secondary identification metric: posterior mass on the true hypothesis, or on the fallback in the majority cell. The plan calls itself "understanding-first", but log loss only measures prediction.
- Store posterior weights in log-space. Underflow isn't reached in 48 steps (0.05⁴⁸ ≈ 1e-63), but log-space is safer.
- The smoke seed 390 was already used in `causal_diagnostic_v0` (seeds 200..399, `artificial_scientist/causal_diagnostic.py:299`). It's harmless for a smoke run, but don't call it new. Seeds 400..439 do look unused.
- The library includes XOR but not XNOR, NAND or NOR, so it isn't symmetric under bit flips. Disclose this, since it shapes the first-step ties.
- Add unit tests for:
  - hypothetical updates leave live state unchanged (hash it before and after scoring);
  - scores ≥ 0;
  - a hand-computed EPIG on a 2-hypothesis fixture;
  - noise and query data never reach learner updates.

## Feasibility
- Only the primary and structured-only policies run acquisition: about 23k acquisition steps × 9 actions × 2 outcomes × 36 components × 8 cells ≈ 1.2e8 inner operations in pure Python. That is plausible within 120 s, but not certain once per-step timing and full trajectory logging are added.
  - Precompute the hypothesis × cell prediction table.
  - Make the smoke run project total runtime and abort before the full run if it exceeds about 60% of the cap.
- Output is roughly 20–30 MB of trajectories, under 100 MB. The self-contained HTML replay should embed a declared subset, or load the JSON offline, rather than inlining everything.

## Claims
The scoping is appropriately modest: it's framed as an integration of known methods, with no novelty, calibration, generalization or autonomy claims, and the prior art is cited correctly.

- Remove "understanding-first" as a descriptor unless the identification metric above is added.
- Label the replay as a playback of recorded runs, as the plan already intends.
