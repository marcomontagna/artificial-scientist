# Review log

The complete [historical review log](https://github.com/marcomontagna/artificial-scientist/blob/0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9/research/review_log.md) remains in Git history. Its test counts and approvals describe retired implementations, not the current scaffold.

## Direction reset — September 26, 2026

Author: Codex primary. Claude Opus 5.5 independently reviewed the direction and proposed cleanup; see its [verbatim review](claude_direction_reset.md), [provenance](direction_reset_claude_provenance.json) and [accepted/deferred decisions](reset_decisions.md). Claude supported the reset and identified the old novelty-before-building requirement as counterproductive. Its review is advice, not evidence of novelty.

Before removal, the distinct Codex independent_review worker verified all 188 manifest paths against their original committed bytes, confirmed the exact retained-file complement, and approved the scoped removal. Git history was not rewritten. The primary verified that all 181 ignored raw-run files retained their sizes and modification times across removal.

Final cleanup review by the distinct independent_review worker approved the exact staged removals, all archived hashes, all three Claude provenance hashes and verbatim report, package import and active relative Markdown links. It confirmed 181 raw files remain; size/mtime continuity was checked separately by the primary. The distinct research_critic approved the direction and proposed Notion summary, requesting explicit action/time inputs for model predictions and a distinction between noise and unexplained model error. Both clarifications were added to the laboratory design. The primary reviewed both reviewers’ findings. No active test suite or new experimental result is claimed.

## First connected tool laboratory — September 26, 2026

The distinct research_critic authored and committed the public API, hidden development/challenge/noise worlds and eight boundary tests in `e6920e7`, before learner execution. Codex primary reviewed those sources and tests: persistent state, tool timing, per-tick noise draws, budget enforcement and atomic rejection are consistent. This is source separation, not formal developer blinding.

Codex primary authored the bounded model interpreter/search, investigator, harness, implementation contract and learner tests. The distinct independent_review worker caught lost coefficient revisions on timeout, incomplete byte accounting, missing post-plan/final CPU checks and an unenforced two-term limit. Those were fixed and re-reviewed. Root reviewed the worker’s findings. Claude Opus 5.5 independently reviewed the plan and then code via existing subscription access; both verbatim reviews and hashes are retained. Its weighting, failure-trigger, lag timing, fresh-evaluation and reference-baseline objections led to concrete changes; disagreements and representation limits are recorded in the implementation contract.

The distinct prior_art worker authored the self-contained replay exporter and three safety tests. Root reviewed source and tests, including safe script embedding, DOM text rendering and trace fidelity; requested clearer labels for structural prequential scores and noise assumptions were applied. Browser/result checks follow the frozen demonstration. Twenty focused tests passed before that demonstration; no test count from retired studies is included.
