# Adversarial research critique

Date: 2026-09-25. Author: independent Codex critic (`research_critic`), **not Claude**. Research-only; no algorithms or experiments executed. Director review required before finalization.

## Verdict

The broad diagnostic-action proposal is occupied prior art. Choosing informative actions to discover otherwise hidden distribution changes is already controlled sensing / bandit quickest change detection. Adding explicit hypotheses, Bayesian updates, or uncertainty does not establish a new learning paradigm. The strongest next step is a small replication-and-evaluation study of where adaptive sensing helps **prediction**, with no novelty claim. A result can be useful even if it establishes only a reproducible boundary condition.

## Six primary-source checks

These are focused additions to `prior_art.md`, not a systematic review. Claims below stay within the inspected records; theoretical proofs and published results were not reproduced. No third-party code copied; code licenses not audited.

| ID / primary source | Verified overlap and boundary | Reading depth |
| --- | --- | --- |
| C01 — Gopalan, Lakshminarayanan, Saligrama, **Bandit Quickest Changepoint Detection**, NeurIPS 2021. [Proceedings](https://proceedings.neurips.cc/paper/2021/hash/f3a4ff4839c56a5f460c88cce3666a2b-Abstract.html) | Sequentially chooses sensors under restricted observations; balances exploring sensors and querying informative ones, with detection-delay bounds. Directly preempts “actively look where a change might be.” Its main objective is detection, not continuing probability forecasts. | Proceedings abstract. |
| C02 — Veeravalli, Fellouris, Moustakides, **Quickest Change Detection with Controlled Sensing**, preprint 2023 / journal 2024. [Paper](https://arxiv.org/html/2310.17223v1) | Finite actions and post-change parameters; windowed estimation, KL-based action selection, exploration, and CuSum detection. Unknown change time/parameter is already covered. First-order asymptotic optimality under its criterion is not a guarantee for our finite prediction horizon. | Abstract/introduction and formulation overview. |
| C03 — Huang, Gerogiannis, Bose, Veeravalli, **Learning Where to Look: UCB-Driven Controlled Sensing for Quickest Change Detection**, March 2026 preprint. [Paper](https://arxiv.org/html/2603.28563v1) | Samples one channel per step; affected subset unknown. Compares adaptive informative sensing to cycling exploration. Main model knows pre/post densities; a later extension addresses unknown distributions with a mean shift. Thus “unknown distributions” alone does not rescue novelty. | Abstract, introduction, problem formulation, UCB-CuSum section through action-selection rule; extension only abstract-level. |
| C04 — Komiyama, Fouché, Honda, **Finite-time Analysis of Globally Nonstationary Multi-Armed Bandits**, JMLR 2024. [Paper record](https://www.jmlr.org/papers/v25/21-0916.html) | Adaptive resets/windowing can remove the need for forced exploration under coordinated global changes. Localized versus global change observability is therefore an essential experimental distinction. Reward regret differs from forecast log loss. | Publisher abstract. |
| C05 — Gerogiannis, Huang, Bose, Veeravalli, **Detection Is All You Need: A Feasible Optimal Prior-Free Black-Box Approach For Piecewise Stationary Bandits**, January 2025 v1. [Versioned record](https://arxiv.org/abs/2501.19401v1) | Modular detection-augmented bandit learning already wraps stationary learners with a detector. This challenges “reusable learner plus detector” as novelty. The latest record was retitled **DAL: A Practical Prior-Free Black-Box Framework for Piecewise Stationary Bandits**; v1 claims are explicitly versioned here. | Versioned abstract; latest title checked, latest method not audited. |
| C06 — Klenske, Hennig, **Dual Control for Approximate Bayesian Reinforcement Learning**, JMLR 2016. [Paper record](https://jmlr.org/papers/v17/15-162.html) | Planning actions for their effect on future beliefs and control is established dual control. Simulated uncertain dynamics and approximate Bayesian treatment overlap with the proposed scientist loop. This is not a direct benchmark for a memoryless sensor task. | Publisher abstract and indexed model passages. |

## Strongest narrow question

**At a fixed one-observation-per-step budget, does adaptive diagnostic sensing reduce post-change prediction error relative to matched uniform/round-robin sensing, using the same change-aware predictor, and does any gain survive wrong change assumptions and stationary controls?**

Use a handful of Bernoulli channels with localized shifts. Score all channels under a fixed evaluation distribution, before the chosen observation updates the learner. The evaluator may compute expected log loss from the true probabilities, but neither these probabilities nor evaluation outcomes enter the learner. This isolates acquisition from easy-action selection and avoids expensive simulation. Actions reveal channels; call them sensing actions, not identified causal interventions.

The null is that any advantage disappears against a matched active-change baseline or under misspecification, or is offset by stationary prediction cost. Choose a practical improvement threshold and stationary-cost ceiling before held-out runs. A failed threshold is a negative result, not permission to redefine the hypothesis.

This is an evaluation question, **not a verified gap**: the inspected papers emphasize detection delay or reward regret, but that observation does not prove no one has studied prediction loss. The latest 2026 sensing work is particularly close and deserves deeper review before claiming a contribution.

## Design traps and required corrections

1. **Weak baseline:** beating cumulative counts mainly shows forgetting. Cross acquisition policies with the same adaptive predictor; include random/round-robin, fixed-window and change-aware controls. A paper-inspired implementation must be labelled an adaptation unless faithfully reproduced.
2. **Tautological sensing gain:** a change invisible in the only sampled channel cannot be inferred without additional assumptions. Include localized, global and no-change settings; do not present this information limitation as a discovery.
3. **Objective mismatch:** maximal change-detection KL need not minimize future all-channel prediction loss. Record this as a testable tradeoff, not an expected theorem. A detector alone does not supply probabilities: explicitly define the associated predictor and reset rule.
4. **Unequal information:** comparing a known-density method to an unknown-density learner confounds acquisition with prior knowledge. Give shared assumptions, or separate clearly labelled information regimes.
5. **Budget leakage:** diagnostic samples replace ordinary samples; evaluation must never supply free training labels. Report every observation and sensing cost, including warm-up. Keep wall-clock and observation-count windows distinct for rarely sampled channels.
6. **Policy-dependent scoring:** selected-action accuracy rewards choosing easy channels. Use a fixed all-channel evaluation distribution, independent of learner actions; retain selected-action loss only as a secondary operational metric.
7. **Change-time leakage:** changes and affected channels are evaluator-only. Do not trigger resets, tuning, or evaluation-conditioned learning from hidden metadata. Stationary false alarms and recovery failures must be retained.
8. **Misspecification theatre:** holding out a new seed is not holding out a new law. Freeze a wrong-hazard condition and a changed probability family or affected-subset condition before tests, and distinguish which assumptions are wrong.
9. **Overstated evidence:** 30 or 50 seeds support paired empirical intervals, not universal calibration or asymptotic-optimality claims. Keep calibration descriptive unless adequate sample counts and a specific definition are supplied. Multiple exploratory slices do not create independent confirmatory wins.
10. **Premature complexity:** learned latents, symbolic equation discovery and a new architecture add no necessary capability to this sensing test. Defer them until an environment requires them.

## Search record and limits

Queries on 2026-09-25: `active quickest change detection controlled sensing bandit quickest change detection primary paper`; `nonstationary bandits change detection forced exploration primary paper 2024 2025`; `site.arxiv.org dual control approximate dual control Bayesian reinforcement learning 2016 Klenske Hennig`; `site.arxiv.org "Detection Is All You Need"`.

Six retained primary works above; follow-up opened original records and C02/C03 HTML. An attempted nonexistent C02 v2 HTML failed; v1 succeeded. Search-index publication ages were inconsistent with records, so actual preprint/publisher dates govern. Coverage remains incomplete for continual causal discovery, strongly adaptive prediction, calibration, and the full 2026 frontier. No novelty clearance and no empirical performance claim is granted.

## Independent review of the director's selected package

Reviewed paths: `research/focused_prior_art.md`, `research/candidate_gaps.md`, `research/decision.md`, `experiments/selected_experiment.md`. Reviewer: distinct Codex agent `research_critic`, 2026-09-25. The director selected candidate 2, an EPIG/EIG replication and stress test; the earlier sensing recommendation above remains adversarial context, not the final decision.

Independently opened the six primary records in the focused map (EPIG; active-learning bias; misspecification-aware design metrics; R-IDeA; COREP; Locatello et al.). Titles, dates, authors and limited abstract-supported overlap claims agree. The review does not certify the director's deeper reading or inaccessible PDF; their depth limitations are appropriately disclosed.

The acquisition/filter design is coherent: EPIG uses separate conditionally independent binary draws, including when query and target actions coincide; global filter propagation occurs every tick; all acquisition methods share inference, hyperparameters and information. Fixed target-distribution scoring and seed-cluster pairing avoid two major confounders. The conjunctive primary rule does not select the winning comparator after evaluation. No new algorithmic claim or empirical result appears in the package.

Requested preregistration clarifications before final acceptance:

1. Specify the tuning objective as full-episode mean expected log loss using the primary q, with equal development-condition weights; specify the window-size tie rule. Otherwise reasonable implementations can select different hyperparameters.
2. State that “matched” means likelihood-matched only. One scheduled switch or no switch differs from the filter's constant-hazard transition model; do not imply a fully matched generative process.
3. Require recovery windows to lie entirely after the change, making the first eligible 20-tick window end at change tick +19.

Verdict pending those editorial fixes: **acceptable research design, no blocking mathematical issue identified**. Remaining limits: arbitrary toy table and target weights, no power guarantee for the chosen threshold, likelihood misspecification may dominate acquisition, and modern robust-design competitors are not implemented. This supports tomorrow's bounded test, not novelty or superiority beyond the specified toy comparison. No code or experiments reviewed in this pass.

### Final verification

The three requested clarifications are present in the final protocol. Final verdict: **approved as a bounded replication/stress-test research plan**, subject to the stated limits and independent implementation review tomorrow. Also reviewed the research-completion section of `RESULTS.md`, rewritten `NEXT_STEPS.md`, historical coordination notes and `research/review_log.md`, and the director's proposed Notion summary substance. They accurately distinguish research completed from implementation not begun and do not imply Claude participation or new empirical results. Earlier smoke-validation and scheduling claims are inherited records, not rerun or independently rechecked in this review. The director has separately read and accepted this critic report.
