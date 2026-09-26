## Verdict: revise before implementation (small wording and metric changes, no new architecture)

### Stage 1 interpretation
- **The FAIL is correct and so is the stop.** Pure-noise worlds got nonzero selections in 9/20 cases against a preset limit of 8/20. Affine support was 20/20, sparse-quadratic support 15/20, and sparse-quadratic false inclusion 5/20 passed. Stopping, deferring active acquisition and not retuning BIC are the right calls.
- **The failure could have been predicted analytically.** With σ known, adding a pure-noise term lowers SSE/σ² by roughly a χ²₁ amount. BIC keeps it when that exceeds log 24 = 3.18, which happens about 7.5% of the time. Across six roughly independent terms, the chance of at least one is about 1−0.925⁶ ≈ 37%. So 45% is consistent with the fitter working as designed, not a bug. A 40% limit was close to a coin flip, so a pass would not have shown calibration either. I'd add one sentence to the result note saying this. It does not reverse the FAIL.
- **The recovery successes happened at very high signal-to-noise.** Coefficients are at least 0.5 in size and σ = 0.05. On affine worlds sparse and linear are identical, and on exponential worlds sparse also matched linear. The only real problem was the penalty calibration on noise.
- **The adequacy reading is right.** Dense fits accepted 19/20 exponential worlds with local MSE 0.0037 but extrapolation MSE 0.99, so local adequacy does not establish a global law. The sparse fits' 20/20 rejection of exponential worlds partly reflects the 3-term cap.
- **Minor:** the five families share the same noise and input streams for each seed (`shared_streams`), so results across families are correlated. The per-family intervals are still fine.

### Stage 2 mathematics: correct
- **The statistic is right.** q is the Gaussian density from the frozen training fit. The denominator is the maximum-likelihood fit under H_j, using five terms on the audit data. That gives log e_j = (SSE_null_j − SSE_cand)/(2σ²).
- **Validity holds.** The selected support S and the coefficients depend only on training data, which is independent of the audit noise. Under H_j the denominator is at least the true density, so E[e_j] ≤ 1.
- **The union bound is right, and conservative.** Markov gives P(e_j ≥ 120) ≤ 1/120, and six tests give 0.05 per dataset. Only selected terms can be reported and |S| ≤ 3, so the real bound is 0.025.
- **The boundary is exact.** A term that wasn't selected has its null containing the candidate, so SSE_null_j ≤ SSE_cand and log e_j ≤ 0. The 1e-8 check is appropriate.
- **The full-family null is the right choice.** A null restricted to S would be false whenever S missed a true term, which would inflate false confirmations.

### Blocking issues
1. **Say upfront what the in-class results will be.** The noise false-term screen is almost guaranteed to pass: about 45% of datasets have a spurious term, and each confirms with probability at most 1/120 (in practice about 0). Power is also huge. On 16 uniform audit points, even an x² term with |β| = 0.5 leaves roughly 11·(4/45)·0.25/σ² ≈ 100 in signal strength. That gives log e of about 45, against a threshold of 4.8. So an in-class pass should be labelled an implementation and calibration check, not evidence that explanations are reliable. Also note that the empirical 5/100 limit equals the analytic bound, which only works because Markov is loose.
2. **Split the recall endpoint into two parts.** The "all true terms confirmed ≥ 80/100" figure mixes stage-1 selection misses with evidence failures, since a true term that wasn't selected can never be confirmed. Report selection recall and confirmation rate among selected true terms separately, and base the gate on the second. Otherwise a failure can't be interpreted.
3. **Separate a validity failure from a power failure.** "Whether pass or fail, stage 3 may…" is too loose. Any of these means a bug or a broken assumption, and stage 3 must not go ahead: a numerical violation, e > 1 on a term that wasn't selected, a failed null fit, or false terms above 5/100 in class. Only shortfalls in selection or power should allow moving on.
4. **Change the outside-family wording.** On sine and exponential worlds, every H_j is technically false and a large e_j only means "improves audit fit relative to the best five-term polynomial on [−1,1]²". Calling a formula "endorsed" there is exactly the kind of unsupported formula assertion this stage is meant to catch. Rename it to "locally adequate polynomial approximation" or leave it out.

### Does it achieve the goal?
Partly. It turns heuristic term selection into a calibrated per-term claim about false inclusions, which directly targets the stage-1 failure. It does **not** detect missing terms (only the local adequacy check does that), wrong functional form, coefficient accuracy, or anything outside the assumed domain. The guarantee rests on σ being known, the truth being in the family, and the uniform audit design. Since the simulation meets all three by construction, the study mostly verifies the implementation.

### Optional improvements (not blocking)
- **Justify universal inference in one sentence, and consider logging the exact test next to it.** With σ known and a linear-Gaussian model, a z-test on the audit data alone (full six-term model, Bonferroni over |S|) is exact and needs about 2.5× less signal. The reasons to prefer universal inference are that any frozen numerator works and e-values combine across later audits. Here power is ample either way.
- **A threshold of |S|/α (at most 60) is valid,** because S depends only on training. Keeping 120 is fine since it was declared in advance.
- **The most informative cheap stress test** is a noise-only run where true σ is 0.075 but the method assumes 0.05. Known σ is the assumption everything rests on.
- **Log the smallest singular value of each audit null design.** Rank loss is unlikely with 16 uniform points, but the existing solver fails on it.

### The conditional stage 3 (domain challenge)
This is the right next question, since stage 1 showed that local adequacy is not enough. It needs its own protocol written in advance. It should use fresh noisy samples from the wider domain, not the noiseless extrapolation grid the evaluator already sees. It should frame the test as whether a frozen candidate is falsified on new ground, not as term confirmation. And it should keep the limit of no formula repair.

I made no writes and ran nothing. Please record this review in `research/review_log.md`, marked as a Claude review.
