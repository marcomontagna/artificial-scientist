# Critique of the first tool-lab implementation plan

The plan follows `AGENTS.md` and `research/tool_lab.md` well: the boundary, frozen predictions, equal-cost controls, one challenge world, one noise world and the replay are all there. Five problems should be fixed before the demonstration runs. #1 and #4 will produce wrong results if left alone.

## Blockers

**1. The velocity estimate creates a fake law from pure noise.**
- The plan uses v_t = y_t − y_{t−1} and fits Δy_{t+1} = y_{t+1} − y_t. Both contain the same noisy reading y_t.
- For an object that isn't moving, with noise level σ, cov(Δy, v) = −σ² and var(v) = 2σ². The fitted coefficient comes out near −0.5.
- So the learner will report "damping ≈ 0.5" in the noise-control world, and it will partly distort real damping estimates elsewhere.
- **Smallest fix:** fit and score candidates as predictors of the next position, y_{t+1} = y_t + f(y_t − y_{t−1}, u, …). Put the known bias in the notebook. The noise control must then check that no velocity term beats persistence on fresh evaluation. If you refit using only non-overlapping differences, write that rule down before running.

**2. The timing of the input `u` is undefined, and fixing it by hand would leak the answer.**
- Depending on the hidden integrator, a push at tick t moves the object at t+1, or only at t+2 (force changes velocity, then position).
- If the primitives only use the current u_t, then the developer's choice of integrator decides which models can fit. That encodes part of the answer.
- **Fix:** add the previous input u_{t−1} as a primitive (the design already allows lags). Also state "wait means u = 0 on every tick." The phrase "u=0 after first tick" is ambiguous: it could mean the previous push is carried into the wait.

**3. Waits and resets break the one-tick training data.**
- `wait(k)` returns only the final position. The displacement across a wait is a k-tick total, not a one-tick transition.
- If the next v is computed from it, v becomes a k-tick average.
- The step from the last pre-reset reading to home is not a physical transition.
- **Fix:** mark any transition whose previous interval wasn't exactly one tick as ineligible for the one-tick fit. Waits are scored only through their recorded rollout prediction. After a reset, v stays "unknown" until two readings exist. Setting v = 0 from the public home state is acceptable only if the home state is documented as zero velocity. Add a test that rejects any fit row spanning a reset or a wait.

**4. The noise estimate the planner relies on is never defined.**
- The planner scores "disagreement beyond estimated noise," but the plan marks noise as unresolved and never defines the number used.
- **Fix:** declare that the noise floor is the best candidate's pre-action residual (model error plus noise, combined). Label it that way in the replay. Only claim noise and model error are separated if repeated readings of a known-static state make that possible.

**5. The success criterion and the evaluation setup are underspecified.**
- Write these down before the run:
  - The evaluator's intervention sequences are fixed ahead of time and identical for the learner and both controls.
  - Each sequence starts from reset/home.
  - Each includes multi-tick waits and push sequences, because one-step error mostly rewards persistence.
  - Evaluation uses a separate noise stream.
  - The metric is per-horizon error.
- Add a second fixed reference next to persistence: a linear fit on (v, u, u_{t−1}, 1). Otherwise you can't tell whether the program search adds anything over plain regression.
- With one seed per world, call the comparison descriptive. "Success" means the loop ran honestly with frozen predictions and reported evaluation errors, not "beats random."

## Should fix (small changes)

- **Ranking after late arrivals:** candidates proposed later have shorter prediction records. Rank on a shared window: the last N events that every live candidate predicted before seeing them.
- **Refitting is part of the model:** coefficients are refit every step, so the prediction score measures program plus refit rule together. Say so.
- **Define "every 4 observations":** actions, ticks or cost units? It changes timing when waits are involved.
- **Define `abs` in 2D:** per component or vector norm? Per-component abs makes |v|·v anisotropic, which contradicts "isotropic."
- **Declare what can't be expressed:** there is no sign(v) or division, so Coulomb/threshold friction is out of reach. List that alongside the isotropy limit.
- **One-step planning horizon:** disagreement often grows faster than linearly with k, so the planner may prefer `wait(4)`. That's fine if it shows up in the logged action scores, not as a hand-tuned weight.
- **Random-number generators:** the controls' action RNG must be separate from the world noise RNG. Noise should be indexed by tick so that different action sequences don't change the noise draws.
- **CPU cap:** does the 120 CPU-seconds cover only the learner, or evaluation and HTML generation too?
- **Recording worlds:** log the committed hash of the frozen worlds in the run. Never import world parameters into learner code; the boundary test should cover transitive imports.

## Tests to add

1. **Noise world, no dynamics:** the fitted velocity coefficient must not be reported as validated, and persistence must not be beaten on fresh evaluation. This guards #1.
2. **No transition rows spanning a reset or wait**, and the next velocity is not computed from a k-tick displacement.
3. **Every scored prediction's timestamp and hash come before the world step's**, including rollouts of `wait(k)`.
4. **The evaluator's sequences are unchanged by whether the learner ran**, and no evaluation outcome ever appears in a fit row.

Everything else can go ahead as planned. I only read `AGENTS.md` and `research/tool_lab.md` and edited nothing. The numbers in #1 are my own derivation, not a test result, and I didn't write a plan file.
