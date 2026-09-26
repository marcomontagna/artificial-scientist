# Claude Opus 5.5 — follow-up B result critique

Verbatim review of supplied figures, without tools.

This is a text-only critique, as you asked, so I haven't written a plan file.

## Results: what holds

- **Primary criterion passes as frozen.** Stress MSE falls 0.0207 → 0.00068, a 96.7% reduction, with 3/3 paired wins. The control and challenge caps also hold.
- **The stress gain comes from the new representation, not from active choice of experiments.** Ordinary_active cannot express a lag at all. It is also the only arm with harmful adoptions (1) and unresolved cycles (3), and one bad seed probably dominates its mean. Report per-seed MSE and medians, or the "96.7%" will read as larger than it is.

## Results: what's weaker than the framing suggests

1. **Active acquisition loses to random.**
   - Control: random 0.00093 vs active 0.00198.
   - Challenge: random 0.00060 vs active 0.00105.
   - Stress: roughly a tie (0.00070 vs 0.00068).

   With n=3 this is not proof. But it points one way in two of three world types, so call it an open negative for the "chooses experiments" claim, not neutral.
2. **The ridge reference is not usable as a yardstick.** Its MSE swings 60× between arms on the same world (control: active 0.065, random 0.001, coverage 0.095). That means it measures how well-conditioned each arm's data is, not how good the learner's model is. Drop it from any comparative claim, not just from the "beats system identification" claim.
3. **Check how "harmful" is labelled.** Coverage seed 3 adopts a false own-lag-13 term and scores external MSE 0.0228, about 30× the other stress runs, yet shows harmful=0 and useful=2. History_active seed 3 also retains the false lag 13. If the label does not catch an adoption that degrades prediction this much, the failure-admission test planned next rests on a mislabelled signal. Look at the audit rule before the next freeze.
4. **Compute is uneven.** History arms run 56–92 candidate fits versus 26–51 for ordinary. Log this as action/compute cost.

## Is the holdout the best next step?

Yes, it tests the actual claim: the same loop, facing laws the designer did not write. Add three cheap items to the protocol before new worlds exist:

- **A strong baseline, frozen now.** Fit a lag-order-selected sparse model (e.g. cross-validated lasso or ARX over the same k=1..16 own/cross lag library) per arm on the same training data. This takes about 15 minutes. It answers "does the loop add anything over off-the-shelf system identification" without a separate study, and it replaces the broken ridge reference.
- **An operational definition of admitting failure.**
  - For the beyond-grammar world, success means ending unresolved, or flagging the residual, *instead of* adopting a confident wrong structure.
  - Across runs, report whether unresolved or flagged runs have higher external MSE than resolved ones.
  - With 3 seeds, pre-declare this as descriptive only.
- **Sealing and arm choice.**
  - The author commits a hash of the world specification before any run.
  - The beyond-grammar world must not be trivially out of range (e.g. only a lag of 17); otherwise it tests a boundary, not the grammar.
  - Keep ordinary_active as a representation baseline and random as the acquisition control.

Don't run a separate acquisition ablation now. The random arm already is one, and the holdout will show whether active < random again. If it does, the acquisition policy, not the learner, becomes the next target.

For the ~80 minutes left: freeze the baseline and the failure definition (~20 min), have the author write and seal the worlds, run 24+ runs, audit. Leave the harm-label check to the other reviewer if time runs short, but note it as unchecked.
