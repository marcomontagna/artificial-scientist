# Equation discovery: focused prior-art check

Research date: 2026-09-26. Author: Codex research worker. Status: reviewed by Codex coordinator. This is a bounded primary-source check, not an exhaustive novelty assessment. No novelty has been established.

## Closest overlaps

- **SINDy — Brunton, Proctor and Kutz (2016):** sparse regression identifies governing equations using a supplied candidate-function library. This directly overlaps learning a compact formula from observations. Variables, available terms and useful measurements remain assumptions. [Primary paper](https://doi.org/10.1073/pnas.1517384113).
- **AI Feynman — Udrescu and Tegmark (2020):** combines neural fitting and physics-inspired decomposition for symbolic regression. Its successor explicitly considers expression complexity/error tradeoffs. Formula discovery alone is therefore not a contribution. [AI Feynman](https://arxiv.org/abs/1905.11481), [AI Feynman 2.0](https://arxiv.org/abs/2006.10782).
- **Active symbolic regression:** Haut, Banzhaf and Punch (2022) select additional observations using ensemble prediction uncertainty; Medina and White (2023 preprint, revised 2024) use a Pareto-frontier equation committee and physical constraints. Choosing inputs that distinguish equations is already an explicit research direction. [StackGP](https://arxiv.org/abs/2202.04708), [physical constraints](https://arxiv.org/abs/2305.10379).
- **Misspecification and evaluation:** Sugiyama (2006) studies active regression with approximately specified models. Matsubara, Chiba, Igarashi and Ushiku (2022) examine realistic sampling domains, irrelevant variables and equation-recovery evaluation. Neither supports treating low training error as discovery of a correct law. [Active regression](https://jmlr.org/papers/v7/sugiyama06a.html), [SRSD benchmarks](https://arxiv.org/abs/2206.10540).

## Three proposed stages, conditional on review

1. **Passive equation recovery:** bounded arithmetic-expression generation or sparse polynomial fitting, with continuous coefficients and simple baselines. Save formulas, complexity and independent prediction errors. Proceed only after implementation checks establish that the chosen bounded search can recover its declared in-class fixtures.
2. **Active equation discrimination:** freeze the search machinery; compare committee disagreement against random and space-filling inputs under equal observation/search budgets. A failed sample-efficiency comparison remains a result; do not tune acquisition after seeing it.
3. **Misspecification audit:** freeze the grammar and introduce omitted-operator or hidden-variable worlds. Use precommitted audit observations and separate interpolation/extrapolation evaluation. Allow “no adequate equation found.” Proceed after the preceding result receives critique, without requiring an active-learning win.

Each stage needs a fixed protocol, Claude review and independent implementation/result checks. The grammar supplies operators, variables, complexity limits and admissible expressions; fitting discovers only combinations and coefficients within that support. An added operator would be a declared design change, not autonomous concept invention.

## Search scope and limits

Three web calls searched active symbolic regression/experimental design, equation discovery, extrapolation and misspecification, plus direct primary-record checks for SINDy and AI Feynman. Most verification was abstract-level; no algorithms or proofs were reproduced. A foundational automated-probing lead hit a PMC access challenge. No complete forward-citation or 2025–2026 survey was performed. No files beyond this note or experiments were changed by this research task.
