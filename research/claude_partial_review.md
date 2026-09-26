**Diagnosis is plausible, but I'd change the fix: the evidence points at a simpler cause than aliasing.**

This was read-only: I read `AGENTS.md`, `artificial_scientist/lab_guided.py` and a few trace fields, and ran nothing. There are no line numbers from the trace because the file is one long line.

**What the trace confirms**
- In the guided call where the incumbent (base) model is `u`, the features ranked `(u*p), u, (v*u), (u*u), (u*abs(u)), abs(u), 1, lag_u, v…`. The seven slots went to `u+(u*p)`, `u+(v*u)`, `(v*u)`, `u+(u*u)`, `(u*u)`, `u+(u*abs(u))` and `u+abs(u)`. The escape slot went to `1`. `v` ranks 9th, so `u+v` is never fitted.
- `lab_guided.py:70-73`: when the base has one term, each feature produces two edits (add it, or replace the base term). So only about 3.5 features ever get a slot.

**The counterargument: `u` is the 2nd most associated feature with its own residuals**
That can only happen if the frozen predictions used stale or miscalibrated coefficients for `u` (0.197 at step 11). The residual evidence is the last 24 records, and it still contains coefficient error for the base term. Every feature correlated with `u` inherits that score (~0.92). This is residual contamination, not wasted slots from aliases.

**Why your alias grouping is shaky as specified**
1. **Centering is wrong here.** Models have no intercept unless `one` is a term, so `x` and `x+c` look identical after centering but fit differently. Also, `one` centers to a zero vector, so it's undefined.
2. **Grouping on the "association-driving coordinate" is too narrow.** Two features can match on y and differ on x, and the fit in `lab_guided.py:109` uses all `rows`, not the 24 evidence records. Any equivalence test should use the fit rows, both axes, uncentered.
3. **Only two pairs are true aliases.** If pushes are unit magnitude on the axes (step 11 has `u ∈ {-1, ~0}`), then `u*abs(u)` equals `u` and `u*u` equals `abs(u)`. The top offenders, `(u*p)` and `(v*u)`, are not aliases. Grouping only helps when combined with round-robin. I hand-traced it: `v` enters at about slot 6, but only if `lag_u` and `1` behave as assumed. That is unchecked.
4. **`u+(u*abs(u))` is rank-deficient on this data,** so that fit is wasted regardless.

**Recommended single fix: opt-in partial association, as a new `guided-partial` mode**
In `_association`, remove the base terms' contribution from both the feature and the residual before correlating, using least squares on the evidence rows (the Frisch–Waugh method). Everything else stays fixed: the 7+1 slots, 8-fit cap, grammar, escape and planner.

This directly removes the "`u` explains its own residual" artifact. It makes `u*abs(u)` score zero without a separate alias rule, and it's a standard, attributable method. Log the projection cost in the feature-evaluation count. Don't claim it separates mechanisms. It only removes what the incumbent's own features can explain linearly.

If you prefer to keep your approach, the safer minimal version is to skip edits whose fit-row design matrix is rank-deficient or spans the same space as an already shortlisted program or the base, and take one edit per feature per round. Don't use centered, per-axis grouping.

**Verification order**
1. Replay step 11 from the saved evidence only (no later outcomes). Record `u`'s own raw and partial scores and the rank of `v`. Also run each of 15 randomly shuffled residual orders and record `v`'s rank. This is a noise check, not proof.
2. Confirm that `u+v` gets fitted and appears among the two selected models by training score. Being fitted alone isn't enough.
3. Then run six active-only runs: old guided vs the new mode on the 3 existing worlds, seed 260926. Report that those worlds were already inspected, so this is not independent confirmation. Keep control/guided outputs unchanged, and add a test that the default mode is byte-identical.

**Kill criterion**
If `u` doesn't rank high under partial association and `v` still misses, the stale-coefficient explanation is wrong. In that case slot allocation, not the scores, is the problem, and the round-robin plus span-dedupe fix above becomes the justified one.

**Unchecked**
- The fit rows and whether both axes are pooled in them.
- Whether `lag_u` is non-constant in the evidence.
- The exact per-record step labels for the base-`u` call.
