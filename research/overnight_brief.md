# Overnight research brief

## Morning outcome
Identify the strongest falsifiable question that is not obviously a reproduction of existing work. Document the closest prior art, compare three candidate gaps with counterarguments, choose one minimal experiment if a gap survives, implement only safe reusable infrastructure and baselines, and write RESULTS.md and NEXT_STEPS.md. No requirement to discover novelty tonight.

## Stage 1: prior art before architecture (roughly 90 minutes)
Search primary papers and official repositories from approximately 2016 through the actual 2026 run date; include older foundations. Start with symbolic system identification/SINDy and AI Feynman; Bayesian experimental design and active learning; active causal discovery and causal representation learning; world models and JEPA; predictive coding and active inference; intrinsic motivation and information gain; program synthesis and minimum description length; automated scientists; nonstationary online learning and change-point detection. These are search leads, not a verified bibliography.

Maintain research/search_log.md (query, date, source, coverage and inaccessible items) and research/prior_art.md. For each close work: exact title/authors/year, primary URL, verified claim, setting, learner information, intervention budget, baseline, code/license if available, overlap, and precise unresolved difference. Aim for 8–12 useful sources with 3–5 read closely; prioritize relevance over quotas. Do not cite future work or turn abstracts into stronger claims than they support.

## Stage 2: three candidate gaps and adversarial review (roughly 60 minutes)
Create research/candidate_gaps.md with exactly three candidate questions. For each provide hypothesis, null, nearest prior art, what is already solved, possible gap, why it matters, strongest counterargument, falsifier, minimal environment, baselines, confounders, and laptop cost. Label unverified novelty explicitly. Candidates may concern calibration under hidden law changes, intervention choice under a budget, or representation revision, but do not assume these are new.

Claude writes research/critique.md, checking independent sources where possible. Hermes scores falsifiability, prior-art distance, feasibility, and interpretability in research/decision.md. Choose one only if its evidence supports investigation. If all are reproductions, say so; select a clearly labeled replication/control to validate the harness rather than inventing novelty.

## Stage 3: preregister one small experiment (roughly 30 minutes)
Write experiments/selected_experiment.md before evaluating the candidate. Specify observation/action interface; hidden variables available only to evaluator; stationary and changing-law controls; held-out law families/change schedules; hypothesis and null; primary metric and practical effect threshold; intervention/observation/compute budgets; train/dev/test seeds; baseline hyperparameter selection; ablations; failure conditions; resource cap; exact commands. Include random/passive, simple Bayesian/online, fixed-window or forgetting, and an appropriate matched adaptive baseline where relevant. An oracle is a labeled reference ceiling, never an ordinary competitor.

Measure proper scoring rules (log loss, Brier), reliability/calibration with adequate bin counts, sample efficiency, intervention cost, and post-change recovery using an explicitly defined criterion. Distinguish epistemic uncertainty from irreducible noise. Report stationary performance costs as well as adaptation. Use paired seed-level comparisons and uncertainty when feasible; otherwise call results exploratory. Do not add learned latents unless needed to answer the selected question.

## Stage 4: implement and run (roughly 90 minutes, <=60 minutes aggregate experiments)
Engineer only interfaces, seeding, configs, logs, baselines, metrics, and tests useful across candidates. Existing smoke code is deliberately a known toy, not the selected research claim. Run tests first, then tiny checks, then a bounded multiseed run if feasible. No large sweeps, training foundation models, or replacing the whole scaffold. Record failed runs and every protocol deviation.

## Stage 5: synthesize (last 30 minutes; finish within 6 hours)
RESULTS.md: question; prior-art assessment; chosen comparison; exact commands/configs/revision; environment; completed and blocked tasks; tests; seed-level results/artifact paths; uncertainty; failures; critic objections; evidence-supported conclusion and limits. NEXT_STEPS.md: ranked next experiments, strongest remaining objection, expected information gained, estimated local cost, and go/no-go decision. Link all reports from README if helpful. Report absence of evidence honestly. Stop at the deadline, even with partial results.

## Mandatory independent review

The user requires a different agent to review every newly written or materially changed code file, research note, prompt, report, or other artifact before it is finalized. Record reviewer identity, reviewed paths, findings, fixes, and remaining limitations in research/review_log.md. A distinct Codex agent may review if Claude is unavailable; label it honestly and do not imply cross-model review. Authors must not certify their own work. If no separate reviewer is available, keep affected artifacts explicitly marked draft/unreviewed and report the blocker. Review subsequent material fixes as well. Reviewer findings themselves are reviewed by the receiving director; avoid an infinite review chain.

## Zero additional spending and bounded effort

The user explicitly prohibits purchases, subscriptions, paid APIs, cloud jobs, new paid services, and any additional charges. Use only already available access within existing limits; never buy credits or enable paid fallback. If billing status is unclear, do not launch the external service. Conserve tokens: one focused research pass and one independent review, no open-ended agent loops or redundant searches. Increase reasoning only for a concrete difficult decision, not routine work.
