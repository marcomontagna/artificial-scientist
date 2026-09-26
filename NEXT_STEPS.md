# Next steps

**The stateful room learner and replay are complete.** [Result](research/stateful_room_result.md) · [replay](visualization/stateful_room.html). Two-step planning helps in the three designed rule worlds, but noise and hidden memory expose limits. Preserve this result; do not tune on seeds500–531.

1. Review a small history-aware comparison with Claude before implementation. Ask whether conditioning on a previous action improves prediction when the same visible state hides different internal states. Compare the frozen visible-state table with a simple supplied-history baseline; hold interaction budgets and evaluation queries fixed. This is not automatic representation discovery.
2. Preregister new development seeds/world variants, memoryless and noise controls, and a practical accuracy/complexity threshold. Reuse the current harness; target one local run under two minutes and100MB. Proceed only if history dependence is distinguishable and the controls can falsify the benefit. These limits are proposed, not a completed protocol.
3. Use that result to decide whether learned memory/state discovery is justified. Keep multiple universes and held-out law families in the longer-term plan; do not jump to chess or a bespoke neural architecture yet.

Strongest objection: a hand-supplied memory feature could trivially encode our designed hidden mechanism. Explicitly label it a reference baseline; improvement alone cannot establish novelty or generalization. Understanding remains the objective, not an external win reward. Existing access only, no extra spending, independent artifact review. Sequence seeds1000–1049 remain unused.
