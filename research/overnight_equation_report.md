# Overnight report — September 26, 2026

**Three validation studies completed; 90 tests pass.** They separately test equation fitting, term evidence and domain challenges. No single selected equation completed the whole sequence. Inputs and six monomials are supplied, Gaussian noise is known, and nonzero coefficients are large relative to noise. This is not yet an autonomous scientist.

| Study | Finding | Fixed screen |
|---|---|---|
| 1. Fit equations | Correct support in 20/20 affine and 15/20 quadratic cases, but nonzero formulas in 9/20 noise cases | **Failed** |
| 2. Confirm terms | On new data, false-term datasets fell from 32/100 to 0/100 for noise and 15/100 to 0/100 for quadratics; retained 198/200 true quadratic terms | Passed |
| 3. Challenge the domain | Wrong quadratic fits were rejected locally versus widely in 10/40 versus 40/40 exponential cases, and 26/40 versus 40/40 cubic cases | Passed |

The third study demonstrated an intended counterexample: a crude error threshold rejected correct models in 29/40 wide tests; accounting for coefficient uncertainty reduced this to 2/40. Its three correct-model controls share noise/design, so they are duplicate checks, not independent evidence.

A concrete output, from the first declared seed of study 2, was:

    y ≈ -0.8360 u + 0.6315 u²

The simulated truth was -0.8621u + 0.6191u². Both terms received fresh-data support. This is coefficient fitting and selection from six supplied monomials; it does not demonstrate invented mathematical concepts. Confirmation filters claims without changing predictions. The domain test uses a fixed full model, so its guarantee cannot simply be attached to the selected sparse equations.

**What we learned:** fitting, term evidence, and falsifying a functional form are different problems. A local fit can look convincing and still fail elsewhere. The results match known theory. Even the first failed gate was close to expected BIC over-selection and provides little evidence of an unexpected failure. No defensible novelty claim emerged from the focused prior-art check.

**Next:** first review a valid end-to-end check of the same reported equation, with separate selection, refitting and untouched validation data. Then ask whether choosing challenge locations reduces observations needed to expose a wrong formula compared with fixed local, wide and random experiments. Count every observation and restrict the learner to its own hypotheses; true-law diagnostics remain evaluator-only. Drop the proposed subsecond CPU-saving objective. This is a revised proposal, not a fourth experiment.

Claude Opus 5.5 completed five reviews: direction, each stage, and final interpretation. Separate Codex agents implemented and reviewed code and independently audited all three runs. The final critique changed the next-step proposal; see the response below. All work used existing access and local CPU computation, with no paid API, new service or extra spending. The requested three-study sequence stops here rather than consuming the full eight hours.

[Study 1](equation_stage1_result.md) · [Study 2](equation_stage2_result.md) · [Study 3](equation_stage3_result.md) · [Prior art](equation_prior_art.md) · [Reproduce](equation_reproduction.md) · [Review record](review_log.md) · [Final critique and response](equation_final_review_response.md)
