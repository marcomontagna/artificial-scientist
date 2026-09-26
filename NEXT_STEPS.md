# Next: reconsider explanations as evidence grows

[Three-study report](research/followup_session_report.md):96 investigations finished; 87 tests pass. Input-history construction improved predictions, but active exploration remains weaker than simple controls and the learner sometimes stops with a poor partial explanation. No experiment is running.

Review a bounded design that lets rejected hypotheses be reconsidered using newly acquired evidence. Compare whole-model construction with the audited sparse history fitter and keep random exploration as the acquisition control. The observed bottleneck combines early rejection, additive proposals and a two-cycle cap; adding another cycle or lowering a threshold is not yet a validated repair. Completed-data success does not prove the early online decision had enough evidence.

Keep the connected observe→propose→predict→act→revise loop. Preserve current defaults and negative results, use no hidden-law hints, and have Claude review the next design/results with independent code/numerical checks. No extra spending or automatic chain.
