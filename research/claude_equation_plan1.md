**Verdict: revise.** There are two blockers. Both are cheap to fix and neither expands scope. I only read the four files. Nothing was run or sampled, and the numbers below are hand calculations for Codex to check.

**Arithmetic I checked and found correct:** 1+6+15+20 = 42 supports. The sparse_quadratic family has 19 allowed supports. The interpolation grid has 100 points and the extrapolation shell has 81−25 = 56. The budget is 24 fitting + 16 audit = 40 observations. With σ known, `SSE/σ² + k·log n` is BIC up to a constant.

I found no leakage. Truth stays with the evaluator, the audit uses its own input and noise streams, and the predictor is frozen before the audit. The baselines are fair: identical data, no tuning, and a singular fit is reported as a failure.

## Blockers

**B1. The in-class recovery gate can never show false inclusion.** Every in-class true formula has exactly 3 terms, and the search allows at most 3. So in-class errors can only be swaps or missing terms, never extra terms. The BIC penalty is never tested there, and the method is close to "pick the 3 terms with the lowest SSE."

The signal is also very strong. The smallest coefficient is 0.5 against σ = 0.05, and the smallest t-statistic is roughly 10 or more, so the ≥70% threshold is nearly guaranteed. The only test of extra terms is noise_only, and its zero-support recovery is reported but not gated.

My rough estimate: log 24 ≈ 3.18, so a null term enters with P(χ²₁ > 3.18) ≈ 0.075. Across 6 correlated terms, noise-only worlds should pick a nonzero formula in something like 20–40% of seeds. Codex should compute this.

- **Minimal fix:** draw the sparse_quadratic support size uniformly from {1,2,3}, still requiring at least one quadratic term (3 + 12 + 19 allowed supports).
- **Or:** add that as a separate family and pre-register a threshold on noise-only nonzero selection.
- **Either way:** record the expected rates before running.

**B2. The exp(x)+0.5u control is only outside the size-3 limit, not the six supplied terms.** Its best quadratic fit on [−1,1] leaves latent MSE ≈ 7×10⁻⁴, which is below σ² = 0.0025. So the 6-term quadratic baseline fits it essentially within noise and should pass the audit.

The sparse fit is rejected only because of the size cap. Its best 3-term support {1,x,u} leaves latent MSE ≈ 0.026, against a threshold of 0.01.

sin(πx)+0.5u is truly outside the basis, but trivial to detect: the leftover error is ≈ 0.196, about 20× the threshold.

So the adequacy gate is predictably passed and says little about the detector's blind spots. As written, "adequacy passes → propose grammar expansion" would be supported by one control that points to raising k, not adding operators, and another that is trivially easy.

- **Required fix:** relabel exp as "outside the size-≤3 limit" and state that the 6-term baseline should pass it.
- **Required fix:** pre-register the expected audit MSEs (≈0.2 for sin, ≈0.03 for exp).
- **Required fix:** state that an adequacy pass shows only that clearly large misfits are detected.
- **Optional:** a subtle control whose leftover error is below 4σ² would make the gate informative. One example is 0.3x³ with a u term: after its best projection its misfit is ≈ 0.002, which the audit would miss. This is optional because it adds scope.

## Optional refinements (not blockers)

1. **Specify tie-breaking** (smaller k first, then lexicographic support) and what the 1e-10 rank tolerance is relative to (e.g. each column's norm before orthogonalization).
2. **Stage 2 has no headroom.** At this signal level and N = 24, passive recovery is near its ceiling, so active acquisition cannot show a gain. Stage 2 needs a harder, pre-registered regime (smaller N, larger σ, or smaller coefficients), chosen without looking at held-out seeds 1000–1049. Say so now, so a stage-1 pass isn't read as a mandate.
3. **Record the deletions from my original direction.** The heteroscedastic/heavy-tailed noise control and the extrapolation-superiority falsifier were dropped. That's acceptable, but record it, and limit audit claims to known, constant Gaussian noise.
4. **Shared noise makes the per-family gates correlated.** Training noise and inputs are identical across families within a seed, so noise_only, affine and sparse_quadratic results move together. The paired analysis is fine, but don't treat the five gates as independent evidence.
5. **Report audit results per method.** The 6-term baseline passing exp is expected and should not be counted as a sparse-method failure.
6. **Pre-register the predicted numbers:** near-100% recovery at size 3, the noise-only nonzero rate, and both audit MSEs. A large deviation from these calculations then flags a bug rather than a finding.

## Summary

The mathematical and experimental plumbing is sound, and the honest framing (best-subset regression, heuristic weights, no F-test claim) is correct. As written, though, the two gates are close to guaranteed passes: the first by the size cap and signal strength, the second by the choice of controls. Fix B1 so that extra terms can actually occur and are gated. Fix B2 so the exp control is labeled for what it tests and the expected audit results are stated before the run. Then approve.
