# Equation confirmation v0 — result

The fixed diagnostic screen **passed**, allowing review of stage 3. This is a favorable known-model check, not a new discovery algorithm or proof that an equation is true.

One full run from clean `b944e2a` used 100 new seeds (700–799), five families and 20,000 observations: 24 training + 16 fresh audit observations per dataset. The unchanged stage-1 candidate equation was frozen before the audit. Six split-likelihood term tests used the prespecified threshold 120. No coefficients, predictions or thresholds were changed after seeing results.

| Family (100 datasets each) | Any false term in raw candidate | After term confirmation | All true terms confirmed |
|---|---:|---:|---:|
| Affine | 0 | 0 | 100 |
| Sparse quadratic | 15 | 0 | 98 |
| Pure noise | 32 | 0 | Not applicable |

Within each family, 0/100 has a descriptive Wilson 95% interval of approximately 0–3.70%; it does not establish zero future error. All 300 affine true terms and 198/200 quadratic true terms were confirmed. Selection recall was 100% in both families; conditional confirmation was 100% and 99%, respectively. Two quadratic datasets lost one true term each. The weaker audit-MSE filter alone retained false claims in 15 quadratic and 31 noise datasets.

The filtering changes **reported support**, not the fitted equation: quadratic exact claimed support rose from 85/100 to 98/100, while only 83/100 full original candidate supports were both entirely confirmed and locally adequate. Empty claims in noise are abstention, not evidence that the zero law is correct.

Both sine and exponential sparse candidates failed the local adequacy screen in all 100 datasets. Nevertheless, their average numbers of large term statistics were 0.57 and 2.58; this demonstrates why term evidence alone must not certify the functional form. Outside the supplied polynomial family, the term-test guarantee does not apply.

The family-wise error bound is at most 5% per dataset under a correct full six-term polynomial mean and independent Gaussian noise with known sigma=.05. The proof follows the known split-likelihood construction ([Universal Inference](https://arxiv.org/abs/1912.11436)); this is not a novel theorem, a coefficient-accuracy guarantee, or a comparison establishing superiority over ordinary Gaussian regression tests. Strong coefficients and known noise favor high power.

Runtime: 1.622872 seconds inside the study, 1.663430 seconds external process wall; artifacts 11,220,175 bytes. All 82 repository tests passed before sampling. Raw records: `results/runs/equation_confirmation_v0_20260926`; compact copies: `results/equation_confirmation_v0`. A distinct reviewer independently solved all 3,000 audit-null fits and recomputed direct Gaussian likelihood ratios, claims and summaries; maximum discrepancy was 1.82e-12. Four compact copies match the raw artifacts byte-for-byte. Details are in the review log.

Next: Claude reviewed the paired local-versus-wide domain challenge; implementation is underway following independent protocol approval. It tests whether a fixed full quadratic approximation can be falsified beyond its training range while accounting for coefficient uncertainty. Active acquisition and grammar expansion remain deferred; the first experiment's failed recovery gate remains a failure.
