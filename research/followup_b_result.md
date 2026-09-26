# Follow-up B: the learner constructs useful input memory

36fixed investigations completed using clean2b0eca1,80training/68evaluation units perrun,4.62CPU seconds total.78tests pass and default behavior reproduces36old traces exactly. Independent audit checked47cycles, all losses, budgets, frozen decisions and every external prediction using a separate lag-aware interpreter; zero discrepancy.

| Mean external MSE | Ordinary active | History active | History random | History coverage |
|---|---:|---:|---:|---:|
| Control | .002070 | .001981 | .000925 | .002055 |
| Coupled | .001074 | .001053 | .000600 | .000417 |
| Delayed stress | .020657 | .000676 | .000697 | .007948 |

The frozen capability screen passes:96.7%lower mean stress error,3/3paired improvements and both simpler-world caps. Per-seed ordinary→historyactive: .015473→.000673, .029691→.000600, .016808→.000756. The median falls .016808→.000673; this is not one outlier creating the gain. All three history-active and random runs select cross-input lag11. One active run also retains own-input lag13; one coverage run retains only that alias and predicts poorly. Constructing a good approximation does not establish the exact true law.

The language expansion is useful; active acquisition remains unproven. Random does better on control and coupled means and nearly matches active on stress. History-active has0harmful and3useful frozen stress adoptions versus ordinary's1harmful/0useful. Here harmful means worse than that candidate's OWN frozen incumbent, not absolutely bad or structurally false. The bad coverage run can improve its incumbent slightly yet remain inaccurate; its0harmful count is not safety certification. Its no-recent-failure status also misses external error.

Flat39feature ridge on the same active histories has stress MSE.001928 versus sparse learner.000676, but wins on coupled means and varies sharply with action history. The audit verified its78coefficients and rollouts; it did not independently solve the coefficient systems. Weak regularization and correlated acquisition remain possible causes of instability. Preserve its results, but do not advertise superiority to strong system identification. History search costs56–92candidate fits on average bycell versus26–51ordinary; action budgets match, compute does not.

Claude reviewed the outcome and supports testing new laws with the learner frozen, plus a better specified sparse history-regression reference and an external-error/status table. We accept that direction. Corrections: ordinary already has lag1; memory construction supplies longer lag operators. The frozen relative-harm definition is internally correct and does not diagnose absolute adequacy. No unresolved status is calibrated confidence.

Next: an independently authored two-world check, with source/specification sealed before runs and unchanged learner settings. Keep random as an acquisition control. These known-method integrations and three noise seeds do not establish novelty or general discovery.

[Design](followup_b_design.md) · [All outcomes](../results/followup_b/summary.json) · [Independent audit](../results/followup_b/independent_audit.json) · [Claude critique](claude_followup_b_result.md) · [First-seed replay](../results/followup_b/replay.html).
