# Review of the first integrated lab agent

I read the code only. I ran nothing and edited nothing. I also read `lab_world.py`, so I know the hidden laws; the learner never sees that file.

**Short answer:** I found no path by which the evaluator leaks into the learner. `lab_agent.py` imports only `lab_api` and `lab_models`, and it only receives `Observation`/`Action` records. Evaluation uses separate world seeds, never calls `accept()`, `propose()` or `fit()` on held-out outcomes, and saves each prediction tape before the evaluated actions run. The loop is wired end to end. But two things are weaker than the note implies: what drives experiment choice, and what triggers revision.

## Objections

1. **The grammar holds the exact development law, and a term that looks shaped to the challenge.** Development is `delta = 0.82·v + 0.42·u`, which is exactly the two-term `('v','u')` entry. The `v·|v|` family matches the challenge's speed-dependent drag. The grammar was written after `e6920e7` while the world source sat in the repo. Recovering the development law therefore validates the plumbing, not discovery. Say so in the report. The challenge world needs different gains per axis plus a cross-axis `0.10·uy` term, which a shared, separable, two-term model cannot express. Its failure is fixed in advance and should be reported as a representation limit, not as a scientific finding.

2. **Experiment choice is driven by strawman models** (`lab_agent.py:46-55`). The committee starts with zero-displacement and constant-velocity models. Every live model gets equal weight in the disagreement score, however badly it has predicted. While the zero model survives (only 6 are kept per round), disagreement on a push is roughly the displacement already predicted, so the planner picks large pushes because of a model it has evidence is wrong. Smallest fix: weight each model's vote by its prequential error, e.g. `exp(-common-window MSE / noise)`, or drop models worse than k× the best.

3. **Revision runs on a clock, not on surprise** (`lab_agent.py:101`). New structures are proposed every 4th step whatever the errors were. Nothing marks an anomaly or triggers a revision. Also, `propose` excludes only the ids of *live* models, so a structure just dropped for poor out-of-sample errors can be re-added next round with a fresh record, which can cause churn. Smallest fix: also propose when the best model's latest error exceeds a threshold relative to its recent mean, and keep a list of dropped model ids.

4. **The planning branch past warmup is untested.** `test_prediction_frozen_before_update…` runs 4 steps, which is all warmup. Nothing tests the score-based choice, `final_model`, the reset-driven noise estimate, or re-proposal churn. Add one short test that goes past step 4 and checks the chosen action is the argmax of the logged scores.

5. **The noise estimate is very weak.** At first it comes from one initial reading. It gets a new sample only on `reset`, which costs 8 and which the active planner will rarely pick. So the `-2*noise` threshold is effectively fixed by a single draw from a chi-square with 2 degrees of freedom. Log the reading count next to every score (already done) and don't read the threshold as calibrated.

6. **The noise world needs a simple baseline.** There, `delta = -1·p` (predict home) is in the grammar and is the true law. Regressing noisy differences also pulls `v`'s coefficient toward −0.5, giving a smoothing predictor. Persistence costs about 2σ²; predicting home costs σ². The linear reference has no `p` term, so "learned beats both references" is guaranteed by construction. Add a frozen predict-home reference, or note this in the report. It is a baseline, not a new study.

7. **Every prediction starts from a noisy position** (`frozen_rollout`, `plan`). Using the observed `p` as the state puts current sensor noise into every prediction, including evaluation, which starts from a noisy reset reading rather than the public (0,0) home. This hits all references equally, so rankings hold, but absolute errors carry a floor of about 2σ².

8. **Post-wait predictions are also biased.** After a wait, planning uses the average-velocity estimate from `velocity()`. The prequential errors that rank models, and `final_model`, therefore include this bias, and it varies by policy with how often waits are chosen.

## I accept your position on the noisy-velocity point

Predicting next position is algebraically the same regression, and a denoising predictor legitimately beating persistence is not a defect. The evaluator warning string states this correctly.

## Recommended smallest step before the demonstration

Fix #2 (weight votes by track record) and #3 (surprise trigger, dropped-model list), and add the test in #4. Then run development only. In the write-up, keep #1 and #6 visible as "representation and baseline limits."

**Not checked:** `lab_replay.py`, `test_lab_replay.py`, and the replay HTML export.
