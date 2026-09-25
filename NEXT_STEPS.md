# Next steps

**The research pass is complete.** V1/v2 are frozen. Their reproducible negative result is useful, but further selector tuning is not the current research direction.

**Provisional question:** can a learner choose experiments that reveal its causal assumptions are wrong, while keeping false alarms controlled? This is an evaluation candidate, not a novelty claim. [Three candidates and the reviewed decision](research/research_reset.md).

1. Specify and independently review the tiny three-variable causal-world feasibility check. Establish which hidden-confounder worlds are observationally indistinguishable yet separable by interventions, and verify the sequential-test assumptions. Do not interpret approximate information rates as power guarantees.
2. Only if that check is useful, preregister a budget-matched comparison of random/round-robin, graph-information, predictive-information and falsification-oriented actions, with prediction loss, false alarms, horizon power and censored detection times.
3. Implement the known inference/test baselines after protocol review. Active causal learning is the replication control; cross-world transfer is deferred. If no meaningful distinction survives prior-art comparison, label the work replication rather than inventing novelty.

No new learner was built in this pass. [Reproduction results](research/selector_review_response.md) and [seed registry](research/seed_registry.md) are saved; reserved sequence-world seeds 1000–1049 remain unused. Claude proposed the candidates, Codex challenged them, and a distinct Codex reviewer checks the final artifacts. No extra spending.
