**Verdict:** The design is mostly sound and does what NEXT_STEPS item 1 asks: one equation is selected on A, refitted on B and frozen, then gets separate term-evidence and whole-form checks on C. Two things need fixing before any sampling. One is a real defect in the seed offsets. The other is a gap in the baselines if you want to draw any comparative conclusion.

## Blockers

**1. The random-number streams overlap across seeds (`equation_pipeline_v0.md:9`).** Each stream uses `Random(offset+seed)`, and the six offsets (12100001, …03, …07, …09, …13, …17) are only 2–16 apart. The seeds run 1100–1159, which is a 59-wide range. So, for example, A-inputs for seed 1102 get `Random(12101103)`, which is exactly A-noise for seed 1100. Python's `gauss` consumes the same underlying `random()` draws, so seed 1100's noise is a fixed transform of seed 1102's input sites. Many other pairs collide the same way.

Within one seed the streams are still distinct, so the planned "disjoint RNG" test would probably pass. But the per-seed Wilson and paired normal intervals assume seeds are independent, and that assumption is broken. Earlier studies avoided this by spacing offsets about 1e5 apart (`equation_discovery.py:275-276`). Respace the offsets, and add a test that the set of all `offset+seed` values across every stream, seed, smoke run and fixture has no duplicates.

**2. The only comparator is the always-dense model.** `fixed_full` fits 6 terms and then extrapolates to C on [-2,2]², where its prediction variance is large. That makes it a weak opponent for the MSE comparison. The obvious ordinary baseline is missing: BIC selection on the pooled A+B (48 observations, no split), then the same C checks. It costs no extra observations because it reuses the same 64.

Its term evidence would still be valid, since C is independent. Its Q statistic would not be exactly χ²₁₆ after selection, and that difference is precisely what would show whether splitting earns its cost. Either add this arm, or cut the protocol's comparative language (the "paired selected-minus-full differences") down to pure integration reporting. As written, the comparison can't show that the split approach is better than ordinary practice.

## Checks that hold up

- **Adequacy null.** A is independent of B and C. If the true function lies in span(S), then r = ε_C − A_C(XᵀX)⁻¹Xᵀε_B, which is Gaussian with covariance V, so Q ~ χ²₁₆ marginally over the B and C noise. The empty-support case (V = σ²I) is correct. The null scope for `selected_refit` is stated honestly.
- **Term bound.** The candidate is independent of C, and the null fit always has at least the likelihood of the truth. So each false term has P(E ≥ 120) ≤ 1/120. Summed over terms, that gives ≤ 3/120 for `selected_refit` and exactly 6/120 = .05 for `fixed_full`. The claim "≤ .05, conservative" is correct, and validity doesn't depend on span(S) being sufficient. The guard for non-selected terms (`equation_confirmation.py:35`) still applies.
- **Budgets.** Both arms use 64 observations. The fact that the baseline uses 48 for fitting versus 24 is declared up front.
- **Data reuse.** The shared use of C is declared, with no evidence multiplication. The qualified flag's false-term rate is still bounded by the term bound.

## Recommended (not blocking)

- **Duplicate data within a seed is heavier than the protocol admits.** In all five in-family worlds, `fixed_full` residuals depend only on the noise. So Q and every false-term log E are identical across those worlds for a given seed. The same is true for `selected_refit` whenever S is sufficient and the same. Effective calibration n is therefore 60, not 300, and the per-family "≤ 6/60" screens are nested rather than separate. Add this invariance as a test (it's a strong implementation check), and state n = 60 in the report.
- **No predeclared calibration warning for adequacy.** Conditioning on sufficiency depends only on A, so the `fixed_full` in-family rate and the sufficient-conditioned `selected_refit` rates are exact-size checks. Predeclare a warning, e.g. `fixed_full` rejections > 8/60 trigger review, instead of keeping them purely descriptive.
- **Multiplicity in the screen.** There are 10 family×pipeline false-claim screens. At the nominal bound, P(Bin(60,.05) ≥ 7) ≈ .03 each. The real rate is probably far below that, because the Markov bound is loose, but state the expected false-alarm rate of the screen.
- **"Weak" may not be weak for affine terms.** With β = .1 on 24 observations in A, a linear term has noncentrality ≈ 32. Weak quadratics are ≈ 2–9. Report evaluator-side theoretical noncentralities so the weak results can be interpreted.
- **Rejection-rate differences.** Paired selected-minus-full rejection differences compare tests with different nulls. Label them as describing different nulls, not as power differences.
- **The recall ≥ .80 threshold was never derived.** C on [-2,2]² differs from stage 2's audit domain, so this is new ground. It's probably easy for strong coefficients, but it's untested.

## Future work, correctly deferred

Unknown σ, grammar revision, and observation-efficient challenge design (NEXT_STEPS items 2–3) are rightly kept out of this protocol.

**Bottom line:** After fixing the offsets and either adding the pooled-BIC arm or dropping the comparative claims, this is a valid, bounded integration experiment. The comparative results tell you little until then.
