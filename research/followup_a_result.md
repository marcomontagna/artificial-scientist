# Follow-up A: stricter checks did not improve the learner

All36declared runs completed using clean e1317cd;80training/68evaluation units each,3.09CPU seconds total. Independent audit checked40cycles, source/journal identity, all prediction losses and decisions with zero discrepancy. The default had already reproduced36old traces exactly.

| External prediction MSE (lower better) | Original | Pooled | Confirm short | Confirm long |
|---|---:|---:|---:|---:|
| Simple control | .000620 | .000620 | .000620 | .000620 |
| Coupled challenge | .000665 | .000665 | .000665 | .000665 |
| Delayed stress | .020086 | .021992 | .021992 | .022290 |

The predeclared long rule fails the encouraging criteria against both pooled and short: neither control nor stress mean improves, and harmful counts cannot fall because no harmful frozen-snapshot adoption occurred on these seeds. All challenge rules retain3/3useful revisions. Stress adoptions are2/1/1/0; useful accepted snapshots1/0/0/0; missed-useful decision candidates0/2/2/1. Zero-adoption rates are undefined. Long is1.35%worse than short and10.97%worse than original on this small stress sample. This is not a precision benefit.

The first-cycle short/long histories and candidates match; their sole decision difference is stress280002, where long rejects a non-harmful candidate whose external improvement falls below the useful-revision margin. Later histories/candidates diverge, so missed counts need not be monotone in total rejections. Independent audit verified those candidate-specific counts. Control/challenge equality concerns final predictions; extra checking still consumes different internal resources.

Claude agrees to stop gate tuning and recommends testing public-history features with a flat regression reference. Its assertion that locally restarted predictions necessarily reset memory is not true of the planned semantics: memory is reconstructed from recorded action history at each start, then advanced using planned actions. Likewise short checks can observe delayed effects from earlier actions; they cannot reveal every delay caused by a new push. Those limits must be tested and disclosed. No fixed bank is selected from evaluator losses.

The next capability question is whether the learner can construct a useful temporal feature from its own action history, propose it after failures and validate it prospectively. Representation benefit and active-experiment benefit need separate controls. No default changes here; new seeds on familiar laws remain development evidence, not generalization or novelty.

[Protocol](followup_a_design.md) · [All outcomes](../results/followup_a/summary.json) · [Independent audit](../results/followup_a/independent_audit.json) · [Claude critique](claude_followup_a_result.md) · [Predeclared replay](../results/followup_a/replay.html). Browser playback remains unverified.
