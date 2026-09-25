# Research reset — September 25, 2026

**Decision:** freeze passive selectors. Provisionally choose **E3: choosing experiments that expose a wrong causal model class**, for mathematical and small-world feasibility work only. No candidate is novelty-cleared, no new method is accepted, and no new learner was built. The bounded research pass is complete; the selected feasibility calculation is the next task.

Claude Opus 5.5 independently proposed [three candidates](claude_research_candidates.md) through official Claude Code. Its original draft is preserved, including its own correction of the earlier selector bound and claimed transcript-recovered scripts. Codex’s corrections below govern subsequent work; the original draft is not an approved protocol.

## Three candidates, challenged

| Candidate | Existing overlap and strongest objection | Decision |
| --- | --- | --- |
| E1: informative interventions versus random/passive sampling | Active Bayesian Causal Inference already optimizes experiments for causal queries. A tiny exact-Bayes example validates a harness, not novelty. | Replication control only; defer implementation until E3 feasibility. |
| E2: distinguish transfer through experiment choice from transfer through inference | CAASL learns intervention policies across simulated worlds; Step-DAD refines amortized design at test time. Prior transfer benefits and prior mismatch costs are expected. The proposed factorial is not evidence of an unknown research gap. | Defer. Count all earlier-world samples and compute; do not claim equal information for fresh and transferred agents. |
| E3: detect excluded hidden confounding by choosing interventions | Sequential testing, universal inference and active discrepancy learning already cover much of this idea. A tiny example could simply reproduce established theory. | Best fit to the project; feasibility only. A possible evaluation contribution is the prediction-versus-rejection tradeoff at equal action budgets and controlled false alarms. This gap is unverified. |

Primary checks: [ABCI, 2022](https://arxiv.org/abs/2206.02063), [CAASL, 2024](https://arxiv.org/abs/2405.16718), [Step-DAD, 2025](https://proceedings.mlr.press/v267/hedman25a.html), [active model discrepancy, 2025](https://arxiv.org/abs/2502.05372). Codex checked their primary abstracts; this supports overlap, not exhaustive novelty clearance.

An important omission in Claude’s search is [Model Discovery Agent, August 2026](https://arxiv.org/html/2608.09696v4). It already combines explicit probabilistic world models, Bayesian experiment design, predictive checks and LLM-proposed model expansion. Codex read its method, predictive-check and limitations sections. The broad “scientist discovers and revises world models” idea is therefore not our novelty claim. E3 would investigate a much smaller, LLM-free statistical diagnostic; a smaller implementation alone is not a contribution.

## Corrections required before an experiment

1. **No false headroom bounds.** An infinite-passive-data error floor below 0.02 does not prove interventions cannot improve finite-sample learning. Nor does one privileged predictor bound every adaptive policy. Use these as descriptive feasibility comparisons, not impossibility proofs.
2. **No power guarantee from a rate approximation.** The proposed `N D* ≥ log(1/α) + regret` is a planning approximation, neither a necessary nor sufficient finite-sample detection condition. A 1.33× information-rate difference does not establish a 25% reduction in detection time. Failure at one action mixture does not reject all adaptive designs.
3. **Use the intervention support.** Passive three-bit observations have eight outcomes (seven free probabilities); each hard single-variable intervention has four possible outcomes (three free probabilities). Seven equal eight-outcome models overcount the effective dimensions. Compute exact sequential predictive probabilities; do not substitute an asymptotic regret formula for validation.
4. **Prove validity, then test implementation.** Simulations cannot establish an anytime false-alarm guarantee. The null is a union of 25 graphs with continuously varying conditional probabilities, not 25 fully specified distributions. All mechanisms must be fixed within an episode; adaptively selected, perfectly executed interventions and complete observed outcomes are assumptions. A rejection diagnoses incompatibility with this null, not uniquely hidden confounding.
5. **Handle failures and budgets honestly.** Compare the same action and sample budgets, disclose acquisition compute, use a query-directed predictive-design baseline as well as graph-information gain, and report prediction loss alongside detection. Do not report median delay only among detected cases; retain right-censoring and horizon power. Proposed targets α=0.05, power≥0.8 by 400 samples, and 25% faster detection are design aspirations, not measured results. Specify world distribution, practical thresholds, uncertainty intervals and all model/policy settings before evaluating them.

The [Müller–Luo–Barber paper](https://arxiv.org/abs/2502.06765) concerns distribution-free lower bounds on model-class risk; its abstract does not justify a blanket impossibility claim for this structured interventional test. Do not claim that a finite graph list automatically bypasses every impossibility theorem.

## A valid statistical starting point, not a new algorithm

Let actions be chosen before outcomes using past observations. Let `q_t(y | a_t, history)` be a normalized prediction formed without seeing `y_t`, and let `L_n(m)` be the conditional likelihood under one fixed null causal model. Use

```
Q_n = product_t q_t(y_t | a_t, history_before_t)
E_n = Q_n / sup_{m in null} L_n(m)
reject when E_n >= 1/alpha
```

For each true null model `m0`, `E_n <= Q_n/L_n(m0)`. The latter is a nonnegative likelihood-ratio supermartingale (a martingale under matching support); Ville’s inequality controls the probability of ever crossing `1/alpha`. This requires the exact supremum, or a certified upper bound—not an optimizer’s lower estimate. Action-selection probabilities cancel only when the same predictable policy is used under every model. This is an application of established running-likelihood inference, not a novel test. [Universal Inference, §8, 2020](https://arxiv.org/html/1912.11436v3).

## Concrete next task

Write and independently review a small feasibility specification: three observed binary variables; stationary worlds with or without one hidden common cause; seven allowed actions (observe, or set one variable to 0/1). Enumerate each world’s interventional distributions and the best-fitting null DAG under explicitly chosen action mixtures. Check observational indistinguishability and interventional separation. Label evaluator-informed mixtures privileged. Check the sequential statistic algebra/support and exact likelihood calculation, including zero-likelihood and null-impossible-history conventions, before building policies. Save zero/near-zero separation cases rather than tuning them away.

This calculation can reject a particular proposed benchmark, or support a later preregistered policy comparison. It cannot prove a research gap or finite-budget power by itself. If the result adds no useful distinction over prior work, keep it as replication and stop the novelty claim. Changes of hidden laws, transfer, neural representations and model repair remain later questions.

## Provenance and limits

Claude completed one read/search pass in about 287 seconds, 24 CLI turns, using existing Pro access after the native usage screen confirmed credits were off. No API key, paid fallback or new service was enabled. Root independently reviewed its proposal and added the primary-source checks/corrections above. Its recovered-script appendix is attributed transcript text; byte identity to the old scratch files was not independently verified or rerun. The separately reviewed [recreation](selector_review_response.md) is the empirical evidence used here.

Search coverage is bounded. Claude disclosed abstract-only and inaccessible references; Codex did not verify every bibliographic claim in its original draft. Universal Inference’s inspected v3 is dated June 2020, resolving the draft’s 2020/2022 uncertainty. No E1–E3 experiment, new seed range, trained model or detection result exists yet. See [review log](review_log.md).
