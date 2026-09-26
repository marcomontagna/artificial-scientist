# The agent revised a modeling assumption—and improved predictions

**A complete failure → alternatives → experiment → revision loop now works.** On the new coupled-motion challenge, all three active runs adopted a cross-coordinate motion term and substantially improved unused-intervention predictions. The declared revision and experiment-selection screens pass on this small comparison. **The no-unnecessary-revision screen fails:** one of three active simple controls expanded needlessly. The delayed-effect stress world remains unresolved and active revision worsens its mean error.

This is useful prototype progress, not autonomous concept invention or novel science. Worlds were chosen for the declared capability, and the exact challenge is expressible in the supplied grammar. Three sensor-noise seeds do not establish generalization across laws.

## What happened in the predeclared replay

[Replay: challenge, active, seed 270001](../results/revision_v1/replay.html). This is the first declared run, not a selected success. It replays saved data; playback has not been browser-verified.

After experiment index 6 (14 tool actions), repeated recorded prediction errors triggered revision. The old model was shared `delta = .676*v + .440*u`. The agent generated three alternatives: separate coefficients by direction, add cross-coordinate motion, or add a nonlinear position term. These came from general supplied edit operations and training data; no world label or evaluator outcome entered search.

It froze all four models, selected four subsequent two-action experiments, and compared their predictions on exactly the same eight outcomes. The old model's check error was 0.021105; cross-coordinate motion scored 0.002885. The reduction exceeded the required 0.003166 margin. It adopted that alternative before refitting. The final formula was approximately:

```text
delta_x = 0.71243*v_x + 0.39202*u_x - 0.16478*v_y
delta_y = 0.63974*v_y + 0.39187*u_y + 0.20640*v_x
```

Here v is an observation-derived motion estimate and u is the push. The agent relaxed independent-axis/shared-coefficient assumptions using predefined operations; it did not invent the variables or arithmetic. Its frozen pre-check revision also improves the separate evaluator in this example. That is evidence for this revision's usefulness, not proof of a uniquely correct physical explanation.

## Complete comparison

Mean squared 2D position error across three declared seeds; lower is better. Every run had 80 training and 68 evaluation tool units. All methods used identical external sequences/noise streams within each seed. Scores concern new challenge/stress worlds and a longer evaluator, so they are not numerically comparable with earlier reports.

| World | Active revision | Random revision | Coverage revision | No revision, coverage | Original enumerator |
|---|---:|---:|---:|---:|---:|
| Simple control | 0.001937 | 0.001036 | 0.002056 | 0.001775 | 0.001937 |
| Coupled challenge | 0.000679 | 0.000971 | 0.000920 | 0.087390 | 0.078046 |
| Delayed stress | 0.027856 | 0.023753 | 0.060130 | 0.024132 | 0.042428 |

Challenge: active error is 99.2% below no-revision, 30.1% below matched random revision and 26.2% below matched coverage revision. It beats no-revision on 3/3 seeds, and each matched exploration control on 2/3. Random and coverage also adopt the cross-coordinate structure in all three runs and improve sharply. This is consistent with representation expansion accounting for much of the gain, rather than a unique insight by active planning. Only up to 16/80 training units can be directed by competing explanations.

The same-data 18-parameter vector-regression reference scores 0.001966 on active challenge data, versus 0.000679 with six selected parameters. This meets the declared baseline-credit screen, but the reference performs poorly on some simple-control data. It is an untuned, overparameterized reference with noisy motion features; this does not establish superiority to strong tuned system-identification methods.

## Failures and practical screens

- All three active challenge runs complete at least one check and adopt cross-coordinate motion. Functional integration passes.
- The predeclared 20% revision and 10% experiment-selection mean-improvement screens, with at least 2/3 paired wins, pass. These are descriptive engineering screens, not significance tests.
- Active simple-control error is 9.1% worse than no-revision. It stays within the declared tolerance, but one of three active runs adopts an unnecessary coefficient split. Its internal acceptance is rejected by the post-run external comparison. The clean no-unnecessary-expansion screen fails.
- Active stress error is 15.4% worse than no-revision. All three active runs retain the `unresolved` flag; two make provisional revisions. Adoption of an approximate model is not automatically an error, but it does not solve the missing delayed-state representation. Random revision is also better than active here.
- Internal and external accept/reject decisions agree on 3/4 challenge cycles, 2/3 control cycles and 2/6 stress cycles. These compare the same frozen candidates with the same adoption margin on different interventions, after execution only. They expose limited transfer of the internal check; they are not an oracle about correct adoption. Recent-failure flags can also miss inadequate models in other policies.

[Full per-seed summaries and screens](../results/revision_v1/summary.json) · [171 raw-file fingerprints](../results/revision_v1/raw_manifest.json). 45 runs completed, 3,392 training tool actions, 3,600 training cost units and 3,060 evaluation cost units. Recorded process CPU time totaled 11.32 seconds. No post-outcome tuning or additional runs.

## Provenance and next decision

World source dfabfe1; complete implementation/protocol frozen at 3dc00a2. 59 tests passed before runs, including chronology, evaluator isolation, actual trigger/cooldown/caps, partial timeout accounting, synthetic journal ordering and safe replay export. Tests are engineering checks, not learner-performance evidence. [Exact protocol](revision_loop_design.md) · [World contract](revision_world_contract.md) · [Review log](review_log.md).

The declared short-memory grammar can express the coupled challenge, but does not explicitly contain the stress world's delayed drive. This does not prove that no formula can approximate finite stress trajectories. World authors saw generic operator intentions, not learner outcomes; source separation is not formal blinding.

The next decision is about the reliability of the check, not more proposal ranking or a larger world suite. Preserve the useful revision behavior while examining why a chosen set of diagnostic experiments can endorse a change that fails elsewhere. No next experiment has been launched.

## Claude’s result critique and our response

[Verbatim review](claude_revision_result.md) · [Provenance](revision_result_claude_provenance.json). Claude accepts the end-to-end capability demonstration, but challenges a general active-selection claim, the weak full regression reference, and reassurance from a tolerance-passing control result. We agree: a `true` numerical screen in the summary means only the declared descriptive threshold passed. It is not proof of superiority or broad discovery. Independent recomputation verified the regression implementation; its poor performance does not itself prove a code bug or establish a strong baseline.

Both accepted stress snapshots perform worse than their own frozen incumbents on the external tapes: seed 270001,0.023607 versus 0.021124; seed 270002,0.029132 versus 0.019595. In the second case a different alternative would improve externally, which is why accept/reject agreement alone can hide a wrong choice. These are post-run diagnostics with no effect on adoption.

Claude suggests longer checks and default abstention. We retain that as a design question, not an automatic code change. Its claim that two-step checks structurally cannot observe an 11-tick delayed effect is too strong: checks occur after earlier actions, so delayed effects can appear in their next observations. Short checking horizons and mismatched interventions are plausible transfer problems, not established exclusive causes. Replaying later trajectories also would not reproduce the actions an altered policy would have chosen. Any such analysis must remain labeled post-hoc; no adopted rule or new experiment is claimed here.
