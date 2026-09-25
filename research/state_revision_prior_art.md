# Focused state-revision check — September 25, 2026

A distinct Codex research_critic screened these primary records/abstracts and limited indexed method descriptions. No method was reproduced; this is not exhaustive novelty clearance.

- [Bayesian variable order Markov models (2010)](https://proceedings.mlr.press/v9/dimitrakakis10a.html): directly overlaps learning which history length matters.
- [Adaptive Context Tree Weighting (2012)](https://arxiv.org/abs/1201.2056): discounting old observations for nonstationary sequence prediction is established.
- [Context Tree Switching (2012)](https://researchportalplus.anu.edu.au/en/publications/context-tree-switching-2/): expands the context-tree model class; the inspected stationary-source guarantees do not establish arbitrary hidden-change guarantees.
- [Skip Context Tree Switching (2014)](https://proceedings.mlr.press/v32/bellemare14.html): relevant sparse-context competitor when distant bits matter but intervening history does not. A dense long-history table alone is a weak efficiency comparison.
- [Skip RNN (2017/2018)](https://imatge-upc.github.io/skiprnn-2017-telecombcn/): adaptive recurrent update cost, not evidence of latent-dimension expansion.

Decision: proceed with the [v0 calibration protocol](../experiments/state_revision_v0.md) and known baselines only. No claim of a novel learner. Any future expansion candidate must count shadow models, replay and selection overhead; active dimension alone is not compute saved. Add sparse-context and recurrent competitors before substantive superiority claims. Older foundations are intentionally included despite the original 2016–2026 search focus.
