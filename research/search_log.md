# Initial literature search log

Date: 2026-09-25. Research worker: Codex. Scope: public read-only browsing; writes limited to this file and `research/prior_art.md`. Repository root: `/Users/marmon/Documents/Codex/2026-09-25/referenced-chatgpt-conversation-this-is-an/outputs/artificial-scientist`.

Purpose: challenge the novelty of a small learner combining calibrated prediction, active experimentation, explicit hypotheses, causal/world models, and adaptation to hidden changes. Approximate target span 2016–2026 through the date above, with older foundations. This bounded first pass does not satisfy an exhaustive novelty search.

## Queries actually issued

All queries were issued on the date above. Search snippets were used as discovery leads; claims in the map rely on primary records/papers opened or primary-source search results.

| Query | Useful result / disposition |
| --- | --- |
| `site.arxiv.org active causal structure learning interventions 2016 2024` | Choo, Gouleakis, Bhattacharyya, *Active causal structure learning with advice* (2023), [primary record](https://arxiv.org/abs/2305.19588). Screened as a lead; not in the 12 core anchors. |
| `site.arxiv.org continual world models nonstationary environment dynamics change causal` | 2026 changepoint/world-model lead found; quarantined below. |
| `site.arxiv.org calibration modern neural networks 2017` | Guo et al. 2017; primary record opened, included as P04. |
| `site.arxiv.org Bayesian experimental design deep adaptive design 2021` | Foster et al. 2021; primary proceedings and full paper opened, P06. |
| `site.arxiv.org "Towards Causal Representation Learning"` | Schölkopf et al. 2021, P08; 2025 observable-sources extension noted but not audited. |
| `site.proceedings.mlr.press "Deep Adaptive Design"` | Official ICML/PMLR paper and PDF, P06. |
| `site.arxiv.org "Adaptive Conformal Inference Under Distribution Shift"` | Gibbs & Candès 2021, P07; 2026 leads noted below. |
| `site.arxiv.org "Active Learning for Optimal Intervention Design in Causal Models"` | Zhang et al. 2022 record and full text, P09. |
| `site.arxiv.org "Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture"` | Assran et al. 2023 primary record opened, P10. |
| `site.arxiv.org "The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery"` | Lu et al. 2024 primary record; official repository opened, P11. |
| `site.arxiv.org nonstationary causal discovery mechanism changes 2025 2026` | SpaceTime 2025 primary record and PDF, P12. |

## Direct primary-source checks

Known-title leads were opened directly for [SINDy](https://arxiv.org/abs/1509.03580), [AI Feynman](https://arxiv.org/abs/1905.11481), [World Models](https://arxiv.org/abs/1803.10122), and [Bayesian Online Changepoint Detection](https://arxiv.org/abs/0710.3742). Titles/authors were checked from the returned primary pages, not assumed from memory.

Detailed passages inspected: BOCPD sections 1–2 and Algorithm 1; DAD evaluation/baselines and code pointer; ACI coverage guarantees and fixed-parameter comparison; causal intervention paper known-DAG assumption, acquisition comparisons, and discussion of misspecification. These are targeted reads, not complete proof audits.

Official repositories inspected: [DAD](https://github.com/ae-foster/dad), which labels MIT licensing; [AI Scientist](https://github.com/SakanaAI/AI-Scientist), which describes a project-specific source-code license. No code downloaded or installed. Code licenses for other anchors remain unverified.

## Exclusions, failed access and uncertain recent leads

- Two memory-based arXiv-ID guesses resolved to unrelated works (`2002.05084` and `2301.00808`). Both were rejected immediately and are not citations in the map. This is why title verification matters.
- SpaceTime HTML retrieval at `https://arxiv.org/html/2501.10235v1` returned an internal error. Its abstract and [PDF](https://arxiv.org/pdf/2501.10235) were accessible. Only abstract-level claims are included; a complete methods comparison remains pending.
- [Changepoint-Aware World Models: Detecting Dynamics Shifts and Recovering by Forgetting Stale Replay in Model-Based RL](https://arxiv.org/abs/2609.18950), Everest Yang: the returned primary record identifies a September 2026-style arXiv ID but says submitted 15 July 2026. The HTML/abstract describes detection and replay forgetting. **Quarantined pending independent bibliographic verification** because the metadata conflict was not resolved. Its apparent relevance argues against making broad novelty claims; no numerical result is used.
- [Score-Based Diffusion Priors for Adaptive Conformal Inference under Distribution Shift](https://proceedings.mlr.press/v337/jiang26a.html), Xiangyu Jiang (UAI 2026): primary landing-page result retrieved; full paper/proofs not audited. Follow-up lead only, not evidence supporting any guarantee in this repo.
- A publisher result for *Online conformal inference with retrospective adjustment for faster adaptation to distribution shift* showed December 2026 issue metadata. Excluded from the map because availability by the run date was not independently established.
- Third-party aggregators, Reddit, Wikipedia, unofficial code replicas, and search-engine publication-age labels were not used to substantiate research claims.

## Next queries before a novelty decision

Search primary sources for active quickest change detection; controlled sensing and change-point detection; Bayesian adaptive design with model misspecification; dual control with switching dynamics; nonstationary bandits with monitoring actions; online probability calibration under adaptive sampling; continual causal representation learning; and causal discovery with changing mechanisms. Trace citations forward from P01, P06, P07, P09, and P12. Check 2025–2026 proceedings directly and distinguish public preprints from accepted papers.

Selection bias: this first pass favored accessible primary sources and canonical works and only closely compared four papers. Negative search outcomes are not evidence that a problem is unsolved. No experiment, implementation, or literature completeness claim follows from this log.
