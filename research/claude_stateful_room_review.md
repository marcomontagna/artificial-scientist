# Stateful room v0: protocol review

**Verdict: REVISE.** The protocol is careful about leakage, pairing, provenance and scope. But the primary screen is partly decided in advance by the world design, and the planned claim is broader than the design can support. Fix the blocking items before implementation.

I worked the deterministic cells out by hand. No samples were generated and nothing was executed.

## Blocking issues

**B1. The cycle baseline's result can be computed before the run.** Starting from state 0 with actions 0,1,2:
- **gate_on:** the path is 0→2→3→3→1→1→1→3→2→2→0→0→0. It has period 12 and visits all 12 (state, action) rows exactly once per period.
- **gate_off:** also period 12, also all 12 rows once per period.
- **directional:** 0→2→3→3→1→0→0. It has period 6 and visits only 6 rows. Rows (0,1), (1,0), (1,2), (2,0), (2,2) and (3,1) are never visited in any seed.

In deterministic worlds each row's loss falls as it is visited more, with diminishing returns. So round-robin coverage is essentially the best possible schedule, and cycle is near-optimal in gate_on and gate_off. lookahead2 can at best tie there and will probably lose.

In directional, each never-visited row keeps an excess loss of ln 5 ≈ 1.609 nats. That adds about 6×1.609/12 ≈ 0.80 nats per row-step to cycle's loss, or about 0.27 after averaging over the three worlds. That is far larger than the −0.01 threshold. So "lookahead2 beats cycle" is effectively guaranteed by one world, and it hides likely losses in the other two.

**Fix:** write these facts into the spec. Then either treat cycle as a sanity arm outside the screen, or replace it with a cycle whose action order and phase are randomised per seed. Add fixture tests for the three hand-computed trajectories above.

**B2. The pooled screen can pass while lookahead2 loses in 2 of 3 worlds.** Averaging the three worlds within a seed lets one world dominate, and this applies to the random and greedy comparisons too. **Fix:** make per-world paired differences part of the decision. For example, a pass also requires that no primary world shows lookahead2 worse than the comparator by more than 0.01. At minimum, state that a pooled pass with per-world losses is reported as "mixed".

**B3. The design cannot distinguish predictive information from simple visit counting.** In every deterministic cell, each row's counts have the form 0.5 + n·e_k, so the score g depends only on how many times the row was visited (n). That makes greedy "pick the least-visited action here" and lookahead2 "two-step count-based novelty". Any pass therefore says nothing about information-theoretic acquisition as such. Only random_room tests anything beyond counting, and it is a control that cannot rescue the screen. **Fix:** limit the claim explicitly to "shallow model-based coverage planning in these designed cells", and add a test that g depends only on n for single-category rows.

**B4. The go/no-go check covers time but not disk.** The smoke go rule checks projected time only. Yet the run writes 61,440+ records, each with 12×5 integer counts, scores, probabilities and metrics. My rough estimate is 40–60 MB of JSON against the 100 MB cap. Breaching the cap mid-run would leave an incomplete study that "cannot pass". **Fix:** project bytes from the smoke run and add `projected_bytes ≤ ~80 MB` to the go condition.

## Optional improvements

1. **Headroom reference.** Add a clearly labelled privileged oracle: an exhaustive planner that knows the true deterministic dynamics and minimises the primary endpoint. Without it, "lookahead2 beat X by 0.01" has no scale.
2. **Justify the −0.01 threshold.** For scale, one unvisited row contributes about 0.134 nats per row-step, so −0.01 over 96 steps is roughly one row covered 7 steps sooner. State this so readers can judge practical significance.
3. **Seed variability.** In deterministic cells the observation uniforms do nothing; all variance comes from tie-breaking. The SE against cycle reflects only lookahead2's tie-break RNG. Say this next to every interval, and consider also reporting the interval's upper bound, not only the mean.
4. **hidden_arm reference.** The equal-arm average is arbitrary: which arm state the learner is in depends on its own previous action (power sets the arm; wait and door clear it). Also report loss against each policy's empirical on-policy arm frequency, descriptively only.
5. **Extra tests.** Check g against a direct mutual-information calculation, the g ≥ −1e-10 guard, and the second-step score reusing the same row when (s′, b) = (s, a).
6. **Tie handling.** Record per step whether the choice was a tie. Early steps are nearly all ties, and this separates planning from RNG effects.
7. **Planner behaviour.** Consider reporting "steps to full coverage" and the final count imbalance for each world. These show what the planner actually does better than the averaged loss does.
8. **Review log.** Per AGENTS.md, record in research/review_log.md that this critique covers the protocol only, not code.

## What is sound

- World identities stay with the evaluator, and query outcomes are never fed back to the learner.
- Imagined updates don't touch the live model, and the two-step query correctly reinforces a row that repeats.
- Random streams are separated and paired, with no world key.
- The go/no-go rule does not fall back to a smaller run automatically.
- There is no tuning after results, and controls cannot rescue a failed screen.
- The citations and prior-art boundary are cited honestly and the scope is modest.
- The visualisation shows declared seeds, not cherry-picked ones.

The protocol does not assume lookahead2 wins: a fail is fully specified. The problem is that the cycle comparison and the pooled screen make part of the result predictable before any run.
