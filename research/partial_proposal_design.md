# Repair one diagnosed proposal failure

## Evidence before choosing the repair

The original suspicion—resetting evidence whenever the incumbent changes—was incomplete. The challenge trace has two distinct bottlenecks. At action 11, incumbent `u` already has eligible observations 7–11 and a substantial motion-feature association 0.743. The seven local candidate slots fill before `v` is reached. At actions 15/23/27/31/35, later incumbent changes and observation eligibility leave only 1/0/0/1/1 observations per coordinate; that is separate evidence starvation. Seen-structure exclusion did not block `v+u`, which had never been proposed.

Several features leading the action 11 shortlist are associated with the same input pattern. The incumbent’s own input has raw association 0.921 with its recorded errors: those errors still include components explained by an existing term, including coefficient error. This does not prove that every remaining correlation is a missing physical mechanism.

Claude challenged an initial shortlist-grouping draft and proposed conditioning the screen on existing terms instead. The draft was not committed or run in a world. We chose the more direct scoring repair. Evidence retention, local edit order and fit budget remain unchanged.

## Exact opt-in change

Add `--proposal guided-partial`; preserve `guided` and default `enumerate`.

For each coordinate and nonconstant feature, center the feature, recorded residual and incumbent-feature columns. Build an orthonormal basis of the incumbent columns with two-pass modified Gram–Schmidt, discarding columns with remaining norm at most 1e-10. Project both feature and residual away from that span, then compute the existing normalized association. Threshold 0.25, sample minimum 3, term ordering, two-term/node limits, seven local fits plus one rotating escape and subsequent fitting are unchanged.

In symbols, with centering matrix C and orthonormal incumbent design Q:

`z_perp = (I - QQᵀ) C z`, `r_perp = (I - QQᵀ) C r`.

The screen correlates these vectors. Existing-term signal has no remaining variance and receives zero score. This is a linear conditioning heuristic using supplied features, not causal identification or a new model language. For the constant 1 candidate, use the existing mean/RMS residual heuristic after projecting residuals away from the **uncentered** incumbent design; if 1 is already present, score 0. This exception preserves an opportunity to propose a missing intercept.

The screen logs raw and conditioned scores, conditioning terms, diagnostic feature evaluations, additional base-column evaluations and projection calls. Building the basis is additional computation even though at most 8 candidate coefficient fits remain. Cache each coordinate’s centered/uncentered basis within the current proposal only. No coefficients, data or hidden information are obtained from the evaluator. Residuals still come from frozen pre-outcome predictions, and coefficient versions remain visible.

## Prefix diagnosis and fixed comparison

Before any new world run, replay only the saved challenge prefix through action 11. Reconstruct eligible rows, prior exclusions, incumbent and cursor using that prefix. The old mode must reproduce its original shortlist. The conditioned mode raises the motion score to 0.926, suppresses the incumbent input’s score to 0, and includes **and selects** `v+u`. This tests the proposed mechanism at that observed failure; it is not independent confirmation or evidence of general benefit. The original trace and complete diagnosis are retained with hashes.

Freeze source before six bounded active-policy runs: old `guided` versus `guided-partial`, development/challenge/noise, previously inspected seed 260926, same 80 training and 44 evaluation tool units/run. Keep formulas, worlds, fitter, planner, resets, shortlist allocation and all other caps unchanged. Report proposal timing, fresh-intervention errors, model/search costs and failures. No tuning, expanded world suite or additional sampling after outcomes. The existing evaluator is reused developmental evidence, not untouched validation.

## Criticism and limits

[Claude’s critique](claude_partial_review.md), [provenance](partial_claude_provenance.json). A distinct Codex trace critic independently identified both early crowding and later starvation. Conditioning targets the former; it cannot be claimed to solve the latter or the absent cross-axis representation.

Do not accept the claim that a surviving raw association proves stale coefficients are its only cause. Model misspecification, sensor noise, adaptive actions and few observations remain. Conditioning on a supplied term can suppress a useful correlated new feature; small/collinear samples can leave almost no residual direction. Tests cover collinearity, constants, invariance to additional incumbent-component error, chronological evidence and work accounting.

Claude suggested shuffled-residual diagnostics. We do not add them as a separate noise study: exact synthetic invariance/degeneracy tests and the existing noise-world comparison are sufficient for this bounded engineering change. No significance, mechanism-identification or novel-method claim follows. Publication requires independent source and recorded-result review.
