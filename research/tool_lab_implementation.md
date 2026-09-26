# First implementation contract — September 26, 2026

Fixed before the first demonstration. This is one integrated prototype, not a novelty or superiority study. World/API source was independently authored and frozen at `e6920e7` before learner execution. The coordinator later reviewed it: this prevents runtime source access, not formal developer blinding.

## Runtime and representations

The learner receives immutable initial/after observations (tick, noisy x,y), its actions and their costs. It never receives a world object. Initial/home position and velocity are zero by public contract; reset occupies eight ticks at home and does not rewind sensor noise. Invalid requests are rejected before execution/time/noise mutation; executed commands all count. Wait has zero input on every tick; push acts only on its first tick.

Models predict position through `p_next = p + delta`. Delta is a sum of one or two coefficient-weighted expressions. Primitives: p, v (last observed displacement/elapsed time), u (current component input), lag_u (previous tick input), 1; abs, positive-part, multiplication. The generator includes unary abs/positive on p,v,u; pair products of those variables; variable times its absolute value. It does not enumerate every possible AST. Weighted displacement ASTs are at most 12 nodes, including coefficients/multiplications/addition; the outer position addition is a fixed wrapper. Coefficients are shared across axes, with no cross-axis features: this is a **separable shared representation**, not rotation invariance. It cannot express arbitrary laws, division, thresholds with arbitrary offsets, or hidden memory.

Ridge least squares (diagonal penalty 1e-4), coefficient clamp [-10,10], fits one-tick rows with an available one-tick previous interval, or initial/reset zero velocity. Exclude reset transitions, multi-tick transitions and the immediate transition after a multi-tick interval from fitting. Planning after a multi-tick observation uses its average-velocity proxy; mark this limitation. Open-loop evaluator rollout carries its model’s predicted final velocity across actions. Predicted values clamp to ±1000 for bounded execution. No eval/exec or host-code access.

Start with zero displacement and constant-velocity predictors. Refit after each outcome. Every fourth executed action, or after a prediction failure, propose at most 2 structures using in-sample error plus 1e-4 times complexity, then retain the best (8 minus new proposal count) existing models and add the proposals. Existing models rank on their shared most recent prediction window (max 12); new models have zero fresh evidence. The final choice needs at least 3 past predictions where available. Scores describe the structure **plus its refitting procedure**, not validation of today’s coefficient values. Formula coefficients and revisions are logged; maximum 8 live models. Ties use deterministic expression IDs.

## Experiment choice

Eight pushes (four cardinal directions × magnitudes 0.3/1), observe, wait 2, wait 4, reset. Four-action coverage warmup. Then score each affordable action as `[min(1,max(0,committee position variance − 2*home sensor variance estimate)) + 0.02/(1+action visits)] / cost`. This is a one-tool planning horizon, including multi-tick waits. Ties follow fixed action order. Random and coverage policies use the same learner/update/search, budget and tool menu; random uses a separate action RNG.

Sensor variance is estimated only from initial/reset readings of the known zero home position, averaged over axes. Few such readings make this weak; stationarity and independent measurement noise are supplied assumptions. Residual model error is never automatically called sensor noise. All candidate predictions and scores are copied into a flushed JSONL journal before step(), then outcome/errors and revisions are appended to the final trace. This is observable program ordering, not a cryptographically trusted timestamp service.

## Fresh checks and limits

One fixed seed 260926 for each development/challenge/noise world; three exploration policies, 80 training cost units each. Complete development first; challenge and noise only afterwards, without tuning. Fixed evaluator sequences in lab_run.py include off-menu angles/magnitudes, repeated pushes and waits. Each starts reset/home in a fresh world/noise stream, identical for all policies. Freeze complete open-loop prediction tapes before their evaluated actions. Evaluator observations never enter fitting. Report squared position errors at each action horizon and their overall average, with frozen persistence and four-term linear-regression references fitted from the same training rows. References are evaluation tools, not candidate hints.

A completed integration means models propose, predict, drive actions and revise with honest saved evidence, plus fresh checks. It need not beat random. Noise can support useful denoising predictors without exposing any physical law. One seed is descriptive and correlated; it supports no statistical superiority or discovery claim.

Each investigation caps learner plus evaluator at 120 process CPU seconds, 80 training tool-cost units and 10 MB combined trace/journal. Evaluation costs are reported separately (identical sequences); replay export is outside the CPU and trace/journal byte caps and bounded by the trace input. Search checks the deadline per candidate; other small atomic operations can exceed a deadline slightly. No backgrounds or extra paid inference. A fresh output directory is required; no prior runs are overwritten.

## Claude’s review and response

[Verbatim critique](claude_tool_lab_plan.md), [provenance](tool_lab_claude_provenance.json). Accepted lagged input, exact wait/reset fitting eligibility, fixed fresh multi-action evaluation, fixed linear reference, common-window structure ranking, and descriptive single-seed status.

Disagreed with two suggestions. Rewriting displacement regression as next-position prediction is algebraically identical and does not remove noisy-difference bias. Also, a noise-derived predictor can beat last-observation persistence by denoising; a test demanding it never does would encode a false expectation. We disclose this bias, evaluate predictions independently, and do not certify physical coefficients. We estimate measurement noise from the supplied known-home privilege instead of treating best-model residuals as pure noise. Unknown dynamics remain unexplained.


## Code-review amendments fixed before running

[Claude’s independent code review](claude_tool_lab_code.md) confirmed the connected loop and no identified evaluator leakage. It correctly challenged unweighted disagreement and purely scheduled revision. Votes now use normalized `exp(-min(50,(common_window_MSE-best_MSE)/scale))`, with `scale=max(2*home_noise,best_MSE,1e-6)`; models with fewer than three fresh predictions get provisional weight0.25 before normalization when mature models exist. These are heuristic influence weights, not probabilities. We preserve a seen-structure set so discarded formulas cannot return with erased evidence.

A prediction-failure trigger compares the previously best structure’s latest error to `max(4*its_previous_recent_mean,8*home_noise,1e-4)`. It supplements the four-action schedule, with at least two actions between searches. This is a declared heuristic, not a calibrated anomaly test. Added tests exercise actual post-warmup argmax choice, weighting, failure triggers and no re-proposal churn. A fixed predict-home reference joins persistence/linear in evaluation.

The development law lies within the supplied grammar; matching it is a plumbing check. The independently specified challenge has cross-axis/direction dependence outside the current shared separable representation. Its limitations cannot establish novelty. Noise-world home prediction is a supplied privileged baseline. Claude suggested development only; we retain the already fixed scope of development followed by one challenge and noise control, with no tuning or additional seeds. This completes the small integration check rather than beginning a new study.
