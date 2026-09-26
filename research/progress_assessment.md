# Are we improving, or going in circles?

**We built a functioning investigator. We have not yet shown that its recent changes make it a better investigator on the harder task.** The last two iterations improved proposal mechanics; treating those intermediate gains as progress toward understanding was too optimistic. This is partly a roadmap problem, not just an algorithm problem.

## What improved—and what did not

The connected learner now observes, constructs executable explanations, predicts before acting, chooses experiments and revises models. That is real integration progress beyond the retired disconnected exercises. Its simple-world predictions improved. But it still uses a small supplied formula language; it does not invent new concepts, expand that language or learn across these separate runs.

Saved evaluator mean squared 2D position error, lower is better:

| Active learner version | Simple world | Harder world |
|---|---:|---:|
| Original enumeration | 0.001237 | 0.026477 |
| Guided proposals | 0.000288 | 0.053171 |
| Conditioned guided proposals | 0.000263 | 0.053795 |

Original random exploration scores 0.000262 on the simple world; original coverage scores 0.021288 on the harder world. Thus the newer active versions have not demonstrated an advantage over these simple controls. These are reused single-seed comparisons, not evidence of general superiority or regression. Tests establish implementation correctness, not intelligence. [Numbers and trace fingerprints](../results/progress_audit/diagnostics.json).

## Why finding the explanation earlier did not solve it

**It was not ignored.** In the repaired harder-world trace, `v+u` stays in the pool from its addition at step 11 through the end. Its planning weight reaches 0.839 by step 15. Removing it changes 21 of 39 subsequent saved decisions under the fixed-weight diagnostic. This shows influence, not beneficial experiment choice or a causal effect on final performance.

**Earlier birth does not mean more training data.** Every live formula is refitted on all eligible historical observations. Refitting `v+u` from each saved full history reproduces both final coefficient pairs exactly: old `(0.769821, 0.295070)`, repaired `(0.769724, 0.293692)`. A late-created formula can catch up immediately on the same history. Timing can help by changing experiments or validation history, but not simply by accumulating extra coefficient updates.

**Different experiments did not yield a better final approximation.** The repaired run supplies 33 eligible training transitions versus 36 before; it takes 13 waits after step 11 versus 10. Waits and their immediate successors can be excluded from coefficient fitting because velocity is not observed instantaneously. This reveals a mismatch between available tools and usable training evidence, but does not establish the cause of the worse score. The planner maximizes heuristic disagreement; it does not directly optimize improvement of the final evaluator's multi-step predictions.

**The model language has a verified ceiling.** It applies the same scalar formula independently to x and y. It cannot express different coefficients by direction or one direction affecting the other. The developer-known challenge violates both assumptions. Shortlist repairs cannot remove this structural mismatch. That is a proven capacity limit, not proof of how much of the current error it causes. About 98% of the repaired evaluator error is in x; this is consistent with the limitation, not a causal diagnosis. Hidden equations were inspected for this report, never supplied to the learner.

## Why the work feels circular, and the decision

We drifted from improving experiment choice into making hypothesis selection look more scientific. Earlier proposals and fewer fits were easier to measure than useful understanding. Repeatedly inspecting the same small task also makes further tuning less convincing.

**Stop proposal-ranking tweaks.** The next capability target is one complete evidence-driven revision: the agent detects an inadequacy, chooses an experiment that distinguishes explanations, revises a model assumption, and improves predictions on unused interventions—or explicitly admits it cannot explain the evidence.

This requires a reviewed design before implementation. General revision operations must be declared in advance, with unchanged/random/coverage exploration using the same learner and a straightforward regression reference. External evaluation must stay outside the learner's adoption decisions. A control where revision is unnecessary and a case the toolbox cannot explain guard against automatic expansion. Do not insert the challenge's known answer or launch a larger sweep by default. No novelty claim follows from this milestone.

## Review and limits

A separate Codex critic independently reached the capacity/proxy diagnosis. Claude Opus 5.5 reviewed the supplied facts and proposed milestone, warning that targeting the exact broken assumption risks scripting the answer. We accept that warning and its demand for matched exploration controls. We do not adopt its proposed four-world/five-seed expansion yet. Its statement that prior comparisons lacked predeclared criteria is too broad: designs and bounded comparisons were written before runs. The missing evidence is a successful capability-level result, not an absence of all experimental discipline. Single-seed results are informative about these traces, though insufficient for general claims.

[Claude's verbatim critique](claude_progress_review.md) · [Provenance](progress_claude_provenance.json). This assessment used existing traces and source inspection only: no new learner, simulator run or claimed test pass. [Independent review record](review_log.md).
