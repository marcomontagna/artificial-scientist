**Verdict: stage 3 can go ahead once two preconditions are met. It is a sound known-model check, but its main result can be predicted from theory, so treat it as an implementation check rather than a discovery.**

## Stage 2 critique
- The math is correct. The split-likelihood statistic, the null fit on five terms and the log 120 threshold match the protocol. `decision.json` and `summary.json` agree with the reported 0/0/0 false-term counts and the 300/300 and 198/200 true-term confirmations.
- The result was expected. Coefficients are large, sigma is known and the per-dataset bound of 0.05 is conservative. 0/100 is consistent with it but says little about calibration. The study never compared against the exact Gaussian z-test, so no power advantage is shown.
- Confirmation changes what gets reported, not what the fitter learns. The stage-1 recovery failure still stands.
- **Precondition 1:** the stage-2 result says the independent raw-data audit "is recorded in the review log before final publication". I cannot find it. `research/review_log.md` mentions confirmation only at lines 13 and 117, which appear to predate sampling. Record the audit before stage 3.

## Stage 3: statistics
- **Test math checks out.** r = ε_audit − A(XᵀX)⁻¹Xᵀε_train, so Cov = σ²(I + A(XᵀX)⁻¹Aᵀ). Q ~ χ²₁₆ marginally, and the even-df survival sum over k=0..7 is correct.
- **Precondition 2: the outcome is largely predictable.** The exp, cubic and sine laws are the same in every seed (`equation_discovery.py:134-135`); only designs and noise vary. Under misspecification, Q is noncentral χ²₁₆, and its noncentrality λ = δᵀV⁻¹δ is fixed once the designs are known. My rough hand estimates, not computed:
  - **Exp, local arm:** the leftover cubic Legendre term is about 0.044·P₃, so λ ≈ 2 and rejection is about 10–15%.
  - **Exp, wide arm:** rejection is near 100%, so the gain is about 0.85.
  - **Cubic, local arm:** the residual is 0.12·P₃ (RMS ≈ 0.045), so λ ≈ 13 and rejection is about 55–65%.
  - **Cubic, wide arm:** rejection is near 100%, so the gain is about 0.35–0.45, with SE ≈ 0.08.

  The cubic gain gate at 0.30 could therefore fail because the local test already works, not because widening fails. **Before sampling:** log the evaluator-only λ and predicted power for every audit, and report absolute wide-arm rejection next to the gain. Also write down now what a cubic failure with wide rejection near 100% would mean. The gate can stay as it is, but decide how to read it before seeing data.
- **The controls amount to one control, not three.** The plan itself says residuals will be identical, so assert that the Q values match within tolerance. The effective sample is 40 per arm, and both arms share noise.
  - If the test is exactly calibrated, the ≤4/40 gate still fails about 4.8% of the time per arm.
  - A true 10% false-reject rate would pass about 63% of the time.

  So the gate barely checks calibration. That evidence has to come from unit tests with known distributions. Also report the control p-value distribution descriptively (KS or quantiles).
- **The crude MSE rule will reject correct models on the wide arm**, because prediction variance grows away from the training region. That is the intended contrast. Label it that way so it isn't read as the correct model failing.
- **Each outside family is one fixed function.** Forty seeds means 40 designs for that function, not 40 functions.

## Blockers vs optional
**Blockers:**
1. Record the stage-2 independent audit.
2. Add the per-audit λ and predicted power.
3. Pre-state how a cubic local-ceiling result will be interpreted.
4. Assert that the three controls give identical Q.

**Optional future work:**
- Unknown σ (F/t tests), plus heteroscedastic and heavy-tailed noise.
- A comparison against the classical z-test.
- A local arm with 32 audit points, to separate the effect of domain from the effect of more data.
- Seed-varying outside-family laws, so there is a population of misspecified functions.
- Adaptive choice of where to audit, and grammar expansion.

## What three studies could support
- BIC selection over 42 supports with 24 observations over-selects on pure noise (9/20; the rough heuristic in the stage-1 notes predicted about 37%). The stage-1 recovery screen failed.
- With a correct polynomial family and known Gaussian noise, held-out split-likelihood confirmation limits false term claims and had high power at these effect sizes.
- Large term statistics do not certify the functional form: the outside-family candidates had them yet failed adequacy.
- If stage 3 passes: for one exponential and one cubic function, audits on a wider domain expose a fixed-quadratic misfit that local audits miss, and the uncertainty-aware rule avoids false rejects where the crude rule does not.

## What they could not support
- That the agent constructs or discovers equations. It only searches supplied monomials.
- Anything about unknown or non-Gaussian noise, other functions, higher dimensions, or adaptive or post-selection reuse.
- Superiority over standard regression tests.
- That wide audits are the best design, or that the agent chooses experiments.
- Coefficient accuracy or physical interpretation.
- Any novelty claim.

Scientifically, the three studies together are useful validation of a small hypothesize, confirm and falsify pipeline. They are not yet evidence that it can explain unfamiliar environments.
