# Independent assessment of the adaptive-state line — September 25, 2026

**Status: DRAFT, pending independent review by Codex.** Author: Claude (Opus 5.5, Claude Code), acting as an independent critic at the user's request. Not reviewed by anyone else yet. Nothing here updates RESULTS.md, NEXT_STEPS.md or any owned file. Existing code and results are unchanged. Nothing was pushed, and reserved seeds 1000..1049 were not used.

## Bottom line

1. **Do not continue the v-series selectors on this benchmark.** The adaptive selector picks from a fixed list of pre-built experts. Here, the fixed-share mixture it is compared against already comes within about 0.01 nats of a privileged learner told the true lag. So even perfect lag selection could gain at most about 0.01 nats. v1 and v2 are each worse than the matched mixture in 20/20 structural development cases, and in 78–79/80 cases on 20 further non-reserved seeds. This matches the classical result, not a new finding (Herbster & Warmuth 1998; van Erven, Grünwald & de Rooij 2012).
2. **The planned factorial ablation (fast simple alternative × reversibility) is not worth running as designed.** A bounded probe shows the 64-tick check period drives much of the v1/v2 gap to the mixture. The factorial leaves that factor out, so it would mainly measure details of a hand-written heuristic that is already dominated.
3. **The resource hypothesis cannot be tested in the current design.** Every alternative is allocated and trained from tick 0. The comparison of logical slots (v2 915.6, mixture 147.6) mostly measures how the loss buffers happen to be implemented. The repository already says this, correctly.
4. **Verdict for the current direction: reject as a novelty or method line, keep as a reproducible harness.** If the user wants to keep studying the adaptive-state question, it only has content in a redesigned setting: one where keeping every candidate is impossible at equal budget. That redesign should pass a pre-set headroom check before anyone builds a learner. Its novelty is also doubtful (see §4). "No defensible novelty found" is my honest reading of the current state.

## 1. What I checked, and what it verified

All checks ran locally with standard-library Python 3.9.6, in one process at a time. Total runtime was under 20 seconds. Probe scripts stayed in the session scratchpad and were not added to the repository. The method for each probe is described well enough below to re-implement.

| Check | Result | Status |
| --- | --- | --- |
| `python3 -m unittest discover -s tests` | 29/29 pass | Verified |
| Re-ran `adaptive_state_v2.simulate` in memory from the tracked config, compared with `results/adaptive_state_v2_dev/summary.json` | All 420 phase summaries identical (max abs diff 0.0) | Verified |
| Reported v1/v2 post-change correct-lag occupancy, 82.13% / 76.80% | Recomputed from decisions.json: 0.8213 / 0.7680 | Verified |
| Reported structural post-change logical slots, v2 915.6 / mixture 147.6 / v1 649.6 | Recomputed from summary.json: identical | Verified |
| Hidden-state leakage, predict-before-update, next-tick decision effect, change-time use | Code read of `sequence_worlds.py`, `adaptive_state.py`, `adaptive_state_v2.py`: learners receive only realized bits. Scoring precedes update. Decisions take effect from the next prediction. The lag and condition labels live only in the generator and evaluator. No privileged reset. | Verified by inspection. No leakage found. |

## 2. New empirical findings (exploratory; bounded probes)

Unless stated otherwise, all numbers are mean post-change log loss in nats. "Oracle" means the evaluator's true probability. It is a **privileged reference, not a competitor**. Seeds 0..4 had already been inspected. **Seeds 100..119 were used here for the first time and must now count as inspected development seeds.** They must not later be used as held-out seeds.

### 2.1 The benchmark leaves almost no room for better selection

Excess loss over the oracle, dev seeds 0..4:

| World | slow | fast | v1 | sparse mix | matched mix | v2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stable | .0038 | .0299 | .0038 | .0044 | .0054 | .0048 |
| parameter | .0759 | .0506 | .0768 | .0610 | .0364 | .0577 |
| noise | .0193 | .0280 | .0193 | .0185 | .0159 | .0212 |
| structural lag 2 / 3 / 4 / 5 | ≈.21–.23 | ≈.18–.24 | .063–.067 | .051–.058 | .050–.058 | .070–.077 |

A privileged learner that runs only the correct sparse expert (1,k) from tick 0 knows the structure but not the change time. Its structural post-change loss was **0.5374**, against 0.5472 for the matched mixture (seeds 0..4). On seeds 100..119 it was **0.5422 vs 0.5515**. This bounds what a perfect hard selector over this bank could gain on structural worlds at about 0.01 nats. The rest of the mixture's roughly 0.05-nat excess over the oracle comes from relearning inside the discounted count tables after the change. No selector over these experts can remove that part.

It also means v2 screen condition 3 (penalty vs matched mixture ≤ 0.02 nats) allowed about twice the whole available headroom. So the screen **passed even though v2 was worse than the mixture in 20/20 structural cases**. Per-seed penalties ranged from 0.0099 to 0.0239. That condition could not tell a useful selector from a clearly dominated one.

### 2.2 The mixture's dominance holds on new seeds

