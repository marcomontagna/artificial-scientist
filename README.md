# Artificial Scientist

Build an agent that enters an unfamiliar simulated world, uses tools to investigate it, constructs explanations, and chooses its next experiment from what it has learned.

The ambition is an unexpected, useful insight—a “Move 37” moment. That is a long-term aspiration, not a promised outcome or an AGI claim. Understanding is the objective; a game score is optional.

## Active direction

One persistent physical laboratory: first a single object moving in 2D, with hidden motion rules. The agent can observe, push, wait and reset. It keeps a notebook, proposes executable models from declared building blocks, makes predictions before acting, and revises models that fail. We supply an interface and learning machinery, not a catalogue containing the correct world explanations.

**Current status: the agent can detect failed predictions, test competing model revisions and adopt one before refitting.** Fifty-nine tests pass; 45 bounded runs are finished. On the new coupled-motion world, all three active runs added cross-coordinate motion and improved unused predictions. One simple-control run revised unnecessarily, and the delayed-effect stress case remains unresolved. These are capability demonstrations within supplied operators, not a novelty or general-discovery claim.

[Latest revision-loop results](research/revision_loop_result.md) · [Revision replay](results/revision_v1/replay.html) · [Exact design](research/revision_loop_design.md) · [Earlier progress assessment](research/progress_assessment.md)

The earlier disconnected studies remain in the [archive](archive/README.md); their raw runs are untouched.

[Direction](research/direction.md) · [First complete laboratory design](research/tool_lab.md) · [Next deliverable](NEXT_STEPS.md) · [Claude’s review and decisions](research/reset_decisions.md)

## Working rules

- Build one complete investigation loop before adding more worlds or machinery. Tests and measurements support that loop; no more disconnected statistical exercises.
- Keep assumptions, failed explanations and limits visible. A surprising action or a nonrejected model is not proof of discovery.
- Reuse established methods and cite them. A working prototype does not need a novelty claim; a scientific contribution does.
- Local Apple Silicon/Python 3.9+; no required MLX, new service, paid API or extra spending. Every substantive artifact gets an independent review.

Run the local prototype from the repository root (Python 3.9+, no runtime dependencies):

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m artificial_scientist.lab_run --variant development --output results/runs/my_fresh_run
```

Use a new output directory; the laboratory command runs active, random and coverage exploration and generates their saved replays. For evidence-guided local proposals, add `--proposal guided --policies active`; use `--proposal guided-partial` for the conditioned variant. The default remains `enumerate`. [Guided design and limitations](research/guided_proposal_design.md) · [Implementation assumptions](research/tool_lab_implementation.md) · [Workflow](research/workflow.md). [Lessons retained](research/lessons.md) · [Closest references](research/references.md).

Run the new revision loop with a fresh output directory:

```sh
.venv/bin/python -m artificial_scientist.revision_run --variant challenge --policy active --seed 270001 --output results/runs/my_fresh_revision
```

The original laboratory command remains available and unchanged.

MIT; see [LICENSE](LICENSE). Archived third-party references keep their original attribution.
