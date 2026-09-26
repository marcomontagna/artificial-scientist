# Direction reset — September 26, 2026

The user’s objective is an artificial scientist investigating an unfamiliar world with tools. “Move 37” is an aspiration for a useful, unscripted discovery, not a promised result. Stop expanding disconnected statistical studies; build one complete investigation loop.

## Independent consultation

Claude Opus 5.5 reviewed the proposed direction and cleanup through the official CLI using the previously verified Pro subscription. Its [verbatim review](claude_direction_reset.md) and [provenance hashes](direction_reset_claude_provenance.json) are retained. No paid API or new service was used.

Accepted: retire the old study lines together; preserve their source, results and tests in Git history; remove the old requirement to establish novelty before building a learner. Known components can support a useful prototype. Novel scientific claims still require evidence and prior-art comparison.

Accepted: tools alone are insufficient. Supply memory, an objective, model-building primitives, a bounded search and an experiment chooser. Expose these assumptions. Separate hidden dynamics from the learner; record predictions before outcomes; account for noise and tool costs; compare with simple random and coverage exploration within the same working prototype.

Modified: generated models use a restricted interpreter, never arbitrary host code. An independently authored challenge reduces co-design but does not establish formal blinding. An unusual action, collapsing model committee or human surprise is insufficient for a “Move 37” claim: require reproducible benefit on independent predictions or planning.

Deferred: a five-world suite, multiple objects, changing laws, learned representations and reinforcement learning. First build one visible loop in a small 2D laboratory. Add complexity when a working loop exposes a concrete limitation. Claude’s additional literature suggestions are leads, not verified novelty clearance; the [reference note](references.md) distinguishes checked sources.

## Cleanup and current state

[188 retired paths](../archive/retired_paths.json) are recoverable from commit `0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9`. All 181 local raw-run files retained their sizes and modification times during removal. The historical seed ledger and RNG correction remain available. Keep three [lessons](lessons.md), not old experiments as active dependencies.

The active Python package is a scaffold. No new agent, replay or experiment was implemented or run in this reset. The next deliverable is the [tool laboratory](tool_lab.md), with an actual investigation trace, independently reviewed code and focused tests.
