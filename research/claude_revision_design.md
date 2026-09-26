# Review: assumption-revision protocol

The design is close to runnable. There are two blockers and a few smaller fixes, and none of them needs a larger study.

## Blockers

1. **Possible answer encoding through the grammar.** Family 3 includes specific own×other products, and lag_u is a primitive. If the challenge-world author saw this menu, "revision succeeds" may only show that the world was written to fit it.
   - Before execution, record whether the author saw the grammar.
   - After the runs, have the evaluator record whether the true challenge dynamics can be expressed within four terms of the grammar.
   - Report "inexpressible" separately from "loop failed."

2. **The active-vs-coverage screen cannot measure much.** Outside checks there is only the incumbent, so active behaves exactly like coverage. The policies differ only during at most two checks, which is 16 of 80 units. With three seeds, "lower error than both random and coverage" is close to a coin flip.
   - Also judge selection with a direct, same-run measure: at each check, the gap in check MSE between the best alternative and the incumbent, and whether the adoption decision matched the one reached on evaluator data.
   - This tests what the active rule claims to do, which is to separate hypotheses.

## Leakage and hidden assumptions

- **Home variance.** It is computed as the initial squared position, which assumes home is the origin and that the initial offset is pure noise. That is world knowledge, not an observation-derived estimate. A stress world with a shifted home would inflate the threshold and stop the trigger from firing. Either derive noise from repeated observe→observe outcomes, or declare the assumption and log the threshold value in every run.
- **Paired prefixes.** Every policy runs coverage with a shared seed before the first trigger, so their histories should be byte-identical up to that point. Add this as a test. It is also your cleanest pairing.
- **Evaluation sequences.** The three off-menu sequences were written for the original world. The world author must confirm, when freezing, that they actually exercise the challenge change. Otherwise a correct revision cannot show up as lower error.

## Control fairness

- **Vector regression.** Fitting it over all nine primitives per coordinate covers everything families 1–2 can express. For linear challenges it should match or beat revision. State that revision earns credit beyond generic fitting only where it beats or ties this regression, or ties it with fewer parameters. Right now the regression is only "also compared."
- **Original learner.** Its menu differs, so it is a reference rather than a matched control. Keep it out of the "useful revision" screen, or report the screen both with and without it.

## Success criteria gaps

- **No functional criterion for the loop.** Predeclare these:
  - the trigger fires on challenge seeds;
  - on control it fires rarely, and any firing leads to rejection;
  - the adopted edit lowers error on the evaluation sequences for that seed.
- **Aggregation is unspecified.** State per-seed paired counts (e.g. 3/3 or 2/3) alongside the means, and decide now which counts as the pass.
- **Control non-regression.** Revision policies must not be worse than no-revision on control beyond a stated tolerance.
- **Replay fallback.** If challenge/active/seed 270001 never triggers, the replay is empty. Predeclare a fallback: the first triggered active challenge run in seed order.

## Practical risk

The ban on learner smoke tests before freeze means an untested threshold (`12*home_variance`, `.0025`) could waste all 45 runs. The control world is already development material, so allow a pre-freeze smoke run on control only, with seeds outside 270001–3. Use it to check trigger frequency and the runtime/trace limits. Log that smoke run as development work.

## Minor

- The parameter penalty (1e-4 per parameter) is negligible against a trigger-scale MSE of about .0025. That is fine, but note that selection within a family is effectively by fit alone.
- Refitting after adoption on data that includes the check observations is fine. Report the check-time frozen errors separately from the final model's errors.

**Verdict:** Fix the grammar-provenance disclosure, the noise-floor assumption, the pass/fail aggregation rule, and the regression-baseline credit rule, then freeze. Leave the scope as it is.
