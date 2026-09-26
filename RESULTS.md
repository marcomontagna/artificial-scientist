# Results

**First complete tool-using investigation implemented and run.** Twenty focused tests pass; nine bounded runs completed. [Full concise report](research/tool_lab_result.md) · [Offline replay](results/tool_lab_v1/replay.html).

The active development learner produced `delta ≈ 0.797*v + 0.420*u` and predicted fresh interventions much better than persistence. Random exploration did better than active in that world; coverage did better on the harder challenge. Noise-world behavior resembles predicting the known home position. This is a connected learner with inspectable formulas, not a novel discovery or consistently superior experiment chooser. One seed per world; no generalization or significance claim.

Claude Opus 5.5 reviewed plan and code; separate Codex agents reviewed implementation and independently recomputed recorded results. Source was frozen before the first demonstration. Browser playback is not verified because local-file navigation was blocked; exporter safety and trace tests passed. No extra spending; no experiment is running.

[Summary](results/tool_lab_v1/summary.json) · [Exact contract](research/tool_lab_implementation.md) · [Next step](NEXT_STEPS.md).

The prior statistical studies are retired, not erased. Their [immutable archive](archive/README.md), [last historical result](research/equation_revision_result.md) and [RNG correction](research/equation_domain_rng_erratum.md) remain accessible. Historical test counts do not describe the current implementation.
