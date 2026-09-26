# Next deliverable

**Build one visible, complete investigation in the physical laboratory.** This replaces the earlier fixed-fitter desk-review assignment. No further standalone equation, calibration or selector studies.

1. Implement the observation/action boundary and one persistent 2D object. A separate agent defines the hidden dynamics and an evaluator-only challenge; the learner receives observations and permitted tools only. Fix tool costs, reset behavior and a short run budget before coding the planner.
2. Connect memory → executable model proposals → predicted experiments → tool use → observation → revision. Use bounded local search over declared primitives. Keep competing explanations and an explicit “unexplained” outcome; do not script the solution or call Claude to choose every action.
3. Produce one replay showing actual actions, frozen predictions, competing models and revisions. Check its independent-intervention predictions against the same learner with random actions and a simple coverage policy. These checks belong to the prototype, not another separate research programme.

Start with the [reviewed design](research/tool_lab.md). A trace with every component genuinely connected is the engineering milestone. Useful new understanding must also survive fresh interventions; an attractive animation or unusual action alone does not count. More objects, hidden law changes, transfer, RL and neural models come only when they solve a demonstrated need.

[Claude review and adopted decisions](research/reset_decisions.md). Current cleanup created no new laboratory implementation or experimental result. No extra spending.
