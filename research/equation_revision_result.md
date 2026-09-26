# Reject, revise, check afresh — September 26, 2026

**The loop works; the practical utility screen fails.** A learner now rejects a base equation, chooses one supplied extra term, independently refits it, and checks the revised formula on fresh observations. It improves on never revising, but a fixed large model using all training data has lower mean prediction error. No superiority, novelty or observations-saved claim is supported. **Raw exact-support recovery is0/60 in every in-family pipeline cell:** all models retain a dense six-term base, so correct extension choice is not recovery of the sparse true equation. Confirmation subsets are separate outputs, not rewritten/refitted formulas.

## What ran

60 development seeds × eight worlds: **480 datasets, 2,400 final candidates, 42,240 observations; 103 tests pass**. A24 fits the six-term quadratic grammar; C16 triggers revision and helps choose x³ or u³. Independent B24 refits, and untouched D24 checks. All five pipelines share88observations. Never-revise and always-large/B24 isolate support choice; fixed large and ordinary four-model BIC use all64pre-D observations and expose the split's estimation cost. No action-selection policy, unknown-noise learning or invented operator is involved.

## Results

Mean latent MSE is measured on the common outer shell **inside** the wide observation domain, not beyond it. Lower is better.

| World | Revision triggered | Final equation rejected | Revision MSE | Fixed large/64 MSE | Pooled BIC MSE |
|---|---:|---:|---:|---:|---:|
| quadratic | 0/60 | 1/60 | 0.001588 | 0.001232 | 0.000872 |
| noise | 0/60 | 1/60 | 0.001588 | 0.001232 | 0.000872 |
| weak_x | 1/60 | 1/60 | 0.002371 | 0.001232 | 0.001353 |
| medium_x | 44/60 | 16/60 | 0.007295 | 0.001232 | 0.001064 |
| strong_x | 60/60 | 1/60 | 0.002353 | 0.001232 | 0.001064 |
| medium_u | 49/60 | 11/60 | 0.004524 | 0.001232 | 0.001016 |
| both | 58/60 | 53/60 | 0.017319 | 0.001232 | 0.001232 |
| exponential | 52/60 | 10/60 | 0.008021 | 0.003832 | 0.003632 |

For medium/strong x³, revision lowers mean shell error versus never-revise by59.5%/99.6%, but its error is5.92×/1.91× the efficient fixed-large baseline. Strong revision also improves over matched-B always-large (0.002353 versus0.003044); medium revision loses (0.007295 versus0.003044). The predefined utility screen fails both primary worlds. Paired revision-minus-pooled-full mean differences are0.006063 (descriptive95% normal interval0.002590–0.009536) and0.001121 (0.000655–0.001587), respectively, across60seeds per world; these are not simultaneous or cross-family guarantees. Controls are unchanged because no false revision occurred; quadratic/noise residual comparisons duplicate the same noise experiment.

When triggered in a single-cubic world, the learner selected the correct supplied term in every case:1/60 weak_x,44/60 medium_x,60/60 strong_x,49/60 medium_u. That is conditional selection success, not universal detection. Of16untriggered medium_x cases,15were finally rejected; among44triggered cases,1was rejected. For medium_u the corresponding counts are10/11 and1/49. The complementary marginal totals therefore do not describe exactly the same seeds. The fixed one-revision protocol cannot act on the late failures. The weak cubic was never term-confirmed. Of60medium_x datasets, the new term was confirmed42times by exact coefficient tests and17times by candidate likelihood evidence; strong_x60/60 by both. These methods have different evidence targets. Their claim containment was proved before sampling and verified, not discovered experimentally.

The limits matter: **58/59 insufficient weak-cubic equations,7/60 both-cubic and50/60 exponential final equations were not rejected**. The remaining weak-cubic nonrejection had selected the correct support; there were59nonrejections in total. The one-extension grammar cannot represent both cubics, and no supplied model represents the exponential. Nonrejection is not a true-law certificate. Pooled BIC's whole-form verdict remains unavailable, not zero rejection. Its mean prediction MSE is lower than revision in all eight worlds.

Each in-family world/pipeline had3/60datasets with any false exact-test claim and0/60with false likelihood-evidence claims. These are paired and often duplicate outcomes, not independent replicated calibration evidence; exponential truth-support metrics are undefined. Each coefficient method has a separate0.05family bound under known Gaussian/full-family assumptions; Q uses0.025perstage. Never combine these into a joint0.05claim. Neither0/60 nor3/60 estimates error precisely.

## Evidence and decision

Clean source `0e8c5c00c8190609b3aac088c2c31f50772f68e0`;4.137seconds internal/4.185external;19,070,392bytes. All hard integration checks pass, no post-result tuning or new seeds. [Protocol](../experiments/equation_revision_v0.md), [compact evidence](../results/equation_revision_v0), [reproduction commands](equation_revision_reproduction.md), [Claude plan critique and response](revision_plan_response.md). Full raw records remain local in `results/runs/equation_revision_v0_20260926`; A distinct reviewer independently recomputed all selections, fits, test statistics, summaries and gates, with maximum discrepancy6.92×10⁻¹¹ and no resampling. Claude Opus5.5 reviewed plan and results; [final critique and independently checked response](revision_result_response.md).

The analytic feasibility example was one fixed grid; its near-unit medium trigger power did not predict this random-design study's44/60. Keep that limitation visible. The earlier [domain-study RNG erratum](equation_domain_rng_erratum.md) remains in force; these new results do not repair or replicate that old study.

**Next decision:** stop this small-grammar line and keep the tested loop as a baseline. A bounded desk review should decide whether choosing costly observations can add value when every method uses the same efficient fitter; check closest active-discovery methods and strong design baselines before another protocol. This is a candidate question, not novelty clearance or a new experiment. Current execution is finished.
