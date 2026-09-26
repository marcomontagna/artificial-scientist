# One equation, independent checks — September 26, 2026

**The integration screen passes; predictive superiority does not.** We can select a formula, independently refit it, and check that same frozen formula. Ordinary pooled BIC recovered more weak terms and had lower mean prediction MSE in all four polynomial families. This is useful statistical infrastructure, not a novel discovery method.

## What ran

60 development seeds (1100–1159) × eight worlds, with three pipelines per dataset: **480 datasets / 1,440 candidates / 30,720 observations**. Each shares a 64-observation budget: A24 selects a support, B24 refits its coefficients, C16 checks it over a wider domain. The fixed six-term and ordinary pooled-BIC baselines fit on A+B48. Different fit allocation is part of this comparison. The supplied grammar is `1,x,u,x²,xu,u²`, with known Gaussian noise σ=0.05.

The first declared affine example (seed1100) outputs `y ≈ 1.09217 + 0.66957x + 0.80282u`. The formula is frozen before C outcomes. Term evidence and whole-form adequacy are separate outputs; neither invents mathematical primitives or proves a law true.

## Main findings

These recalls pool confirmed true terms over all true terms, not the mean of per-dataset ratios.

| True terms confirmed / all true terms | Independent refit | Fixed full | Pooled BIC |
|---|---:|---:|---:|
| Strong affine | 180/180 (100%) | 180/180 (100%) | 180/180 (100%) |
| Strong quadratic | 115/115 (100%) | 115/115 (100%) | 115/115 (100%) |
| Weaker affine | 88/180 (48.9%) | 60/180 (33.3%) | 114/180 (63.3%) |
| Weaker quadratic | 45/115 (39.1%) | 56/115 (48.7%) | 69/115 (60.0%) |

Fixed full also has a valid whole-form check: independent refit wins one weak-family recall comparison and loses the other. In weak quadratic, fixed-full mean extrapolation MSE is0.01366 versus0.02141 for independent refit. The latter's mean per-dataset selection recall is85.6%, but its mean confirmation among selected true terms is47.0% (excluding empty denominators); these means must not be multiplied to obtain the pooled39.1%. Conservative evidence and estimation error are plausible bottlenecks, not isolated causal findings.

Each of the five in-family/noise worlds had **0/60 datasets with any falsely confirmed term**, for each pipeline. These are paired worlds, not 900 independent trials. A single 0/60 cell has a 95% Wilson upper bound of about6.0%; zero observed is not zero risk. Outside-family false-term counts are undefined.

Whole-form rejection for independently refitted strong affine/quadratic models was6/60 each (95% Wilson interval approximately4.7–20.1%). For weak affine it was12/60, including6/52 sufficient and6/8 insufficient selected supports; weak quadratic21/60, including6/45 sufficient and15/15 insufficient. Thus a rejection is not automatically evidence of successful discovery. The fixed-full null control rejected5/60; its five in-family worlds duplicate the same residual experiment and must not be pooled as300 independent tests. The three fixed outside-family functions—exponential, cubic and sine—were each rejected60/60 by both available whole-form checks. This is strong designed misspecification, not demonstrated generalization to arbitrary functions.

Pooled BIC has independent term evidence and prediction metrics, but its whole-form p-value/rejection fields are **unavailable**: the current chi-square derivation does not justify post-selection fitting on the same A+B outcomes. Its better prediction and weak-term recall expose the cost of the extra split. A non-rejected refit is not a certificate that no terms are missing.

## Validity and correction

The whole-form statistic is `Q = rᵀ[σ²(I + X_C(X_BᵀX_B)⁻¹X_Cᵀ)]⁻¹r`, using columns of the selected support. Its χ²16 null requires the true mean to lie in that span; it is conditional on selection/designs and marginal over B/C noise, not conditional on the realized fitted coefficients. Independent term evidence uses the full-family null and threshold120. These are known-method guarantees under stated assumptions, not inferred from a passing empirical screen.

Claude's plan review uncovered overlapping random-stream keys in the **earlier domain study**. Its counts remain descriptive, but prior aggregate independence-based uncertainty claims are unsupported. [Erratum](equation_domain_rng_erratum.md). Historical raw data/source remain unchanged. The current run uses separated streams and a collision regression test.

## Reproduction and next step

Clean source `1ef9ae58974f6767124cad32d2b4c692182d959b`; **96 tests passed**. Full execution took3.599seconds internally (3.677external), producing16,035,957bytes. [Frozen protocol](../experiments/equation_pipeline_v0.md), [compact evidence](../results/equation_pipeline_v0), full local raw directory `results/runs/equation_pipeline_v0_20260926`. Run once, no post-result tuning; reserve1000–1049 untouched. A distinct reviewer independently recomputed all selections, refits, term statistics, valid Q checks and summaries (maximum discrepancy1.60×10⁻¹⁰), with no resampling. Claude Opus5.5 reviewed both plan and results; [critique and our response](pipeline_review_response.md).

Next: review a minimal reject → revise → fresh-check experiment with graded misspecification and ordinary always-large/pooled baselines. Include exact known-noise coefficient testing as an inference baseline, with its different target explicit. This is a proposal, not implemented. Active acquisition and data-fission comparisons are deferred; there is no trained RL policy or novelty claim.
