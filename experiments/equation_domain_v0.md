# Domain challenge v0 — diagnostic stage 3

Claude reviewed stage 2 and this plan; the additions below address its presampling objections. Final independent approval is required before implementation. The question is whether wider experiments expose wrong polynomial approximations without mistaking coefficient-estimation uncertainty for a wrong law. This is a known linear-regression predictive check, not a new discovery method or grammar repair.

## Fixed model and equal budgets

Use the unchanged full six-term quadratic OLS baseline, never a selected sparse formula. Fit 24 observations at 12 duplicated uniform sites in [-1,1]^2, sigma=.05. Same generator and training streams as stage 1. New development seeds850–889 (40), smoke840, fixtures7/11. Six families: affine, sparse_quadratic and noise_only as in stage1; exp(x)+.5u; .3*x^3+.5u (new subtle omitted-operator control); sin(pi*x)+.5u. Supplied variables and basis remain unchanged. Evaluator grids are exactly stage1:100interpolation points and56extrapolation-shell points.

Two preselected audit arms each collect16 independent observations. Generate16base uniform points in[-1,1]^2 with Random(10100009+seed), and16Gaussian noise draws with Random(10100011+seed). Local uses the base points; wide multiplies both coordinates by2. Share noise by index and share the24training observations across arms. Each arm costs40observations; the paired dataset costs56unique observations, not40. Full240datasets,480audits,13,440unique observations. No domain is chosen from fitted coefficients or earlier audit outcomes. Fit is frozen; audits do not retrain it.

## Two diagnostic rules on each arm

Crude rule: reject if mean squared audit residual>.01, as in stage1. This ignores coefficient-estimation uncertainty.

Primary rule: let X be the24x6 training design, A the16x6 audit design, b the fixed full OLS estimate, and r=y_audit-A*b. Under the full quadratic family and independent known Gaussian noise,

    V = sigma^2 * [I_16 + A*(X^T*X)^(-1)*A^T]
    Q = r^T*V^(-1)*r

Conditional on the two designs, and marginal over BOTH training and audit noise, Q has a chi-square distribution with16degrees of freedom. This is not a guarantee conditional on the realized fitted coefficients. For outside-basis families, no such null calibration is claimed. Fixed full-model fitting avoids importing this statement into post-selection sparse inference.

Compute training QR with the same two-pass orthogonalization/rank tolerance as stage1. For each audit feature vector a, solve R^T*z=a; coefficient covariance contribution is z_i dot z_j. Form V and use a Cholesky solve, never an unchecked matrix inverse. Reject numerical/rank failures without resampling designs. Record Q, log survival probability and rejection when log_p<=log(.05). For df16, survival(Q)=exp(-Q/2)*sum_{k=0}^7 (Q/2)^k/k!; evaluate in log space, with Q=0 giving log_p=0. Negative Q beyond1e-10 is a failure; tiny negative roundoff clamps to0.

Each domain has nominal size.05 separately. The event 'either domain rejects' is not advertised as a.05test; report each arm separately. Shared noise and coordinate pairing are not independent replications. No pooling across families to hide failures.

## Prespecified questions and screen

Primary contrast: wide minus local rejection rate for the uncertainty-aware rule in EACH exponential and cubic family. Require gain>=.30 (at least12/40 paired net additional rejections) in EACH family, while observed false-reject rate<=.10 (at most4/40) in EACH affine/quadratic/noise control for EACH arm. All480audits must be complete. These empirical tolerances are distinct from nominal test size and do not establish calibration by themselves.

Report all six families and both rules: rejection counts/Wilson95intervals; paired differences with SE/descriptive normal95intervals; audit MSE; evaluator-only interpolation and extrapolation latent MSE; both trace(V) including observation noise and trace(V)-16*sigma² excluding it. Conditioning diagnostics are min/max absolute training-R diagonal ratio and minimum Cholesky diagonal of V; these are numerical proxies, not matrix condition numbers. Report the number of local non-rejections followed by wide rejections as a descriptive subset, not as an independently calibrated conditional test. Sine is a positive control, not part of the gain threshold; its local detection may already be at a ceiling.

