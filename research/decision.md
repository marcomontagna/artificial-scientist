# Research decision for tomorrow

> Historical decision, superseded by [current direction](direction.md). Candidate 2 remains optional replication groundwork; representation revision across procedural universes is now the candidate for focused review. Do not start the old implementation plan by default.

2026-09-25. Director for this pass: Codex primary, with a distinct Codex adversarial reviewer. No Claude participation is attributed.

**Select candidate 2 as a replication/stress test of existing acquisition methods. No candidate has passed a methodological novelty gate.** The useful question is whether predictive-information acquisition retains an advantage under hidden changes and wrong likelihood assumptions, after separating acquisition from an identical adaptive predictor.

| Candidate | Falsifiability | Prior-art distance | Mac feasibility | Interpretability | Decision |
| --- | --- | --- | --- | --- | --- |
| 1: diagnostic sensing | high | low: direct controlled-sensing overlap | high | high | baseline/context, no novelty |
| 2: predictive vs parameter information | high | low/uncertain: EPIG and robust BOED exist | high | high with matched filter | selected stress test |
| 3: representation revision | medium until identifying assumptions fixed | low/uncertain | medium | low initially | defer |

These are qualitative judgments, not measured scores. Candidate 2 yields a clean implementation target without promising research novelty: a small finite-state simulation, known acquisition rules, shared predictor, held-out schedules and explicit falsifiers. Its limited scientific value is to expose where our intended learning loop fails before investing in representations or grand architectures.

Nearest competitors and counterarguments are documented in [candidate gaps](candidate_gaps.md), [focused prior art](focused_prior_art.md), and [critic report](critique.md). The 2026 R-IDeA method remains a methods-level comparison requirement before any future robust-design contribution. A successful toy result would not establish superiority over that method or the controlled-detection literature.

The [selected protocol](../experiments/selected_experiment.md) fixes environments, observations, baselines, metrics, thresholds, tuning split, uncertainty and resource caps. No experiment has been run for this question. Tomorrow: review this choice with the user, implement the exact small comparison, get independent code review, then run bounded tests and evaluation. A failure of the hypothesis is grounds to revise the research direction, not to search indefinitely for favorable seeds.
