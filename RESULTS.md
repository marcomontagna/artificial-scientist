# Results

**Latest: an evidence-driven modeling-assumption revision works on the declared coupled-motion challenge.** Mean active error is 0.000679 versus 0.087390 without revision, 0.000971 with random revision and 0.000920 with coverage revision. These are three sensor-noise seeds per world, not generalization evidence. One active simple control expanded unnecessarily; all active delayed-stress runs remain unresolved and their mean error worsens versus no revision.

59 tests passed; all 45 fixed runs completed without tuning. Claude critiqued design and results; independent agents reviewed code and recomputed recorded errors/decisions.

[Latest report](research/revision_loop_result.md) · [Saved revision replay](results/revision_v1/replay.html) · [Next step](NEXT_STEPS.md).

## Earlier proposal-conditioning repair

**One proposal-scoring failure repaired, without a harder-world prediction gain.** The useful motion-plus-push model enters at step 11 instead of 39, but final harder-world error rises slightly (0.053171 → 0.053795). Simple-world error improves slightly; noise error worsens slightly. Keep the repair optional. Thirty-two tests passed; six runs completed without tuning.

[Earlier report](research/partial_proposal_result.md) · [Harder-world replay](results/partial_v1/replay.html) · [Next step](NEXT_STEPS.md).

## Earlier observation-guided comparison

**Observation-guided hypothesis proposals implemented; results are mixed.** Twenty-eight tests pass. Guided prediction error improved in the simple world (0.001237 → 0.000288), worsened in the harder world (0.026477 → 0.053171), and was slightly worse in noise. Proposal fits fell sharply, but that alone is not a practical success. Enumeration remains the default.

[Earlier report](research/guided_proposal_result.md) · [Evidence → proposal → choice replay](results/guided_v1/replay.html) · [Next decision](NEXT_STEPS.md).

The selective mechanism was reviewed by Claude and independently audited. No human-cognition, causal-discovery or novelty claim. These are previously inspected developmental checks, not independent confirmation. Runs are finished; no extra spending.

## Earlier first-loop demonstration

**First complete tool-using investigation implemented and run.** Twenty focused tests pass; nine bounded runs completed. [Full concise report](research/tool_lab_result.md) · [Offline replay](results/tool_lab_v1/replay.html).

The active development learner produced `delta ≈ 0.797*v + 0.420*u` and predicted fresh interventions much better than persistence. Random exploration did better than active in that world; coverage did better on the harder challenge. Noise-world behavior resembles predicting the known home position. This is a connected learner with inspectable formulas, not a novel discovery or consistently superior experiment chooser. One seed per world; no generalization or significance claim.

Claude Opus 5.5 reviewed plan and code; separate Codex agents reviewed implementation and independently recomputed recorded results. Source was frozen before the first demonstration. Browser playback is not verified because local-file navigation was blocked; exporter safety and trace tests passed. No extra spending; no experiment is running.

[Summary](results/tool_lab_v1/summary.json) · [Exact contract](research/tool_lab_implementation.md) · [Next step](NEXT_STEPS.md).

The prior statistical studies are retired, not erased. Their [immutable archive](archive/README.md), [last historical result](research/equation_revision_result.md) and [RNG correction](research/equation_domain_rng_erratum.md) remain accessible. Historical test counts do not describe the current implementation.