Widening can amplify both misspecification signal and parameter uncertainty, so benefit is not assumed. If the screen fails, report that and stop. Do not add operators, tune sigma, change audit locations or train a policy afterward. This is the third and final authorized experiment tonight; synthesize findings and remaining gaps.

## Execution and verification

One process, internal120seconds/external150seconds, max50MB. Smoke6datasets/12audits; full240datasets/480audits. Go only if1.5*(240/6)*smoke elapsed<=60seconds and the same projection for bytes<=40MB. Fresh results/runs/equation_domain_*; source/helper/protocol/test/config hashes, matching smoke, clean source commit before full, no overwrites or partial-run passes. No new dependencies or extra spending.

Tests: independent small-matrix covariance/whitening examples; a diagonal chi-square tail fixture and monotonicity; rank failure; known positive-definite solve; correct domain/noise coupling; predictions unchanged by audit; 40-versus56budget accounting; complete grid and all per-family gates; provenance/time/disk protection. Independent code/data review and final Claude interpretation are required.

The three in-class/noise controls share design and noise. Full OLS removes their polynomial means exactly, so their residuals and rejection decisions should agree up to numerical precision; they are not three independent calibration replications.

## Presampling resolutions from Claude

The independent stage2 raw-data audit is complete and recorded in research/review_log.md. Each outside family here is one fixed function with40random designs/noise draws; these are not40independent sampled laws. This is a predictable validation of known regression theory, not a discovery result.

Record evaluator-only noncentrality and theoretical power on every audit. Fit noiseless training means to the same full six-term design to obtain b0. Let delta=f(A)-A*b0, lambda=delta^T*V^(-1)*delta. Under each fixed function, conditional on the designs and marginal over both noise sources, Q follows noncentral chi-square16(lambda). Do NOT use the realized noisy fit to define lambda. No hidden law, lambda or power may influence fitting, audit locations or rejection. Log the noiseless coefficients, delta, lambda and theoretical power; report mean power next to observed rejection in each cell.

Find the central 95%critical value by80bisections on[0,128] using the fixed df16 survival formula. Power is1 minus the Poisson(lambda/2) mixture of central chi-square CDFs with df16+2j. Sum Poisson components j=0..128, computing weights individually in log space (special-case lambda=0). Compute each integer-shape gamma CDF with the positive series exp(-z)*sum_{k=shape}^infinity z^k/k!, not subtraction from1. Stop its positive tail when the geometric remainder bound is below1e-15; cap1000terms and fail if not converged. The omitted mixture CDF is bounded by GammaCDF(shape137,z=critical/2), below8.28e-88. Use fsum and validate finite probabilities, allowing clamping only within1e-12 of[0,1]. No new dependencies or Monte Carlo power estimates. Add independent fixtures for lambda0 (power.05), monotonicity and nonzero reference values.

Keep the gain gate unchanged. If cubic wide rejection is high but its gain fails because local detection is already high, the comparative screen still FAILS; report the local ceiling and absolute detection in both arms. This does not mean the wide test lacks detection power. Report these absolute rates regardless of outcome. No retrospective threshold or amplitude changes.

Assert the three in-class/noise controls have matching Q per seed/arm within absolute1e-8 plus relative1e-10; a discrepancy fails the run rather than being treated as three replications. Their effective calibration sample remains40per arm. Report empirical p-value quantiles at0,.25,.5,.75,1 using linear interpolation of sorted values. These summaries and a small empirical error gate cannot establish uniform calibration; the proof and numerical fixtures provide the stated model-specific basis. The crude MSE threshold intentionally ignores growing coefficient uncertainty on the wide arm; its false rejections do not show that the underlying polynomial law is wrong.

Primary numerical reference: [Boost noncentral chi-square documentation](https://www.boost.org/doc/libs/latest/libs/math/doc/html/math_toolkit/dist_ref/dists/nc_chi_squared_dist.html). The implementation remains a small independently checked standard-library calculation, not a Boost dependency.
