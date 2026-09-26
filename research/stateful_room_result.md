# Stateful room v0 — September 26, 2026

**Completed: a learner now explores persistent rooms and learns transition probabilities, including blocked actions.** The two-step planner passes the fixed primary screen. This is a small development study of known Bayesian learning and shallow planning, not a novel algorithm or autonomous scientist.

## What learns

Four visible states encode power/door; three actions press power, press door or wait. Each observation updates one of twelve Dirichlet tables: `P(outcome | state, action) = (count + 0.5)/(row visits + 2.5)`. Five outcomes distinguish four accepted next states from a blocked self-transition. The learner receives no door-rule library or hidden arm. The sensor channels, table form, prior, stationarity and blocked-action support are supplied.

Greedy selects immediate predictive information `g`; the planner selects `g + E[max next g]`, including hypothetical posterior updates, and replans after each observation. In deterministic worlds this reduces to count-based coverage planning. No neural network or separately trained RL policy is present. RL is not restricted to neural policies; this study simply tests explicit shallow planning first.

## Measured result

One full run: **640 episodes, 61,440 actions, 32 development seeds500–531**, five fixed worlds, four policies,96actions each. Primary mean excess one-step query loss over observations1–96: planner **0.50067**, greedy **0.51214**, random **0.60726** nats. Lower is better: approximately2.24% and17.55% reductions, respectively.

Paired planner-minus-comparator differences, averaging the three primary worlds within seed:

| Comparator | Mean | Descriptive normal95% interval |
| --- | ---: | --- |
| Random | −0.106583 | [−0.121252, −0.091915] |
| Greedy | −0.011462 | [−0.012687, −0.010237] |

Both means pass the prespecified≤−0.01 criterion. All six per-world harm guards pass≤+0.01; every primary world mean improves against both comparators. Intervals describe policy/tie randomness in these fixed worlds, not variation across new law families. These are inspected development data; no post-result tuning or held-out confirmation.

Each cell below is **mean one-step loss area / final joint two-step excess loss**. The three first rows are primary; controls stay separate. All other metrics, four two-step checkpoints, per-seed differences and per-world intervals are preserved in [summary](../results/stateful_room_v0/summary.json).

| World | Random | Fixed cycle | Greedy | Two-step planner |
| --- | ---: | ---: | ---: | ---: |
| gate_on | 0.60552 / 0.49792 | 0.49022 / 0.41924 | 0.50768 / 0.42255 | 0.49636 / 0.42047 |
| gate_off | 0.61152 / 0.49352 | 0.49022 / 0.41924 | 0.50142 / 0.42147 | 0.49648 / 0.42026 |
| directional | 0.60474 / 0.49993 | 0.96350 / 1.55576 | 0.52731 / 0.43754 | 0.50918 / 0.42760 |
| random_room | 0.24864 / 0.39943 | 0.25174 / 0.38538 | 0.26315 / 0.41885 | 0.25963 / 0.40711 |
| hidden_arm | 0.57012 / 0.74040 | 0.95035 / 2.07977 | 0.49479 / 0.65384 | 0.48046 / 0.62574 |

**Limits matter:** fixed cycle is slightly better in gate_on/gate_off because its prescribed path perfectly covers all twelve rows; it visits only six in directional. Cycle was designated descriptive before sampling. The planner is worse than random in the noise control by0.010993nats. Hidden-arm final two-step excess loss remains0.62574: the visible-state table cannot represent action-history dependence. Its one-step reference averages equally over hidden-arm states, not the learner's on-policy hidden-state conditional; two-step evaluation propagates the arm without resetting. Better stress scores do not demonstrate hidden-state discovery. No calibration, transfer or novelty claim.

## Verification, cost and review

All **65 tests pass**. Claude Opus5.5 independently reviewed the protocol; root fixed all four blockers before implementation. A separate Codex author wrote the learner, another wrote the viewer, and independent review checked code and evidence. See [review log](review_log.md) and [unchanged Claude critique](claude_stateful_room_review.md).

Clean source `e6978fdaa9385e94f034dd4f0300cfea3c5ac214`, Python3.9.6 on Apple Silicon. Internal elapsed2.80719seconds; external process wall2.85649seconds including final I/O,42,703,543raw artifact bytes. Selection-only mean microseconds/action: random 0.48, cycle 0.22, greedy 7.10, lookahead2 36.58; evaluator/serialization excluded. Planning therefore costs more compute despite equal observation budgets. The20episode smoke passed both conservative time/disk gates; source/config/artifact hashes are in [metadata](../results/stateful_room_v0/metadata.json). No new dependencies or additional spending.

## Replay and reproduce

[Open/download the self-contained replay](../visualization/stateful_room.html). It shows actual recorded actions, pre-action predictions, post-update counts, blocked probabilities and query-error curves. First two declared seeds500/501, all worlds/policies; full overview includes all32seeds. Default is the first world/seed and prespecified planner, not a favorable trace selected afterward. Evaluator truth is optional and initially hidden. It is playback, not an ongoing training job.

From repository root, choose fresh output names:

```sh
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B -m artificial_scientist.stateful_room --output results/runs/stateful_room_reproduction_smoke --smoke
.venv/bin/python -B -m artificial_scientist.stateful_room --output results/runs/stateful_room_reproduction --smoke-evidence results/runs/stateful_room_reproduction_smoke
.venv/bin/python -B visualization/export_stateful_room.py --run results/runs/stateful_room_reproduction
```

The full runner enforces120seconds internally; this recorded execution also had a150second external timeout. Compact JSON copies are byte-identical; large trajectories remain in ignored local runs and are reproducible. No extra data was collected for the replay.

**Next:** review a minimal history-aware predictor against this frozen visible-state learner on new development worlds. Test whether previous actions resolve hidden memory without hurting memoryless/noisy controls; give all comparisons equal interaction budgets. A supplied memory feature is a baseline, not discovered representation. Representation discovery remains a later, separate question.
