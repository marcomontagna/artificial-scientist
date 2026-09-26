# Independent design review: persistent-lab reset

I read README.md, research/direction.md, NEXT_STEPS.md, research/revision_result_response.md, AGENTS.md, CLAUDE.md, research/seed_registry.md and the package listing. I made no edits.

## Keep / delete

**Retire** all six study lines by pointing to commit `0c7c3e4`: sequence/selector, causal, switch lab, stateful room, equation modules, and their tests, configs, visualizations and reports. Also retire `SwitchingBernoulli`, the smoke runner, and the `baselines/`, `environments/` and `metrics/` stubs, because a Bernoulli stream is not a lab. Leave ignored `results/runs/` untouched.

**Keep:** LICENSE, pyproject, .gitignore, and AGENTS.md/CLAUDE.md with the spending, safety, review and resource rules. Add a short `research/lessons.md` with three lessons:
1. Efficient pooled fitting beat revision.
2. Random exploration beat information-seeking on the noise control.
3. "Not rejected" never meant "true."

Also add a one-paragraph seed note: used seeds are burned; start a fresh range.

**Fix these, or agents will stall:**
- AGENTS.md says "challenge novelty before implementing a new learner" and "avoid bespoke architectures until a surviving question." The new destination needs an explicit exemption.
- NEXT_STEPS.md still points at the fixed-fitter design desk review. Replace it rather than stacking on top of it.

## Smallest coherent deliverable

1. **`lab/`**: one 2D point object. The only reading is a noisy position. Velocity is not given, so the agent must infer it with temporal primitives.
   - Tools: `push(angle, magnitude≤M)`, `wait(k≤K)`, `observe`, `reset`. Each has a declared time cost, within a single step budget.
   - Hidden laws live in a sealed evaluator module that the learner package must not import. Add a test for this.
   - Decide whether `reset` returns a fixed start or a random one. A fixed start is a privileged tool.
2. **`agent/`**: an append-only log and a small primitive set. Suggested primitives: `+ − × ÷`, `sign`, `abs`, `prev(x)`, `if a<θ then b else c`, `region(x,y)`, and fitted constants.
   - Proposals: enumerate programs bottom-up by size and fit constants by least squares. When a prediction fails, propose a split into regimes (separate conditions) for that failure.
   - Keep a committee of the top-K structurally different programs, rescored on the full log. Score = held-out log-likelihood minus description length.
   - Before each outcome, write every committee member's prediction to the log with a hash, so predictions are frozen.
3. **Replay**: a JSONL record per step (action, frozen predictions, outcome, committee added/removed/refit). Start with a text viewer; HTML can wait.

## Missing assumptions and objective

- **Exploration objective:** choose the action that maximises expected disagreement between committee members, beyond what the estimated noise explains, per unit time cost. Never use raw surprise, which is lesson 2 again.
- **Stopping rule and search budget:** state the maximum program size, a CPU-seconds limit, and what the agent reports when nothing fits. It should answer "unexplained residual in regime R", not silently overfit.
- **Supplied assumptions to state openly:** Cartesian coordinates, discrete time step, and a Gaussian noise model.
- **Worlds where experiment choice can matter.** If friction is smooth and linear, random pushes plus ordinary regression will win again. Include at least:
  - static friction with a threshold (small pushes do nothing);
  - drag or friction that depends on direction;
  - a hidden surface region, such as an ice patch or slope, that only targeted pushes reach;
  - a delayed response;
  - a pure-noise/null world.
- **Author separation:** the grammar makes "no hand list" true in form only; the author still shapes what is reachable. A different agent should write the hidden laws and commit a hash before the learner exists. Include one law the author did not anticipate but the grammar can express, and one it cannot express. Without this separation, "discovery" is authored.

## First end-to-end check (bounded, not a study)

The same learner under three policies, with an equal time budget and roughly 5 worlds:
- chosen experiments;
- random actions;
- a coverage policy that sweeps magnitudes and directions.

Coverage is essential because random can lose to it trivially.

Evaluate on independent interventions drawn by the evaluator, including extrapolation: magnitudes outside anything tried, and unvisited regions. Report two things per world:
- prediction error;
- whether the final program has the right regime structure.

Write down pass/fail before running. Add one non-explanatory predictor (nearest-neighbour on history) given the same data, to test whether explicit models buy extrapolation. That is a control, not a statistics programme.

## When is an insight meaningful?

"Move 37" here is an experiment that meets all four conditions:
1. Random and coverage policies rarely or never take it (low logged frequency).
2. It removes most of the competing explanations in one step.
3. It exposes a law the author did not script the agent to look for.
4. A human sees it as sensible only after the fact.

Example: pushing gently just under the threshold, repeatedly, at one location. Surprise alone doesn't qualify, and neither does a rare action. Any claim covers the implemented simulator only.

## Prior art (from memory, not verified this session)

Check these before claiming anything:
- Denil et al. 2017, agents pushing blocks to infer mass;
- Wu & Tegmark 2019, *AI Physicist*;
- Tsividis et al. 2021, EMPA;
- Das et al. 2023, AutumnSynth;
- Tang, Key & Ellis 2024, WorldCoder.

This is established territory. Frame it as building the loop, not claiming novelty.
