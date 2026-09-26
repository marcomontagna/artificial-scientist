# Results and traces

`partial_v1/` contains the latest six-run conditioning repair comparison, full prefix diagnosis, raw hashes and harder-world replay. Earlier proposal timing did not improve harder-world prediction. [Latest report](../research/partial_proposal_result.md). Raw runs are preserved under ignored `runs/partial_v1_*`.

`guided_v1/` contains the earlier six-run selective-proposal comparison, source/raw hashes and a self-contained evidence-to-choice replay. The default enumeration control exactly reproduces v1 behavior. [Earlier result](../research/guided_proposal_result.md). Raw data remain under ignored `runs/guided_v1_*`; no prior output was overwritten.

`tool_lab_v1/` contains the first connected investigator’s compact summaries, raw-file hashes and self-contained development/active replay. [Result report](../research/tool_lab_result.md).

All nine original traces, before-action journals and per-policy replays remain under ignored `runs/tool_lab_v1_*` directories. Do not overwrite them. The tracked replay embeds its original trace. Reproduce with the frozen source and commands in the report; timing fields may vary.

Earlier runs are preserved under `runs/`, with their source/tests/reports in the [Git archive](../archive/README.md). They are not current learner dependencies.
