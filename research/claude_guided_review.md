Your idea is worth building, with two conditions. Frame it as "residual-directed forward selection over supplied terms", which is a known method (matching pursuit / stepwise regression), and fix four problems in the spec first. This review was read-only: I changed no files and ran no tests.

**1. At this size, the guided search can't beat the control on fit.**
- `grammar()` produces 20 terms. `propose()` fits about 200 one- and two-term candidates with 2×2 solves (`lab_models.py:187`). That's cheap, and it always finds the best fit on the data seen so far.
- A guided proposer limited to 8 fits can at best match that fit. "Fewer fits" isn't a meaningful win here.
- What the guided search can change is which models sit in the committee, and so which experiments get chosen. Measure that directly:
  - At each proposal event, log the guided candidates' rank in a shadow enumeration run on the same rows. This is diagnostic only and never feeds back into the learner.
  - Measure a counterfactual: would the chosen action differ if the guided model were left out of `plan()`? Scoring that is cheap. Without it, "affects action choice" is an assertion.

**2. Sensor noise alone will make the residuals point at p and v.** This is the main technical problem.
- The target `after − p` shares p's noise, so it correlates with −σ² even with no real effect.
- `v` is the previous delta, and it shares that noise with opposite sign, which gives a covariance of about −σ² too.
- So a pure-noise world will reliably suggest "add p" (mean reversion) or "add v" (damping).
- Fix: compare each association against the null implied by `home_noise`, and log that comparison.
- Required test: in a noise-only or constant-velocity world, the guided mode must not add p or v terms more often than the enumeration control.
- `u` and `lag_u` are set by the agent's own actions, so they are the cleanest signals. They're still confounded by the planner's choices.

**3. Residuals from a changing incumbent get mixed.**
- Pre-action predictions were made with coefficients from before the latest refit, often by a different incumbent (`final_model` switches between models).
- Pooling those residuals mixes coefficient drift and model switches with genuinely missing structure.
- Recommendation: screen on in-sample residuals of the current refit incumbent over `training_rows`. Keep pre-action predictions for validation only.
- If you insist on pre-action residuals, reset the pool whenever the incumbent changes, and log that.
- Either way, `training_rows` needs to carry each row's transition index. Otherwise traceability and the no-leakage test can't be checked.

**4. "Strongest input plus related transforms" is a hand-written rule, and it misses interactions.**
- Screening raw inputs cannot find `mul(v,u)` when neither main effect shows up. Your own test will simply confirm the blind spot.
- Cheaper and cleaner: score all 20 grammar term features against the residuals (about 20 dot products, with the cost logged), then fit the top 7 or so.
- This removes the hand-coded "related transforms" table. It also makes the escape candidate less important.
- Specify how the escape candidate is chosen: seeded random from the grammar. It must never be the enumeration's best.

**Other issues in the code**
- `seen_structures` permanently excludes any structure that has been proposed once (`lab_agent.py:128`). Local edits to a 2-term incumbent have few neighbours, so guided mode will run out of candidates, and an evicted correct term can never come back. Decide whether to exclude per edit or with an expiry, and log "no candidates".
- An incumbent with 2 terms can only receive replacements, never additions. Some pairs also exceed complexity 12 (for example `mul(v,abs v)` + `mul(u,abs u)` is 13). Log edits that were rejected by the budget.
- Before `final_model` has any mature model, the incumbent is the zero model. Its residuals are then the raw deltas, so early guidance is just a correlation screen on the raw data.
- New models get weight 0.25 until they have 3 prediction errors (`lab_agent.py:50`). A proposal may not drive action choice for several steps, and your "not separated" log needs to cover that window.
- `predict_state` uses averaged velocities across multiple ticks, but training excludes those transitions. The eligibility rule for residuals must match `training_rows` exactly.
- Break ties by `program_id` so replays are reproducible.

**What the six runs can and can't show**
- With one seed, they're descriptive traces. They can't separate the two modes, and they give no generalization evidence.
- Decide in advance what you'll report:
  - the counterfactual action-change rate
  - how many guided proposals were later confirmed or refuted by pre-action predictions
  - the enumeration rank of each guided proposal
  - the rate of spurious p/v additions under noise
- An honest likely result is "guided ≈ control, sometimes worse". Report that plainly.

**Keep in the plan**
- The control stays unchanged.
- Nothing from the worlds, the evaluator or world IDs feeds proposals.
- An association only motivates a hypothesis.
- Outcomes that failed to separate a proposal stay visible.

**Unchecked:** I haven't read `lab_api.py`, the worlds, the evaluator or the tests, so how well eligibility and leakage are guarded there is unverified.
