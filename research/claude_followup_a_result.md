# Claude Opus 5.5 — follow-up A result critique

Review of supplied protocol and figures; no direct file/tool audit. Verbatim response follows.

**Verdict on the claim**

Your interpretation holds, but it should be stated more strongly. The new gates did not just fail to help; on stress they hurt.

- **Control and challenge are unchanged across all four rule sets.** There were zero harmful adoptions in any cell, so the gates had nothing to prevent. The challenge result (3/3 cross-velocity adoptions) replicates earlier work and is not evidence for the new rules.
- **Stress got worse.** Under the original rules there were 2 adoptions, 1 useful. Pooled and short gave 1 adoption, 0 useful, 2 missed. Long gave 0 adoptions. Mean MSE rose from 0.0201 to 0.0220 to 0.0223. Stricter gates cost a useful revision and bought no safety. Report it as "stricter gates reduced recall with no measurable precision benefit (n=3, harmful base rate 0)."
- **Check "missed" before writing it up.** Long has fewer adoptions than pooled but fewer misses (1 vs 2). Either the definition depends on which candidates reached checking, or there is a counting issue. Flag it for the raw audit; I have not checked it.
- **The real gap is stress MSE**, about 30× control. Stop gate tuning. Agreed.

**Recommended next experiment**

Run a frozen multi-timescale memory bank, with the residual diagnostic as its first stage rather than a separate study.

1. **Diagnostic (training data only, cheap).** Within each world's 80 training units, regress incumbent residuals on public history using held-out folds inside training. Record whether temporal residual predictability exists per world. This sets expectations; it is not a result.
2. **Arms.**
   - A: current grammar.
   - B: grammar plus an opt-in bank of geometric-timescale EMAs (or lags 1..K) of each public sensor and action. Fix K and the timescales from a principle, such as powers of 2 up to about half the continuous suffix length, not from stress behavior.
   - Keep max 4 terms, ridge, 2 cycles, 3 alternatives, and the current checks unchanged.
3. **Strong baseline C.** Flat ridge on the full bank with no formula search. If C matches B, the construction loop adds nothing beyond features.
4. **Negative control.** Include worlds whose missing structure is known to be non-temporal. B should not adopt bank terms there.

**Risks**

- **Answer leakage.** If K was chosen knowing the stress world's hidden lag, the bank encodes the answer. Document the choice before running and have the other agent confirm it.
- **Tape restarts break memory.** The short check uses locally restarted 2-step tapes, which reset or corrupt memory features. Freeze how warm-up and initialization work from public history only. Otherwise the short check will systematically reject memory candidates for reasons unrelated to the world.
- **Experiment choice can't see long memory.** Two-action checks cannot reveal long timescales. Only the continuous suffix can. Report which checks could in principle discriminate each timescale, and don't count long-suffix passes as "agent chose informative experiments."
- **Search inflation.** More primitives means more chances to pass checks by luck. Report candidate counts per cycle.
- **Scope.** Same laws with new noise remains development, not generalization.

**Frozen success criteria**

- B beats A on external stress MSE in at least 2 of 3 worlds.
- B shows no control or challenge degradation beyond the existing cap.
- Harmful adoptions do not increase.
- B beats C.
- Negative-control worlds show no bank adoptions.
