# Claude Opus 5.5 — follow-up B design critique

Verbatim review of supplied design, without tools.

**Verdict: nearly ready.** Freeze the protocol once the two blockers below are fixed. None of them requires a redesign. I did not check the code, the simulator or the result files, so every point below is about the design text only.

## Blockers

1. **Reset semantics may not match the simulator.** The design zeroes the input buffer at reset. If the stress world's hidden delayed state survives a reset, the lag model is wrong in a systematic way, and a failure would reflect a convention mismatch rather than a missing capability. Before freezing, the auditor should confirm the simulator's reset behaviour by reading the code (not running it) and record the result. If the two don't match, declare that the design's convention is being kept anyway and treat the resulting error as expected.
2. **The evaluation-tape buffer source is not specified.** For each external tape, say which history rebuilds lag memory at the start of prediction: the tape's own inputs since its reset, or training history. It must never include inputs from other tapes or from after the prediction start. The flat reference must build its features exactly the same way. Add one synthetic test that would catch leakage across tapes.

## Minimal corrections

- **A lag term only appears if a check fails.** A temporal term is proposed only after an ordinary check fails on the stress world. Log how often that happens per arm and seed. If it never happens, report the run as "construction never triggered", not as "no benefit".
- **Limit on attributing gains to active acquisition.** Only one temporal candidate reaches the committee, so active acquisition can separate the lag winner from the other alternatives, but never one lag from another. Say so. If history-active beats random, credit that to choosing between explanations, not to choosing the lag.
- **Weak penalty against 30 new candidates.** A 0.0001 cost per parameter barely penalises picking the best of 30 correlated lag features with 80 training units. Also log the rank and score of the chosen lag relative to its neighbours at k±1 and k±2. That shows whether the lag was clearly identified or picked from nearly tied scores. This is a logged diagnostic only; it must not change the shortlist.
- **Pin down the primary arithmetic.** Say that "20%" means the ratio of mean stress MSE across the 3 seeds, and that "paired" means the same world and sensor seed, compared per seed. Say that "control/challenge ≤ 1.25×ordinary + 0.0001" is checked per world on the mean. It is not an OR across the two worlds.
- **Scope.** The primary result rests on one world with three seeds. Label it as developmental evidence of integration, which the design already mostly does.
- **Missed revisions.** Define "missed" before running, since the long and short later histories can diverge. Keep the audited definition from Follow-up A, word for word, so the two studies can be compared.

## Not blockers

- The model class contains the known stress law. The design already discloses this and claims no novelty, so it is acceptable for testing a working integration.
- A lag horizon of 16 is justified independently of the result, and all 32 entries are searched uniformly. Keep the rule that the budget is not enlarged afterwards.
- The flat 39-feature ridge is a strong, fair same-data baseline. Treating it as a qualifier rather than the primary comparison is fine. But if it beats history-active, the report's headline must say so.

## Why this is worth running

This is the right next step for the connected loop. It adds a new kind of explanation, which is triggered by prediction failure and judged on frozen prospective checks, instead of tuning the gates again. Fix the two blockers, add the logging above, freeze, and run all 36 runs once.
