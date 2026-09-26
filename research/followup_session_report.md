# Three experiments: useful memory, an unreliable investigator

Completed 96 bounded investigations and 87 passing tests. Claude Opus 5.5 reviewed every design and result; separate Codex agents researched prior work, implemented components, reviewed code and independently audited numerical evidence. Existing subscription/local computation only; no additional spending. All runs are finished.

| Experiment | Finding | Decision |
|---|---|---|
| A: separate confirmation,36 runs | Stricter/longer checks did not improve predictions. | Stop gate tuning; keep original default. |
| B: construct input-history terms,36 runs | Delayed-world mean error fell 96.7%; random exploration was nearly as good. | A real representation capability, not an active-policy breakthrough. |
| C: unchanged learner in two independently authored worlds,24 runs | Memory improved one world's mean 71.4% against ordinary, but random and sparse regression were better; some poor models stayed unflagged. | Construction/reconsideration and warnings need work. |

The model now can produce an equation using motion, current input and a learned input delay. It does not receive a catalogue of full world laws. We supply the mathematical operators and bounded search; this is known system-identification machinery integrated into an investigation loop, not discovery of new physics or novelty evidence.

A concrete bottleneck emerged: the learner proposed a useful partial hypothesis early, rejected it, later accepted another part, then exhausted its two revision opportunities. A post-run fitter found the combined explanation from the same final observations. That comparison uses more computation and later data, so it does not prove that simply relaxing the gate or adding one attempt will work.

**Next design:** allow the investigator to revisit rejected explanations as evidence accumulates, with the audited sparse model fitter as a construction control and random exploration as an acquisition control. Test the same connected loop; no more threshold changes without a specific failure mechanism. No fourth experiment has been launched.

Only three noise seeds per cell and five deliberately designed laws were involved; this is development evidence. The new-world author saw the grammar, and the higher-capacity offline reference has advantages over the online learner. Replay files show recorded learning, not live training; browser playback is unverified.

[A: check design/result](followup_a_result.md) · [B: memory/result](followup_b_result.md) · [C: new-world/result](followup_c_result.md) · [Research sources](revision_followup_literature.md) · [Memory replay](../results/followup_b/replay.html) · [New-world replay](../results/followup_c/replay.html).