Paired differences against the matched mixture. Seed-SE means the standard error across seeds of the per-seed mean.

| Comparison | seeds 0..4 | seeds 100..119 |
| --- | --- | --- |
| v1 − mix, structural | +.0097 (SE .0015), worse 20/20 | +.0108 (SE .0012), worse 78/80 |
| v2 − mix, structural | +.0181 (SE .0025), worse 20/20 | +.0156 (SE .0013), worse 79/80 |
| v2 − mix, parameter | +.0214, worse 5/5 | +.0179, worse 20/20 |
| v2 − mix, noise | +.0052, worse 4/5 | +.0043, worse 18/20 |
| v2 − mix, stable | −.0006, worse 2/5 | −.0022, worse 5/20 |

The only place selection beats the mixture is stable worlds, by about 0.001–0.002 nats. There the mixture pays for putting some weight on the fast expert. This is the ordinary cost of hedging, and the mixture's share parameter controls it.

### 2.3 Check cadence explains much of the "delay"

This is a diagnostic, not a proposed tuning. Same windows and thresholds as before, but the decision is checked every tick instead of every 64 ticks.

| Structural gap to mixture | every 64 (as run) | every 1 |
| --- | --- | --- |
| v1, seeds 0..4 / 100..119 | .0097 / .0108 | .0010 / .0024 |
| v2, seeds 0..4 / 100..119 | .0181 / .0156 | .0050 / .0062 |

The change is at tick 600, and checks fall at 640, 704 and 768. The reported "v2 activates at 704 or 768 vs v1 at 704" is a gap of one check period. The v1-vs-v2 difference comes from an interaction between the stronger fast simple comparator and the coarse check schedule. The planned factorial varies the comparator and reversibility but not the check schedule, so it cannot separate these effects. Even checking every tick, both selectors still trail the mixture in most structural cases: v2 77/80, v1 58/80 on seeds 100..119.

### 2.4 Return-to-simple probe (the proposed next experiment)

Worlds run stable → structural(lag k) at tick 600 → stable at tick 1200, for 1800 ticks, seeds 100..119 × lags 2..5 (80 worlds). Loss on ticks 1200–1799: slow lag-1 **.5159**, matched mixture **.5168**, v2 **.5286**, v1 **.5337**, v2 checking every tick .5260. v2 contracted in 80/80 worlds, 80–144 ticks after the return, but it was still worse than the mixture in 79/80 worlds and worse than plain slow lag-1. Contraction works mechanically. It just does not help prediction, because each sparse expert (1,k) contains lag-1 as a special case and only needs to relearn. So NEXT_STEPS item 1 would show, at best, that contraction "works". It would not show that contraction is worth anything. This probe partly pre-empts that experiment. Any future protocol for it should say that this probe was run.

## 3. Design critique (reasoning, not new measurements)

- **The true hypothesis is built in by design.** The structural rule is always `x[t-1] XOR x[t-k]` with k in 2..5. The sparse bank is exactly {(1,k): k = 2..5}. So "detecting insufficient state and expanding it" reduces to choosing among 4 pre-enumerated candidates, one of which is known to be correct. The learner sees no hidden information at runtime. But the designer's knowledge of the rule family is written into the candidate set. No result here says anything about finding a feature that was not supplied.
- **Pre-change prefixes are shared.** All 7 conditions for a seed share the same first 600 observations. "0/5 stable and 0/5 noise pre-change expansions" is therefore the same 5 prefixes counted again, not 10 or 35 independent null trials. The repository says the cases are correlated. This is a more specific form of that caveat.
- **The comparison between hard selection and a Bayesian mixture is settled in principle.** Fixed-share mixtures track the best expert over segments with bounded regret (Herbster & Warmuth). The catch-up phenomenon, where Bayesian averaging is slow to move to a more complex model, and the switch distribution that fixes it, are van Erven et al. 2012. A thresholded windowed hard selector is a cruder version of the same thing. On log loss it is expected to lose, as it does here.
- **Logical-slot accounting depends on implementation.** Loss buffers of capacity 128 per expert dominate the selector's storage. An exponentially weighted running loss would make them O(1). So neither "v2 uses 6× the mixture's memory" nor any reverse claim is a property of the idea. Measuring memory in this design cannot support conclusions either way.
- **Missing baselines, if the line continued:** CTW/SkipCTS with the same discounting, Partition Tree Weighting for nonstationarity, and a small online recurrent network with a matched parameter count. The audit already lists the context-tree ones; PTW is my addition and I have not verified it here. They matter less now, because the simpler matched mixture already dominates.

## 4. Novelty classification

| Component | Class |
| --- | --- |
| Procedural sequence worlds with hidden change | Engineering harness (useful, not novel) |
| Selection among supplied experts with a windowed likelihood-gain threshold (v1/v2) | Reproduction of known, dominated approaches (model selection / expert tracking) |
| "Detect insufficient memory and add it" | Prior art in RL with hidden state: Utile Suffix Memory "creates only as much memory as needed", using statistical tests to separate noise from structure (McCallum, ICML 1995; abstract-level check). Also variable-order and context-tree methods already in the repo's audit. |
| Budgeted discovery of new features/experts | Occupied at least at the framing level: online generate-and-test representation search (Mahmood & Sutton 2013; abstract-level check only, the PDF text could not be extracted here) and tracking a growing number of experts (Mourtada & Maillard, ALT 2017; abstract checked). |

