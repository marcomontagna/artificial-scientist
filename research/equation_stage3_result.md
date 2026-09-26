# Domain challenge v0 — result

**Erratum:** [38 cross-seed RNG collisions](equation_domain_rng_erratum.md) were found during the next protocol review. Counts and the engineering screen remain descriptive; the independence-based aggregate intervals below are not validated uncertainty estimates. Raw artifacts remain unchanged.

**The fixed comparative screen passed.** This is a numerical/Monte Carlo validation of known regression theory: wider tests exposed the designed wrong quadratic approximations while the uncertainty-aware test retained the same observed false-rejection rate on correct polynomial controls. Supplied variables, known Gaussian noise and strong in-class coefficients favor the method.

| Fixed family, 40 designs each | Local rejections | Wide rejections | Mean theoretical power, local / wide |
|---|---:|---:|---:|
| Exponential | 10/40 | 40/40 | 23.8% / approximately 100% |
| Cubic | 26/40 | 40/40 | 62.8% / approximately 100% |
| Sine | 40/40 | 40/40 | approximately 100% / 100% |
| Affine | 2/40 | 2/40 | 5% / 5% |
| Sparse quadratic | 2/40 | 2/40 | 5% / 5% |
| Noise | 2/40 | 2/40 | 5% / 5% |

The paired wide-minus-local gains were 75 percentage points for exponential (previously calculated normal interval61.4–88.6; coverage unvalidated due to RNG reuse) and 35 points for cubic (previously calculated interval20.0–50.0; same limitation). Both point estimates pass the prespecified 30-point threshold; this is not evidence that the population cubic gain exceeds 30 points. The wide test rejected 30 exponential and 14 cubic cases that the local test did not. Sine already reached the local detection ceiling.

For each correct-model control, the crude audit-MSE threshold rejected 29/40 wide tests versus 2/40 with coefficient uncertainty included. That is the intended counterexample: extrapolation amplifies estimation error even when the mathematical family is correct. The three controls share design and noise and yield identical residual checks up to rounding, so they provide only40recorded datasets per arm, not120independent replications. The previously calculated Wilson intervals were1.4–16.5% for2/40 and91.2–100% for40/40; their coverage is unvalidated due to RNG reuse. This small correlated run does not empirically establish calibration.

The fixed full quadratic fit uses 24 observations. Each arm then uses 16 fresh observations: 40 per arm, 56 unique per paired dataset. Local audit coordinates lie in [-1,1]^2; wide coordinates are twice the same base coordinates. Audit noise is paired. Fits and domain choices never change after outcomes.

The test uses Q=r^T V^-1 r, with V=sigma²[I+A(X^T X)^-1 A^T] and known sigma=.05. For a correct full quadratic mean, Q is chi-square with 16 degrees of freedom conditional on designs and marginal over training AND audit noise. This statement does not apply to a selected sparse fit or to adaptive reuse. Under each specified non-polynomial mean, evaluator-only noncentrality predicts the observed power; no hidden quantities influence the learner or rejection.

Mean total audit variance trace grew from 0.07633 locally to 0.54071 widely; excluding observation noise it grew from 0.03633 to 0.50071. Control p-value medians were 0.4916 and 0.4594. Full quantiles, numerical proxies, prediction MSEs and per-seed contrasts are in the compact summary. Extremely small displayed probabilities may underflow to zero; decisions use finite log probabilities. Roundoff may put raw Wilson endpoints a few ulps outside [0,1]; displayed endpoints are rounded.

One full run from clean `7b19220` completed 240 datasets, 480 audits and 13,440 unique observations. All 90 tests passed before sampling. Internal runtime 0.298314 seconds; external process wall 0.344123 seconds; artifacts 1,771,409 bytes. No post-result tuning. A distinct reviewer independently solved the observed and noiseless fits, covariance systems and all 480 statistics/power values, then recomputed every summary and gate; maximum discrepancy was 2.73e-11. Exact grid, source/artifact hashes and smoke linkage were verified without resampling. Claude subsequently agreed with the mathematics and required more explicit validation-only framing; its unchanged critique and the coordinator response are recorded.

**Limits and decision:** this validates known regression theory on three fixed outside-family functions across random designs, not a population of new laws. The agent did not select the wider domain, invent an operator or repair its equation. This is the third and final study in the authorized sequence. Stop sampling. Following Claude’s final critique, first review one valid same-equation selection/refit/check object, then target observation efficiency from learner-chosen challenge locations rather than subsecond fitting-cost savings. [Reproduction](equation_reproduction.md).

The stage1 dense exponential MSE test rejected1/20 cases; this study’s local uncertainty-aware AND crude MSE tests each rejected10/40. Different seeds and audit designs, as well as different test definitions for the primary statistic, prevent a controlled cross-study attribution. The contrast is not evidence that changing the test alone caused the difference.
