## Recommendation: bounded equation discovery in three conditional steps

I read `AGENTS.md`, `research/direction.md` and `research/stateful_room_result.md`, and nothing else was run. The polynomial-structure search you suggested is a reasonable first step: it is transparent, needs only the standard library, and is cheap. On its own, though, it is textbook best-subset regression. The "revise" part of the destination only gets tested if a world can reject the grammar the agent was given, so outside-grammar falsification should be part of experiment 1, not left for later.

**Detour to challenge:** the stateful-room report proposes a history-aware predictor as the next step. That tests hidden memory, not building formulas. Defer it until after tonight and record the deferral.

### Experiment 1: find the structure under a fixed sampling plan, and detect when the grammar is wrong
- **World:** the agent sets inputs x∈[−1,1]³ and observes y = f(x) + Gaussian noise. The hidden f comes from a generator:
  - (a) in-grammar: 1–4 monomials of degree ≤3 with random coefficients;
  - (b) outside-grammar: x₁/(1+x₂²), exp(x₁), a step, sin;
  - (c) noise-only.
- **Learner:** always includes a constant, then tries every subset of up to 4 of the other 19 monomials (5,036 structures). It fits each by least squares, weights structures by BIC, and reports the top structures with their weights, not a single "law".
- **Grammar-failure check:** use a classical lack-of-fit F-test, with replicate points inside the budget to estimate pure noise. Then run a predict-before-observe check on independent points.
- **Baselines, same N ∈ {16, 32}:**
  - full 20-term ridge regression;
  - sequential-threshold sparse regression (the SINDy-style method);
  - k-nearest neighbours.
- **Metrics:**
  - interpolation error and extrapolation error in the [−2,2]³ shell (extrapolation is where getting the structure right should matter);
  - exact-structure recovery;
  - false-reject rate on in-grammar worlds and false-accept rate on outside-grammar worlds.
- **Falsifiers:** fix these thresholds before running. Proposed values:
  - at high signal-to-noise and N=32, exact recovery is below 70%;
  - extrapolation is no better than sparse regression and ridge;
  - outside-grammar false-accept is above 20%;
  - in-grammar false-reject is above 10%;
  - noise-only worlds produce confident nonzero structures.
- **Stop rules:**
  - Recovery fails → treat it as a bug or a grammar that's too large, fix it and stop there.
  - Detection fails → experiment 3 as designed has no basis; revise detection first.
- **Known-method overlap:** BIC subset selection, SINDy, BACON-style discovery (Langley), AI Feynman, lack-of-fit F-test. Nothing here is novel. Recovering a law the generator planted inside the grammar shows the implementation works, not that anything was discovered.

### Experiment 2 (only if experiment 1 passes): choose the sampling points actively
Keep the same N. The agent picks each next x where the top-weighted structures disagree most, compared with expected noise. This is design for telling models apart, in the Box–Hill style. Compare against random sampling and a space-filling Latin-hypercube design, with an identical budget that includes the replicate points.
- **Falsifier:** at N=16, active sampling fails to beat the space-filling design on structure recovery and on extrapolation by a preset margin, or it does worse on noise-only and outside-grammar controls.
- **Overlap:** Bongard & Lipson (2007) did active experiments for symbolic model inference, and Schmidt & Lipson (2009) is related. A negative result is acceptable. If it fails, run experiment 3 with the space-filling design.

### Experiment 3 (only if experiment 1's detection passes): revise the grammar
When the falsification test fires, the agent adds a second, larger library (1/(1+x²), exp, log|x|, thresholds, products) and refits on its remaining budget.
- **Comparators at equal N:**
  - always using the large library from the start;
  - never revising.
- **Falsifier:** always-large matches staged revision on outside-grammar worlds without hurting in-grammar worlds. In that case, report that revision only saves compute.

This is the "expand only when evidence demands it" question from the frozen first question, now asked about formulas. Keep in mind that the expanded library is still supplied by us, so this is selection from a bigger menu, not invention.

**Protocol for all three:**
- Separate development seeds from held-out seeds, and keep one held-out outside-grammar family.
- Fix thresholds before any run and don't tune on held-out seeds.
- Record timings.
- Each run should take well under 10 minutes on a CPU.

### What counts as structure discovery vs coefficient fitting
Within a supplied grammar, "structure" only means which terms were selected. The coefficients are ordinary fitting. We should report structure recovery and coefficient error separately. A formula outside the grammar can only be claimed if the expanded search finds it, and even then it came from a library we wrote.

### Strongest objections
1. **No novelty:** each piece exists already (subset selection, SINDy, BIC, lack-of-fit tests, active model discrimination). The best-case outcome is a clean, reviewed, working loop, not a contribution.
2. **The laws are designed:** laws planted inside the grammar are recoverable by construction. The honest signal is extrapolation, behaviour on controls, and detecting when the grammar is wrong.
3. **Identifiability:** monomials are strongly correlated on a bounded box (x and x³ especially). Several structures can fit the data, so "exact recovery" may understate real equivalence. Report the top structures and their weights.
4. **It drops state:** a static input–output function is less of a "world" than the rooms were. Dynamics (x_{t+1} = f(x_t, a_t)) and hidden state are left out tonight. If all three pass, revisit them.
5. **The detector depends on the noise model:** the F-test assumes constant Gaussian noise, so non-constant or heavy-tailed noise could trigger false revisions. Add one such control.
6. **Budget accounting:** replicate points used by the detector have to count toward N for every method, including the baselines.

For the coordinator, the precise next inputs are the generator's parameter ranges, the pre-registered thresholds, and seed allocations. I'll critique experiment 1's plan before anything runs.
