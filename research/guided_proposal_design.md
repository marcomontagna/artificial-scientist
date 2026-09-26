# Observation-guided proposals: a critical implementation decision

The user’s idea is coherent if observations actually narrow the search before fitting. “Like humans” is not an operational criterion. This prototype implements selective local search over supplied mathematical features, not unrestricted theory invention, human cognition or a new learning principle. The old enumerating proposer remains the default/control.

## Exact change, fixed before execution

`--proposal guided` records signed residuals **after outcomes**, using predictions frozen before those outcomes. A record includes action-step index, coordinate, public feature inputs, predicted/observed positions, incumbent structure ID and coefficient version. Only transitions eligible for the existing one-tick fitter enter this diagnostic pool. It resets when the pre-outcome incumbent structure changes; at most the latest 24 coordinate records of that episode enter a proposal. Refitted coefficients can still differ within the episode; the data describe an updating predictor, not a fixed physical hypothesis.

Screen the 20 single-term features already in the v1 grammar, separately by coordinate, using signed Pearson correlation with residuals. Constant 1 uses mean residual/RMS residual. Fewer than 3 records for a coordinate or near-zero normalization gives score 0. Rank by max absolute coordinate association, threshold 0.25, ties by existing grammar order. This is a heuristic screen with no significance or causal interpretation. Features involving position/estimated velocity share sensor noise with the residual; the trace flags this vulnerability.

Use ranked features to generate one-term additions/replacements of the incumbent (still at most 2 terms and 12 nodes). Canonical term order matches v1. Freeze at most 7 unique unseen local edits before fitting; record rejected size/excluded edits. Add at most 1 unguided escape, cycling through eligible grammar structures without evaluating their fit. Total at most 8 candidate fits/update, including the escape. The escape cannot guarantee discovery of a missing relationship. Score/refit candidates exactly as v1 and insert at most 2 into the committee. A seen structure remains excluded to preserve v1’s anti-churn rule; exhaustion is explicitly logged, not silently treated as understanding.

No world, evaluator, action menu, training fit, search-trigger schedule, model-ranking rule or active-planner formula changes. Existing warmup and coverage still apply. New models start with no future evidence; association and in-sample fit do not validate them.

## Evidence → proposal → experiment

The revision records exact support observations, all feature associations, the fixed shortlist, fit counts and proposal origin. The next plan links live proposed models to their origin and shows their separation from the parent, when the parent remains present. It also recomputes the current decision with that one model removed, renormalizing frozen committee weights. This is a one-decision counterfactual, not a retrained control or proof of a uniquely causal explanation. Log unchanged choices and missing parents. No invented narration or human intervention chooses actions.

Count proposal fits, all diagnostic feature-value evaluations, retained-model refits, tool costs and process CPU time. Fewer proposal fits are expected by construction; the original tiny search is already cheap. Do not claim a practical improvement from that count alone.

## Bounded check

Freeze source before six runs: enumeration versus guided, active policy only, existing development/challenge/noise worlds, existing seed 260926, 80 training units plus the unchanged 44 evaluation units/run. These worlds, seed and evaluator sequences have already been inspected. This is a developmental comparison, not independent confirmation or generalization evidence. Preserve all old runs; no tuning or extra sampling after outcomes.

Report formula, fresh-intervention prediction errors, proposal/search costs, actual one-decision action changes and paired subsequent errors where parent/proposal are both observed. Call those comparisons lower/higher paired error, never confirmed physical laws. Keep testable failures: pure interaction can be found by the full feature screen, but rules outside the grammar cannot; noisy correlations can propose spurious mechanisms. Paired errors are conditional on the learner’s chosen actions, not an unbiased all-intervention comparison. Screening all terms can expose some pure interactions but does not guarantee association under cancellation or limited exploration. No new disconnected statistical study.

## Independent criticism and decisions

[Claude’s verbatim critique](claude_guided_review.md), [provenance](guided_claude_provenance.json). A distinct Codex critic independently approved the narrow question while rejecting a human-cognition claim.

Accepted Claude’s full 20 feature screen (the earlier main-effect-first proposal would miss pure interactions), explicit incumbent-episode separation, one-decision influence diagnostic, budget/exhaustion logs and cost caveats. Kept the original committee planner so the implemented change is genuinely proposal selection.

Did not add shadow full enumeration at each guided update: it would add the computation the guided branch avoids and is unnecessary to establish this mechanism. The separate unchanged enumeration control supplies the practical comparison. Did not enforce a rule that noise must never cause position/velocity proposals: a denoising predictor may improve prediction, and a valid adaptive-selection null is not supplied by one noisy home estimate. We flag shared-noise associations and report outcomes without assigning causal meaning. Did not change seen-structure expiry or grammar: those are remaining limitations rather than extra changes hidden in this comparison.
