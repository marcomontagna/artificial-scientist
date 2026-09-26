# Review log

The complete [historical review log](https://github.com/marcomontagna/artificial-scientist/blob/0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9/research/review_log.md) remains in Git history. Its test counts and approvals describe retired implementations, not the current scaffold.

## Direction reset — September 26, 2026

Author: Codex primary. Claude Opus 5.5 independently reviewed the direction and proposed cleanup; see its [verbatim review](claude_direction_reset.md), [provenance](direction_reset_claude_provenance.json) and [accepted/deferred decisions](reset_decisions.md). Claude supported the reset and identified the old novelty-before-building requirement as counterproductive. Its review is advice, not evidence of novelty.

Before removal, the distinct Codex independent_review worker verified all 188 manifest paths against their original committed bytes, confirmed the exact retained-file complement, and approved the scoped removal. Git history was not rewritten. The primary verified that all 181 ignored raw-run files retained their sizes and modification times across removal.

Final cleanup review by the distinct independent_review worker approved the exact staged removals, all archived hashes, all three Claude provenance hashes and verbatim report, package import and active relative Markdown links. It confirmed 181 raw files remain; size/mtime continuity was checked separately by the primary. The distinct research_critic approved the direction and proposed Notion summary, requesting explicit action/time inputs for model predictions and a distinction between noise and unexplained model error. Both clarifications were added to the laboratory design. The primary reviewed both reviewers’ findings. No active test suite or new experimental result is claimed.
