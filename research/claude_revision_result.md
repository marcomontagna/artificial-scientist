**Assessment of the bounded revision-loop results (no tools used)**

**Warranted claims**
- **The loop runs end to end on a world its operators can express.** It triggers, proposes generic alternatives, checks them with frozen coefficients, and adopts the cross-velocity structure on all 3 challenge seeds. Error falls about 100× relative to no-revision (0.087 → ~0.0007–0.001).
- **Most of that gain comes from the hypothesis space, not from choosing experiments.** Random and coverage also recover the correct structure 3/3.
- **Active selection has a modest, unestablished edge in one world.** It is about 30% better than random or coverage and wins 2/3 paired seeds. That is suggestive at best. The screen value `useful_experiment_selection: true` overstates it.

**Not warranted**
- **Credit beyond the reference.** The ridge reference errs 0.057 on control, so it is broken or overparameterized. The 65.5% margin should not be headlined, and the credit screen means little.
- **Control non-regression as reassurance.** Active is 9% worse than no-revision, and the check and external evaluation disagreed on adoption. Random beats no-revision on control (0.00104 vs 0.00177). That suggests data distribution matters more than revision there.
- **General discovery.** The challenge law lies inside the operator library, and its authors knew the operator intentions. It tests search within a known family, not open representation change.

**Most important remaining failure: adoption honesty under misspecification**
- **Stress world:** the loop is unresolved 3/3, wrongly accepts 2/3, and ends 15.4% worse than keeping the incumbent.
- **Null world:** 1/3 unnecessary adoptions, which passed tolerance but made prediction worse.
- **Likely cause:** the frozen check uses 2-step experiments, while the hidden delay is 11 ticks and evaluation is 16 ticks. The acceptance test structurally cannot see the failure it must guard against. So the loop acts as if it has improved when it has not. A scientist should instead conclude "my representation is inadequate; keep the incumbent."

**One recommendation (no new sampling)**
Rewrite the adoption rule as a pre-registered change, before any further runs:
1. **Match the check horizon to the declared evaluation horizon.** Replay each candidate open-loop over already-collected trajectories at 16 ticks, not 2.
2. **Make "unresolved, keep incumbent" the default outcome.** Use it whenever the short check and long replay disagree, or the candidate fails to beat the incumbent on long replay.
3. **Log these as model-inadequacy declarations, not failed searches.**

**Constraints on how to do this**
- Do not add a lag or history operator now. Adding it after seeing the stress outcome would encode the answer.
- Freeze the new rule before evaluation. Then score it once on the existing 45 run logs to check whether the wrong adoptions (stress 2/3, null 1/3) become abstentions without losing the challenge adoptions.
- Label that rescoring as post-hoc diagnosis. Confirmatory evidence has to wait for fresh frozen worlds.
- Another agent should review the rule text before it is frozen.

**Unchecked:** I have not seen the true coefficients. The fitted cross terms (−0.165, +0.206) and the unequal axis gains (0.712 vs 0.640) may be accurate or may be compensating for something. Compare them to the ground truth before claiming the structure is "correct" rather than just "predictive."