I found no plausible methodological novelty in the current line. This is a bounded check (about six sources, abstract-level for three), not an exhaustive search. It is enough to shift the burden onto anyone claiming a gap.

## 5. What work is justified next

In order of priority:

1. **Record the boundary result and close the v-series (low cost, high value).** Suggested finding for the RESULTS owner: "On these worlds a fixed-share mixture over the same experts dominates thresholded hard selection. A privileged correct-lag expert beats the mixture by only about 0.01 nats, so this benchmark cannot separate better selectors." Include the per-case win counts. Do not run v3 or the factorial ablation.
2. **Add a headroom gate to every future protocol (process fix).** Before implementing a learner, measure privileged references: the oracle, and a correct-structure learner without change knowledge. Also measure the strongest cheap baseline (here, the fixed-share mixture). Proceed only if the pre-set margin between them is larger than the effect the learner would need to show. Report per-case win/loss counts and seed-level SEs next to the means. Screen thresholds must be set relative to this measured headroom. Condition 3 of the v2 screen failed this test.
3. **Only if the user wants to keep the adaptive-state question: redesign so it has content.** The needed property is a candidate space too large to keep at equal budget. Examples: lags up to 32–64, or interactions of 2–3 bits, where enumerating every sparse context exceeds a fixed memory and compute cap. Only then does "when and what to add" differ from mixing. Compare at matched logical memory and per-tick compute: fixed-share over a fixed random subset of candidates; a budgeted generate-and-test baseline; SkipCTS/CTW truncated to the same budget; a small online GRU. Report log loss against budget. Warning: a 2-bit XOR pair has no signal in either single bit, so greedy search on single features cannot find such pairs. At larger scale this becomes a noisy-parity problem, which is computationally hard in general. The world family has to be chosen so the task is learnable in principle, or the result is guaranteed to be negative. Treat this as an **evaluation study, not a method claim**, given §4. It needs its own novelty pass and critic review before any code.
4. **Consider whether this is the right sub-question at all.** The stated destination is a learner that chooses experiments. Observation-only sequence prediction exercises none of that. The earlier critique found active sensing and quickest change detection also well occupied. Before continuing, the user should decide which kind of outcome they value. One option is an honest, reproducible teaching and evaluation harness, which the repo is close to already. The other is a research claim, and nothing in the evidence so far points to a surviving gap.

**Not justified now:** new selector variants, neural learners on the current worlds, memory or efficiency claims, held-out evaluation, visual or planetary universes.

## 6. Verified vs speculative

- **Verified (run or read here):** everything in §1; all numbers in §2 (development-only, exploratory, one run each); the code properties in §3; the source metadata in §4 at the depth stated.
- **Reasoned but not measured:** that O(1) running losses would remove the storage gap; that item 3's redesign would give the learner any real room to improve (untested; the headroom gate exists to check exactly this); how noisy-parity hardness would apply to specific world designs.
- **Not done:** no full reading of the four new sources; no CTW, SkipCTS, PTW or RNN baseline implemented; no check of the visualizations; no check of Notion or GitHub publication state; no held-out seeds.

## 7. Residual objections even if the coordinator proceeds

- All development evidence covers one rule family (XOR with lag 1), one noise level (0.8), one change time, and one discount (0.99). Every conclusion, including mine, is conditional on that.
- The project's review chain has so far been Codex reviewing Codex. The reviews were careful about provenance and hashes, but did not check whether screens could discriminate at all (the ≤ 0.02 allowance vs about 0.01 headroom). Future reviews should question whether a measurement can discriminate, not only whether it was computed correctly.

## Sources consulted (primary records, depth as stated)

- Herbster & Warmuth, *Tracking the Best Expert*, Machine Learning 32(2), 1998. https://link.springer.com/article/10.1023/A:1007424614876 (bibliographic record and abstract)
- van Erven, Grünwald & de Rooij, *Catching up Faster by Switching Sooner*, JRSS-B 74(3), 2012; arXiv:0807.1005. https://arxiv.org/abs/0807.1005 (abstract)
- McCallum, *Instance-Based Utile Distinctions for Reinforcement Learning with Hidden State*, ICML 1995. https://mlanthology.org/icml/1995/mccallum1995icml-instance/ (abstract)
- Mahmood & Sutton, *Representation Search through Generate and Test*, AAAI 2013 workshop. https://www.aaai.org/ocs/index.php/WS/AAAIW13/paper/view/7164 (abstract only; PDF text not extractable here)
- Mourtada & Maillard, *Efficient Tracking of a Growing Number of Experts*, ALT 2017. https://arxiv.org/abs/1708.09811 (abstract)
- Context-tree and SkipCTS entries: see `research/state_revision_prior_art.md`. I did not re-verify them. Partition Tree Weighting (Veness et al.) is cited from memory and not verified in this session.
