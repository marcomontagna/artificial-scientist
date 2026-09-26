I ran the review read-only: no edits and no shell. I didn't run the Python script you pasted.

# Critic review: `experiments/equation_revision_v0.md`

**Verdict: the math is mostly sound, but the design can't answer its own question. Don't implement it as written.**

## What checks out
- **Q statistic:** the covariance V and the χ²_|E| null (lines 25–27) are correct for a fixed OLS support. Conditioning on selection from A+C keeps the final B→D test valid. The survival formula for even degrees of freedom is correct.
- **Union bound:** it holds for span-true worlds. A false revision in the quadratic world still contains the truth, so the final null stays true.
- **Candidate likelihood evidence:** this is a valid split-likelihood-ratio e-value (universal inference). The candidate is frozen before D and the null's MLE is fitted on D. Markov's inequality then gives the eight-test bound.

## Blockers
1. **The threshold is ambiguous (line 32).** It defines log E but thresholds E≥160. Specify `log E ≥ ln 160 ≈ 5.075` and test for it explicitly. Otherwise an implementation can compare log E against 160 and never confirm anything.
2. **The "extrapolation" grid isn't extrapolation for B-fitted models.** `equation_discovery.py:165,283` builds the grid from the axis {−2,…,2} and keeps points with max(|x|,|u|)>1. All 56 points lie inside B's and D's domain [−2,2]². The line-42 gate therefore measures interpolation in the shell region. Rename it, or add a grid beyond ±2.
3. **Most outcomes can be computed before sampling.** For fixed supports with fixed designs and known σ, the expected grid MSE is exactly bias² plus variance, and trigger power is a noncentral χ² with computable noncentrality. Only the selection step needs simulation. Calculate and preregister these predictions first. As written, the thresholds are called "engineering targets" when they could be derived.
4. **The always_large gate is really a trigger-power requirement.** My rough hand estimate, not verified: in medium_x, never_revise has squared bias of about 0.007 on the shell grid, while always_large pays only a small variance cost from two extra terms on 24 points. Passing `revise_once ≤ always_large` would then need trigger power of roughly ≥0.95. The same estimate puts medium_x trigger power near 0.6–0.8, because extrapolating from A's 12 duplicated sites in [−1,1]² to C inflates V. Expect this gate to fail for predictable reasons. Compute it now (blocker 3).
5. **The baselines are unfair in both directions.** never_revise and always_large throw away 40 of the 88 observations, so "same total budget" (line 21) is misleading framing. The utility gate also leaves out pooled_bic and fixed models fitted on all 64 pre-D observations, which are the competitors that matter. Prior results already show pooled BIC winning. Add always_large on A+C+B to the gate.
6. **pooled_bic gets no whole-form check without need.** A D-only nested test of the selected support against full8 (χ² with 8−|S| degrees of freedom, known σ) is valid for every pipeline, because D is independent of all selection. Use it as the common check.

## Smaller issues
- **The noise world duplicates the quadratic world.** Every residual statistic (trigger, selection SSE, Q, latent MSE error) is identical when the truth is in the span. Line 40 admits this, but line 42 still gates "EACH" control, which is one check counted twice.
- **"BIC" in step 2 is just minimum SSE.** Both candidates have seven parameters, so say so.
- **A's duplicated sites need a reason.** Replicates help lack-of-fit tests when σ is unknown. Here σ is known, and duplication reduces design spread and trigger power.
- **Revision is forced after rejection.** The learner can't choose "neither" or full8, so the both-cubic and exponential worlds are fixed by construction, not measured.
- **Rank failure handling is unclear.** "Rank failure invalidates the run" doesn't say whether that means one dataset or the whole study.

## Direction challenge
With only two supplied candidate terms, always_large is nearly free, and a reject→revise loop has no regime where it could win. The most likely outcome repeats the last study: pooled selection wins and revision ties or loses. That also doesn't move toward *discovering* equations, because picking one of two given cubics is support selection, not revision.

Revision only has a reason to exist when:
- the candidate library is large compared with n (say 15–30 supplied terms against 24 points per stage), so always_large is infeasible or ill-conditioned; and
- searching pooled over all subsets has a real multiplicity cost.

Only then can trigger, targeted proposal and fresh check beat the alternatives. The proposal step should also use the residual structure on C (e.g. correlate residuals with the candidate terms). A blind forced choice doesn't do that.

**Recommendation:** first do the analytic power and MSE calculation (no sampling) for the current worlds. If it confirms blocker 4, redesign around a large library before spending seeds 1200–1259. The current protocol would mostly confirm what can already be calculated.
