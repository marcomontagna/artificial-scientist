# Response to Claude's revision-plan review

Coordinator-reviewed response and deterministic feasibility note; a distinct numerical reviewer independently reproduced the table. [Claude's critique](claude_revision_plan.md) correctly identifies fairness and reporting changes. No study seeds or random observations were generated for this response.

**Accepted fixes:** explicitly compare log E with ln(160); call the common grid an outer shell inside the wide observation domain, not extrapolation; add a fixed full-eight model fitted on all A+C+B64 observations, including it in the utility gate; invalidate the whole run on rank failure; treat quadratic/noise null controls as duplicate residual checks. Initial A now uses 24 distinct sites, not unnecessary duplicated observations. Equal total observations alone does not make B-only fixed baselines efficient; their role is a matched-estimation comparison. The pooled fixed model and pooled selector expose the allocation cost. The coordinator has incorporated these changes in the frozen protocol.

**Scope of a D-only nested test:** conditional on independently selected S, comparing restricted and full-eight fits both estimated on D can test the population support restriction under the correct full family. It does not check the predictive adequacy of the frozen B equation or its estimated coefficients. For full8 the comparison has zero degrees of freedom and cannot detect outside-family failure. This could be a separately labelled diagnostic, but it cannot replace the same-equation Q. The pooled fixed full-eight model already has an ordinary valid predictive Q; the pooled selected model still lacks that post-selection guarantee.

**Claims requiring qualification:** the two equal-size revision fits select by residual SSE, so proposal selection already uses observed residual structure rather than being a blind feature choice. The supplied grammar remains a major limitation. One-extension capacity excludes the both-cubic truth, but detection and prediction outcomes are not fixed by that fact. No theorem establishes that revision can never beat an always-large model; extra features carry estimation variance. Conversely, no favorable regime should be manufactured by expanding the grammar after an unfavorable calculation. A functional reject–revise–fresh-check loop is useful infrastructure, not novelty or a discovery-efficiency result.

## One deterministic calculation, not a study prediction

We evaluated the amended distinct-A design on one explicit Cartesian construction: A uses x={-1,-0.6,-0.2,0.2,0.6,1}, u={-1,-1/3,1/3,1}; B is twice A; C is the 4×4 product of {-2,-2/3,2/3,2}. The evaluation shell is the 56 stage1 grid points on {-2,-1.5,...,2}² with max(|x|,|u|)>1. Set sigma=0.05. A common quadratic mean cancels from these fixed-model bias/variance calculations, so the added mean a*x³ suffices.

For each fixed model/design, compute expected latent shell MSE as the shell average of squared noiseless OLS bias plus sigma²*vᵀ(XᵀX)^(-1)v. For the initial Q, compute the noiseless residual delta and lambda=deltaᵀV^(-1)delta; power is the noncentral chi-square16 tail at the central 0.025 rejection threshold. Calculations used standard-library linear algebra and the existing domain-study probability helpers, without calling any generator or sampler.

| Added amplitude | Initial lambda | Trigger power | Base6 on B | Correct7 on B | Full8 on B | Full8 on pooled64 |
|---|---:|---:|---:|---:|---:|---:|
| 0.05 | 108.9780 | approximately 0.9999999993 | 0.00680145 | 0.000680302 | 0.000803047 | 0.000361505 |
| 0.3 | 3923.2089 | approximately 1 | 0.22424159 | 0.000680302 | 0.000803047 | 0.000361505 |

The final four columns are expected shell MSE, not sampled measurements. If a triggered proposal always chooses the correct feature, independence of B makes the triggered estimator's risk (1-power)*risk_base+power*risk_correct, approximately 0.000680302 in both rows. This idealized proposal beats B-only full8 here, but loses to pooled64 full8. It is not the actual selector's risk and is not a universal lower bound when another biased estimator could have lower risk.

This is one boundary-rich, symmetric design, not an integral over the planned random designs. It refutes treating the unverified trigger-power estimate as settled, but does not establish average utility, derive the engineering thresholds, or predict an inevitable pass/fail. Strong-power rounding is not a claim of literally certain rejection. No additional designs were searched to select a favorable result.

**Recommendation:** retain the small supplied grammar, freeze the strengthened protocol before implementation, and report a negative utility result if pooled estimation wins. Passing infrastructure checks alone must not authorize another diagnostic iteration. The scientific deliverable is the bounded functional loop plus an honest efficiency comparison; any larger grammar, active acquisition or further revision requires a separately justified question.
