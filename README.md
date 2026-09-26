# Artificial Scientist

Build an agent that enters an unfamiliar simulated world, uses tools to investigate it, constructs explanations, and chooses its next experiment from what it has learned.

The ambition is an unexpected, useful insight—a “Move 37” moment. That is a long-term aspiration, not a promised outcome or an AGI claim. Understanding is the objective; a game score is optional.

## Active direction

One persistent physical laboratory: first a single object moving in 2D, with hidden motion rules. The agent can observe, push, wait and reset. It keeps a notebook, proposes executable models from declared building blocks, makes predictions before acting, and revises models that fail. We supply an interface and learning machinery, not a catalogue containing the correct world explanations.

**Current status: repository refocused; the new laboratory and agent are not implemented yet.** No learner or experiment is running. The previous toy studies are retired from the active codebase. Their complete code, tests, reports and results remain accessible through the [archive](archive/README.md); local raw runs remain untouched.

[Direction](research/direction.md) · [First complete laboratory design](research/tool_lab.md) · [Next deliverable](NEXT_STEPS.md) · [Claude’s review and decisions](research/reset_decisions.md)

## Working rules

- Build one complete investigation loop before adding more worlds or machinery. Tests and measurements support that loop; no more disconnected statistical exercises.
- Keep assumptions, failed explanations and limits visible. A surprising action or a nonrejected model is not proof of discovery.
- Reuse established methods and cite them. A working prototype does not need a novelty claim; a scientific contribution does.
- Local Apple Silicon/Python 3.9+; no required MLX, new service, paid API or extra spending. Every substantive artifact gets an independent review.

Only package scaffolding remains active; there is no new runnable laboratory command or active test suite to advertise. Follow the [workflow](research/workflow.md) when implementing it. [Lessons retained](research/lessons.md) · [Closest references](research/references.md).

MIT; see [LICENSE](LICENSE). Archived third-party references keep their original attribution.
