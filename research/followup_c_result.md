# Follow-up C: history helps; the investigation loop still wastes evidence

All 24 declared runs completed using clean `4fc9e84`. Protocol/reference were frozen at `fae6bd8` before a separate agent authored the laws; learner/model source stayed byte-identical to `2b0eca1`. Another reviewer checked and sealed source/specification. Coordinator first read numerical laws after all 24 outcomes existed. This is a deliberately capability-aligned design check, not formal blinding or a random-world generalization claim.87 tests pass ; 8.36 CPU seconds for the24 runs.

| Mean external MSE | Ordinary active | History active | History random | History coverage | Sparse reference on history-active data |
|---|---:|---:|---:|---:|---:|
| New four-feature world | .079456 | .022752 | .010117 | .037017 | .000541 |
| New five-feature world | .038369 | .054588 | .014130 | .013624 | .000669 |

The first world's frozen representation screen passes: 71.4% mean reduction and 3/3 paired wins against ordinary. But all three history-active errors remain above the predeclared 0.01 reporting threshold, and random has a lower mean. Per-seed history-active errors are 0.033148 / 0.013809 / 0.021297; random: 0.000689 / 0.028558 / 0.001105. Coverage's 0.109694 third seed drives its high mean. This is not reliable scientific investigation.

The five-feature law exceeds runtime capacity 4. History-active errors are 0.014994 / 0.014142 / 0.134626; its mean is 42.3% worse than ordinary, despite improvements in the first two pairs. All three are poor and flagged, passing the narrow status criterion. However, two of three poor history-active runs in the four-feature world are unflagged. Ordinary also flags all poor five-feature runs. The status screen is not calibrated failure awareness; raw errors and all flag/poor cells are retained.

## What the saved traces explain

For all three active four-feature runs, the first primitive proposal includes own-input lag3 after experiment 5 and is checked at 6–9. It is rejected: seed 300001's improvement 0.014693 misses margin 0.015258; on 300002/3 it worsens prediction. The second cycle adds cross-input lag6 after checks 16–19. Both allowed cycles are now consumed, so no later proposal combines the two terms. Remaining trigger/cooldown/tool-budget conditions are met again in saved trajectories at 25 / 25 / 26, but the cycle cap prevents another attempt. This does not establish that a third attempt would succeed.

Random reaches both terms in two seeds by accepting the first term and then the second. On the active learner's same completed datasets, the sparse reference selects the complete four-term structure for seeds 300002/3 and predicts with MSE 0.000664 / 0.000324, versus 0.013809 / 0.021297. So useful information exists in the completed data. The offline reference sees later observations and has more fitting/validation work; this is not proof that the earlier online rejection was irrational or that acquisition is irrelevant.

The missing term was already proposed. Claude's suggestion to make proposals residual-driven does not alone address the observed bottleneck. The next design should let explanations be reconsidered after new evidence, benchmark whole-model construction against the audited sparse fitter, and separate construction quality from acquisition. Do not merely lower the acceptance margin, add the true term, or assume another cycle fixes it. The five-feature case also requires an explicit capacity decision, not just more opportunities.

## Audit and limits

Independent audit checked24 runs/48cycles, source seals, journal identity, all costs/errors/decisions,216 continuous prefix-only reference validation tapes and 48 final sparse ridge axis fits. Rollouts/fits matched exactly; largest loss-recomputation difference 4.44e-16.286 reference fits per run. Not every greedy candidate was independently refitted. The eight-term reference has more capacity and compute than the four-term investigator; two same-capacity selected models in worldA narrow but do not eliminate the online/offline distinction.

Claude reviewed supplied design/results without tools, separately from numerical auditing. We retain its criticism of model construction, warnings and weak primary baseline. Corrections: ordinary includes lag1; final warnings use short prospective errors, not merely in-sample fit; representation benefit does not make acquisition irrelevant. No default promotion, extra run or post-result law tuning.

[Design](followup_c_design.md) · [Sealed laws](followup_c_world_contract.md) · [All results](../results/followup_c/summary.json) · [Audit](../results/followup_c/independent_audit.json) · [Claude critique](claude_followup_c_result.md) · [Predeclared replay](../results/followup_c/replay.html). Browser playback remains unverified.
