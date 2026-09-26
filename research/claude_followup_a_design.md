**Verdict:** the design is runnable after five corrections. Its main weakness is that stricter gating could look like better judgment. I made no tool calls, as you asked, so there is no plan file.

## Corrections before coding

1. **Journal timing for confirm_short.** Its two-step tapes start from observed suffix states, so they cannot all be journaled before the first suffix action. Journal each restarted prediction before its own action. Pre-freeze only the action sequence, the frozen models and the long tape.
2. **Define "visit counts."** Say whether they count actions or state/action bins. If they count states, an open-loop suffix cannot know future states without predicting them, which contradicts "never depend on predictions."
3. **Timeouts.** State that a partial confirmation batch cannot trigger adoption under split rules. It should resolve as unresolved or rejected, never as a pass.
4. **Long-tape scoring.** Compounding makes late positions dominate the eight-position MSE, and the 15% relative margin behaves differently at that scale. Log per-position error, and predeclare that the margin applies to the whole-tape mean.
5. **Evaluator horizon.** Say whether the "common evaluator tapes" are continuous or restarted. If they are continuous, confirm_long's gate matches the evaluator more closely. That is the hypothesis, but name it as alignment and not as generic validity.

## Causal confounding

- **Fewer adoptions.** Confirm_short and confirm_long use an AND gate across two batches, which is mechanically stricter than pooled. Fewer harmful snapshots may just mean fewer adoptions. Report harmful and useful snapshots per adoption, plus missed-useful counts, next to the raw counts.
- **Trigger timing.** The 16-unit trigger requirement lets original fire later in the budget than the split rules. This compounds the cost mismatch, which the design already labels as context.
- **Diverging histories.** After the first adoption, seeds are no longer paired histories, so later differences mix rule effects with path effects. Report outcomes up to the first divergence separately.
- **Sample size.** Nine runs per rule is anecdotal. Keep every claim at the world and seed level, as planned.
- **Mismatched criterion.** The encouraging criterion benchmarks against pooled, but the primary contrast is confirm_long versus confirm_short. Add a criterion for that contrast directly.

## Actionable failure criteria (predeclare)

- **Abort before the 36 runs** if deterministic replay of default-original differs from prior traces in any byte-relevant decision.
- **Inert split:** if confirmation disagrees with screening in fewer than 2 of all triggered cycles, the confirmation stage adds nothing and the line stops.
- **Horizon hypothesis fails** if confirm_long does not have fewer harmful accepted snapshots per adoption than confirm_short in at least 2/3 control/stress world-seeds. It also fails if it gets its control/stress gain with zero challenge adoptions or with fewer than 2/3 useful challenge adoptions.
- **Gating is just conservatism** if either split rule's advantage over pooled disappears once rates are expressed per adoption. Record that and do not pursue further gate tuning.

If any failure criterion holds, the next step is diagnosing representation or state distribution, not another gate variant.

## Scope and references

- The scope is bounded: one frozen design, 36 runs and no paid fallback. Whether 36 sequential runs fit in two hours is unchecked; estimate it from one prior run's wall time before freezing.
- I have not checked Sloman et al. 2022 or Ribeiro 2020 myself. Cite them as motivating only, as you wrote, and do not describe the failures as "sampling bias" unless the per-adoption analysis supports it.
- Per CLAUDE.md, another agent must review this critique.
