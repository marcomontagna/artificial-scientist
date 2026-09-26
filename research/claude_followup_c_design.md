# Claude Opus 5.5 — follow-up C design critique

Verbatim review of supplied design, without tools.

# Critique of the Follow-up C design

The design is coherent and appropriately scoped. There are four blockers and a few small fixes, and none of them expand the study.

## Blockers (fix before sealing the worlds)

1. **"Term" is ambiguous.** The runtime cap is 4 terms, the reference allows 8, "separate coefficients per axis" is mentioned, and transfer_b has "five features." Define one unit, either per-axis terms or shared features, and apply it to the law, runtime and reference alike. Otherwise transfer_b might actually fit within the cap, or transfer_a might exceed it.

2. **transfer_a's delay must be lag ≥2 and not reducible to ordinary features.** Ordinary has lag 1. If the "nontrivial delayed component" is lag 1, or can be absorbed by lag 1, then ordinary can represent it. The ≤0.8 criterion would then test noise rather than history construction. The reviewer should confirm this analytically.

3. **The sparse reference validation must respect resets.** "One continuous rollout over the remaining 40%" is invalid if the training transitions span episodes or resets, and a 60% cut can split an episode. Split at episode boundaries (the nearest one at or after 60%). Roll out each validation segment from its own reset, or from its own prefix history, and sum the errors.

4. **Keep incomplete_check caused by compute separate from detector flags.** If a run hits 120 CPU-seconds and reports incomplete_check, it counts as "flagged" without any failure awareness. Tabulate budget-caused incomplete_check separately, and exclude it from the status-alignment numerator. Report it as incomplete.

## Minimal fixes

5. **Pre-seal oracle check for transfer_b, done on the law rather than a learner.** The reviewer computes the best 4-unit least-squares approximation of the true noiseless law on training-distribution inputs. If its rollout MSE is well below 0.01, the failure test is predictably uninformative, so revise before sealing. This checks whether the specification is valid, not learner performance, and it does not violate "no tuning."

6. **Report a noise floor for each world.** Report the external MSE of the true law under the fixed noise convention. The 0.01 threshold is only interpretable relative to that floor and to B's scales (~0.015 ordinary, ~0.0006 history).

7. **Pairing.** State that all 4 arms share the world and noise seed for each seed. Otherwise the "paired wins" are not truly paired.

8. **Deadline rule.** If the 24 runs are not all done by 22:15, report the completed set as incomplete. Do not interpret any subset selectively.

9. **Criteria on transfer_b.** Also report history-active versus ordinary there. A history gain on a non-expressible world is informative even without an alarm.

## Acceptable as declared

- A capability-aligned pair, with the world author seeing the grammar. You label this honestly as reduced co-design, not blindness.
- 3 seeds with 2/3 wins, reported as descriptive only.
- The own-incumbent harm counter kept separate from absolute adequacy. The absolute error/status table is the right addition.
- A greedy ARX reference with 8-unit capacity and explicit compute. Keep the older 9- and 39-feature references alongside it.

## Unchecked

I have not verified that the detector frozen at 2b0eca1 can see any absolute-scale signal. If it only uses internal residuals, a transfer_b miss is expected by construction. Say this in the report rather than treating it as a surprise.
