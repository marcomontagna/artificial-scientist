# Next steps

**The interactive learner and its visualization are complete.** [Result](research/interactive_lab_result.md) · [recorded replay](visualization/interactive_lab.html). It chooses experiments and improves predictions in supplied-rule worlds, but active acquisition loses on the random-lamp control. No novelty claim; no reward-trained RL policy yet.

1. Inspect the replay: compare the rule worlds, pure noise and majority stress. Distinguish posterior rule selection from the supplied lookup-table fallback. Preserve this version and its negative results; do not tune on seeds400–439.
2. Review one small stateful-world extension with Claude: actions should affect future states, with an explicit interface, unknown transition rules/action constraints, and independent prediction queries. Keep random, systematic and greedy predictive-information baselines. Specify when multi-step planning or intrinsic-reward RL is actually needed before implementing it.
3. Preregister new development seeds and reserved rule families, equal interaction budgets, compute costs, noise/wrong-model controls and a falsifier. Avoid full chess, a bespoke neural architecture or frontier-model training until the small comparison motivates them.

Understanding remains the objective; external win/lose reward is optional. Existing access only, no extra spending, independent review of every substantive artifact. Sequence seeds1000–1049 remain unused. See [seed registry](research/seed_registry.md).
