# Results

**Latest: observation-guided hypothesis proposals implemented; results are mixed.** Twenty-eight tests pass. Guided prediction error improved in the simple world (0.001237 → 0.000288), worsened in the harder world (0.026477 → 0.053171), and was slightly worse in noise. Proposal fits fell sharply, but that alone is not a practical success. Enumeration remains the default.

[Latest report](research/guided_proposal_result.md) · [Evidence → proposal → choice replay](results/guided_v1/replay.html) · [Next decision](NEXT_STEPS.md).

The selective mechanism was reviewed by Claude and independently audited. No human-cognition, causal-discovery or novelty claim. These are previously inspected developmental checks, not independent confirmation. Runs are finished; no extra spending.

## Earlier first-loop demonstration

**First complete tool-using investigation implemented and run.** Twenty focused tests pass; nine bounded runs completed. [Full concise report](research/tool_lab_result.md) · [Offline replay](results/tool_lab_v1/replay.html).

The active development learner produced `delta ≈ 0.797*v + 0.420*u` and predicted fresh interventions much better than persistence. Random exploration did better than active in that world; coverage did better on the harder challenge. Noise-world behavior resembles predicting the known home position. This is a connected learner with inspectable formulas, not a novel discovery or consistently superior experiment chooser. One seed per world; no generalization or significance claim.

Claude Opus 5.5 reviewed plan and code; separate Codex agents reviewed implementation and independently recomputed recorded results. Source was frozen before the first demonstration. Browser playback is not verified because local-file navigation was blocked; exporter safety and trace tests passed. No extra spending; no experiment is running.

[Summary](results/tool_lab_v1/summary.json) · [Exact contract](research/tool_lab_implementation.md) · [Next step](NEXT_STEPS.md).

The prior statistical studies are retired, not erased. Their [immutable archive](archive/README.md), [last historical result](research/equation_revision_result.md) and [RNG correction](research/equation_domain_rng_erratum.md) remain accessible. Historical test counts do not describe the current implementation.
