# Tomorrow’s starting point

Research decision phase is complete; implementation is intentionally deferred. Read [decision](research/decision.md), [three candidates](research/candidate_gaps.md), [independent critique](research/critique.md), and [protocol](experiments/selected_experiment.md).

1. Review candidate 2 with the user: a known-method stress test of predictive versus parameter information under hidden shifts and wrong likelihood assumptions. No novelty claim.
2. Implement the separate finite-state runner and exact acquisition rules without changing the existing smoke experiment. Use standard-library CPU code; no paid services, model training or mandatory MLX.
3. Have a distinct agent review the implementation, especially same-state independent EPIG draws, tick-wise filtering, leakage, paired randomness and evaluation independence.
4. Run tests and the tiny development timing check; then freeze the specified development choices before held-out evaluation. Follow the resource caps and preregistered failure criteria. Do not optimize after seeing test outcomes.
5. Report all conditions, stationary costs, uncertainty and nonrecoveries. If the practical threshold fails, accept a negative/inconclusive result. A toy success does not establish novelty or superiority over R-IDeA/controlled-sensing methods.
6. Before any future methodological novelty claim, audit R-IDeA and latest controlled-sensing methods in depth. Representation learning remains deferred until identifying assumptions and need are demonstrated.

The one-time Notion report remains scheduled September 26, 2026 at 20:00 America/Chicago. Hermes/Claude activity remains unverified; do not duplicate their work if an acknowledgment appears. No new implementation or experiment was run during this research-only continuation.
