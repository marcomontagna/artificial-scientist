# Critique of the reject–revise–fresh-check result (equation_revision_v0)

**Verdict:** The arithmetic and the "utility fails" verdict are correct. I checked the ratios against the compact means (59.5%, 99.6%, 5.92×, 1.91×). But the write-up frames the result as a finding about revision, when it mostly re-measures a cost the protocol built in.

## 1. The decisive loss was predicted before sampling
The revise_once pipeline's final fit uses only B24, the 24 wide-domain training observations; A and C are discarded so that the fresh-check statistic Q stays exact. The pooled comparators fit on 64 observations. The plan response's deterministic table (`research/revision_plan_response.md:17-22`) already showed that even an ideal trigger and selector (0.000680) loses to pooled full8 (0.000362). The sampled data confirm this without any revision at all. In the quadratic and noise controls, revise_once exactly equals never_revise (0 triggers), yet pooled BIC is 0.00087 versus 0.00159. That gap is purely 24 versus 64 fitting observations. State the conclusion as: *under this design, exact post-selection validity costs about 2–6× in shell MSE compared with ordinary pooled fitting.* That is a price of sample splitting, which is well known. It does not show that revision lacks value.

## 2. The trigger stage is the real failure point, and the result understates it
- **Undetected cubics are caught only at the end.** medium_x triggered 44/60 and had 16/60 final rejections; medium_u triggered 49/60 and had 11/60. The counts are exact complements. That suggests nearly every untriggered in-family cubic is caught at D, and the protocol can then only label it "unresolved". Please have the raw audit confirm these are the same seeds.
- **The trigger design is the weak link.** The C test extrapolates a fit from the narrow A domain to the wide C domain. Random A designs then inflate predictive variance V and lose power, while the wide B→D check does not.
- **This failure drives medium_x's loss even to matched always_large** (0.00729 vs 0.00304).
- **Update the feasibility-note admission.** Say that the fixed-grid λ≈109 power estimate was materially wrong for random designs, not just "did not predict" the result.

## 3. Overlooked: no pipeline ever recovers the true equation
Exact support is 0/60 in all 35 in-family cells. The raw any-false-term count is 60/60 in the quadratic control. Every pipeline fits the dense six-term base, while each true law has at most three quadratic terms. The loop never outputs the true law, only a superset that predicts adequately. For an artificial-scientist claim this belongs in the headline. "Selected the correct supplied term" describes only which extension was added, not whether the equation was identified.

## 4. Smaller points
- **The confirmation evidence comes from D, not from the loop.** The exact and likelihood tests are computed on D and are identical across pipelines. The "42/17 confirmations" therefore show that D can detect x³; the loop only decides which terms are in the support being evaluated.
- **Quadratic false exact claims were 3/60 (Wilson 1.7–13.7%).** That is consistent with the bound but uninformative. The write-up already says so; keep it.
- **Sanity checks pass.** always_large and always_large_pooled are identical across all in-family worlds (0.003044 and 0.001232), as expected for unbiased full8 fits under shared designs.

## 5. The next decision
"Choose a task where uncertainty, experiment choice or model revision has practical value" is too open-ended. It invites a fourth round of validity scaffolding. The commit history shows a pattern: each study adds rigor around textbook linear regression and then loses to ordinary BIC or pooled fitting. That outcome is predictable whenever these conditions all hold:
- the hypothesis space is a small, enumerable linear family;
- noise is known;
- designs are fixed;
- the metric is in-domain prediction.

In that setting, standard model selection is close to optimal by construction.

My recommendation is to **stop this line and run no new study now.**

1. **Publish the result as a price-of-validity finding.** Apply the reframing from section 1, surface the 0/60 exact-support result, and name the trigger-power failure.
2. **Do a desk decision, not an experiment.** Write down which property of a future task would make ordinary pooled selection *unavailable* rather than merely beatable. Candidates:
   - the hypothesis space cannot be enumerated in advance (the exponential and both-cubic cases, where 50/60 and 7/60 final equations were wrongly accepted);
   - observations are costly and their location can be chosen;
   - the goal is structural identification rather than prediction.
3. **Authorize another experiment only if** step 2 yields a comparison where ordinary fitting is not trivially the right answer, and a pre-sampling analytic check like the plan response's shows that a win is possible. Don't redefine the metric or enlarge the grammar to rescue this study.

**Keep the loop's code as a tested component, not as evidence of progress.**
