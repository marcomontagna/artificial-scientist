**Verdict: REVISE.** The statistical core is sound. The plan cannot run as written because of three blocking issues: the runtime has never been estimated, one of the three schedules can never raise an alarm (by construction, not by chance), and the JSON config leaves out most of the protocol. Nothing below requires redesigning the study.

## Blocking issues (fix before the run)

**B1. Runtime has not been estimated and probably exceeds 500 s.** The existing `null_log_likelihood` (`artificial_scientist/causal_feasibility.py:110`) refits all 25 DAGs from scratch at every step. That is several thousand Python operations per step, roughly milliseconds each, and 3.6M steps would take about an hour. The incremental denominator is therefore required, not just allowed. Cache the 12 node/parent-set scores, update only the cells that change, and take the max over the 25 DAGs as sums of three cached scores.

Even then the total is roughly 50–150 µs per step, or about 180–540 s, which is close to the limit. The 800-step smoke run is too small to extrapolate from reliably. Before implementation, fix:
- a go/no-go rule, e.g. the timing smoke must project ≤350 s, otherwise revise before running;
- **seed-major loop order** (every cell for seed 200, then 201, …), so a timeout leaves balanced partial evidence rather than whole missing worlds;
- or, alternatively, preregistered sequential shards that each fit the 10-minute per-process cap and the 60-minute total cap in AGENTS.md.

**B2. The passive schedule has zero alarm probability by construction.** With passive-only data, log E_n ≤ 0 on every history, for both numerators:
- **Mixture:** Q_n = Σ w_k L_k ≤ max_k L_k. Each component's passive law (one correlated pair plus an independent third variable) is a DAG law, so this is ≤ the max DAG likelihood.
- **KT:** the Dirichlet mixture is ≤ the saturated multinomial maximum likelihood, which equals the likelihood of a complete DAG.

So the 3,000 passive episodes (a third of the compute) only check this fact. They must not be reported as empirical null evidence or as "power". Assert it as a unit test instead. Either drop passive from the sampled run, which also eases B1, or keep a small number of passive episodes explicitly labelled as an invariant check.

**B3. The JSON config does not encode the protocol.** It is missing:
- the definitions of the five null worlds (biased-root P1, fork noise 0.2, boundary fork, random DAG with CPT range [0.1, 0.9]) and the stress cell;
- the KT prior of 1/2, the threshold log(20), Wilson 95%, and the cap of 401;
- the random-stream offsets, smoke seed 190, and the 540 s external kill;
- the exact six gate cells;
- the null-debug rule, stated as ">20/200 in any single null cell and numerator".

State that a Wilson lower bound ≥0.8 at n=200 needs **≥172/200** detections (171/200 gives 0.7995). The runner should read everything from the config and hash it. Otherwise the independent verifier has nothing machine-checkable to hold the implementation to.

**Required tests before the run** (they belong with B1–B3):
- passive-only histories give log E_n ≤ 0 for both numerators;
- inverse-CDF sampling never returns an infeasible or zero-probability state, including u close to 1 when floating-point cumulative sums fall short of 1 (this matters for the deterministic boundary fork);
- the incremental denominator matches the exact helper within 1e-9, including intervened and deterministic histories;
- the mixture's predictive probabilities sum to 1 in every regime, and its running product equals Σ_k w_k Π p_k(x_i) computed directly.

## Assessment of the other points you asked about

- **Validity.** The Ville argument holds: the numerator predicts before each outcome and is normalized, the schedules are predictable or use independent randomness, and the denominator's max-likelihood term is bounded below by the true null likelihood. Continuing after alarm, reporting capped T over all 200 seeds, and treating the snapshots as P(T ≤ n) are all correct and consistent with the anytime guarantee.
- **Usefulness.** Much of the outcome can be predicted beforehand. With uniform-7 at e=0.05, the expected evidence is about 0.0745 × 400 ≈ 30 nats. Subtract about 3.4 nats for the 30-component prior, a few nats for the grid mismatch, and a few more for the max-over-DAGs overfit, and roughly 15–20 nats remain against a threshold of 3.0. The gate will very likely pass.
  - At e=0.35 the total expected evidence is about 0.28 nats, so power is essentially 0.
  - At e=0.20 it is about 4.6 nats before costs, so power is marginal.
  - KT's regret is roughly 40–50 nats, so KT power at 400 is probably near 0.

  **Preregister these predictions.** The study then becomes a test of the calculation instead of a foregone result. Its real value is the quantitative result: T distributions, the size of the KT gap, and the stress cell.
- **Hidden advantage.** The plan discloses it, but it is large. The mixture knows the exact generator form, fair U and a fair third variable; only the pair and noise are unknown, and the noise grid brackets 0.05 at 0.025 and 0.075. A passed gate therefore says almost nothing about a numerator a learner could use. The next adaptive study must not reuse this numerator without that caveat.
- **Null controls.** Independent fair roots is the most demanding null for the mixture, because the e=0.475 component almost matches it. Biased roots are close to trivially safe, because the mixture assumes fair marginals. Say this.
- **False-alarm checks.** The >0.10 debug threshold only catches gross bugs: P(≥21/200 | true rate 0.05) ≈ 5e-4, and it cannot detect a rate of 0.07.
- **Sample size.** 200 seeds is adequate for this screen: Wilson half-width ≈ ±0.05 near 0.85. The three pair cells share seeds and are relabelings of one another, so they are not three independent confirmations.

## Optional improvements

1. Add a non-oracle middle numerator, e.g. a mixture that also spans the U bias and the third variable's marginal. The mixture-vs-KT gap then separates "family knowledge" from "structure".
2. For null cells, report the empirical survival curve of max log E against the Ville bound P(max ≥ log(1/a)) ≤ a for several values of a. It costs nothing extra and is far more sensitive than a single rate at 0.05.
3. Report the maximum upper Wilson bound across null cells, not only the observed rates.
4. Clarify what "denominator200" means (I assume it means n = 200 seeds).
5. Note that round-robin gives action 0 58 of 400 samples and the other actions 57 each.
6. State the aim of the stress cell (misspecification of the U bias) in advance, as a direction of expected effect.
