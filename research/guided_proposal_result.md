# Observation-guided proposals: implemented, with mixed results

**The idea makes sense as selective search, not as a requirement to imitate humans.** The new mode uses observed prediction failures to select a few local formula changes before fitting. It is implemented and its hypotheses influence actual experiment choices. It is not consistently a better learner, so it remains an opt-in experiment; enumeration stays the default.

## A concrete investigation

In the guided development run, after action 11 (zero-based), an input-only model was the incumbent. Its signed prediction errors over eligible actions 7–11 were strongly associated with observed motion v (maximum coordinate correlation 0.979). That association motivated adding a motion term, producing a provisional `v+u` structure. It did not establish a physical mechanism.

At action 12 the agent pushed downward. Removing that proposed model and renormalizing the other models’ fixed weights would instead select a leftward push. Both options and predictions were recorded before the outcome. This is a demonstrated influence on that decision, not proof that the choice was optimal or that the proposed explanation was true.

The final predictor was `delta = 0.817131*v + 0.417184*u`. Its motion/input structure is within the supplied grammar. No new mathematical primitives or concepts were invented.

## Prediction and search costs

Same worlds, fitter, planner formula and 80 training cost units per run. Each final model predicted the same fixed evaluator interventions, without receiving those outcomes for fitting. These environments, seed and checks had already been inspected; results are developmental and descriptive.

| World | Enumerating: prediction error | Guided: prediction error | Candidate fits, enumerating → guided | Diagnostic feature evaluations, guided |
|---|---:|---:|---:|---:|
| Development | 0.001237 | 0.000288 | 2340 → 99 | 3640 |
| Challenge | 0.026477 | 0.053171 | 2702 → 55 | 1240 |
| Noise | 0.118847 | 0.119674 | 3402 → 74 | 1840 |

Error is mean squared 2D position error across the existing 11 evaluation horizons. Guided prediction improves on this simple-world control, roughly doubles the error on the harder world and is slightly worse in noise. The development linear reference fitted from guided data has error 0.000243, below the guided formula’s 0.000288. Neither approach demonstrates a new scientific discovery. Full reference scores are in the [summary](../results/guided_v1/summary.json).

Candidate-fit reduction is real but expected from the cap, not proof of useful intelligence. Retained-model refits also cost work: enumerating/guided counts were 300/381, 348/370 and 544/532. Measured process CPU seconds, including evaluation, were 0.492/0.421, 0.622/0.362 and 1.650/0.754; these tiny single timings are not a speed benchmark. Screening counts only diagnostic feature-value evaluations, not all expression arithmetic. Six runs completed 343 actions in about 4.30 CPU seconds total; training 480 units plus unchanged evaluation 264 units. No tuning or extra sampling followed.

## Did observations actually matter?

The guided mode fitted at most 8 candidate structures per update; its shortlist was fixed before fitting. It selected 24/11/16 association-driven proposals and 4/8/10 scheduled escapes in development/challenge/noise. The complete-formula enumerator was never called by the guided branch. All 20 individual supplied features were cheaply screened, including interactions; this is still bounded search, not search-free understanding.

On 32/53 development decisions, 30/52 challenge decisions and 6/74 noise decisions, removing at least one association-proposed model would change the current action. Each counterfactual keeps the other weights fixed except renormalization and performs no retraining. Thus it establishes influence on a decision, not long-run benefit.

New proposals often disappoint. Across all proposal origins, the first three subsequent actions with both proposal and parent predictions gave lower paired error for 6/28 development proposals, 5/19 challenge proposals and 5/26 noise proposals. Respectively 4, 2 and 4 proposals lacked three common predictions; the rest did not improve that paired score. This descriptive post-run summary conditions on selected actions and is not a physical-hypothesis confirmation/refutation test. Noisy position/motion associations can be predictive without identifying real dynamics.

## Review, replay and next decision

Twenty-eight tests pass. Claude Opus 5.5 critically reviewed the design; separate Codex agents reviewed design/code and independently audited all six runs. The audit matched all metrics, 336 residual-support records and 1081 one-decision counterfactuals. The enumeration control reproduces v1’s actions, selected models and evaluations exactly. Source was frozen at `d567435b36b74b64ab62a61e4a41837e8060b1ef` before execution.

[Open/download the guided replay](../results/guided_v1/replay.html), then inspect action 11 and 12. It shows saved evidence → proposal → next choice, including unavailable or unchanged effects. This is offline playback, not ongoing training. Export safety/data checks passed; browser playback remains unverified because local-file navigation was previously blocked. No workaround was attempted.

Next: investigate the harder-world trace before changing anything else. The useful `v+u` approximation appears after action 39 there, versus 11 in development; why the local search reaches it late is a concrete question. Incumbent switching, sparse eligible evidence, permanent exclusions and a misspecified shared representation are plausible limitations, not established explanations. Do not replace the default on the strength of the simple-world win or add the hidden law as an answer.

## Run it

From the repository root, with existing local Python 3.9+:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m artificial_scientist.lab_run --proposal guided --policies active --variant development --output results/runs/my_new_guided_run
```

Use a fresh output directory. Omit `--proposal guided` for the preserved enumerating control. Default seed 260926; the six recorded outputs are `results/runs/guided_v1_{development,challenge,noise}_{enumerate,guided}`. [Raw hashes](../results/guided_v1/raw_manifest.json), [exact design/Claude response](guided_proposal_design.md), [review log](review_log.md). No extra spending or new dependencies; all runs are finished.
