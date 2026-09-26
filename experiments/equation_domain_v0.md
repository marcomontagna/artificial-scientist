# Domain challenge v0 — provisional diagnostic stage 3

Not approved for implementation or sampling until Claude reviews stage 2 and this plan. The question is whether wider experiments expose wrong polynomial approximations without mistaking coefficient-estimation uncertainty for a wrong law. This is a known linear-regression predictive check, not a new discovery method or grammar repair.

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
