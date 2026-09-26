# Response to Claude’s final review

The [unchanged critique](claude_equation_final.md) reviewed all three completed studies. Its request/response/report hashes are in [provenance](equation_claude_provenance.json). No additional study or tuning followed it.

**Accepted:** these are validations of known theory, with supplied variables/monomials, known Gaussian noise and strong signals. The small first gate was near expected BIC over-selection; its failure remains recorded but does not reveal an unexpected defect. The third result matches evaluator-computed theoretical power, and its cubic point-estimate screen is not a confidence statement that the population gain exceeds30points. The crude-threshold example was intentional. No single selected equation went through all three stages. Reports now say this prominently.

**Direction changed:** drop subsecond CPU savings as the next scientific objective. First review a coherent same-equation selection/refit/validation object. Then test observation efficiency of learner-chosen challenge locations against fixed local/wide/random schedules, using learner-available hypotheses. Grammar revision follows only if useful, with ordinary model-selection and always-large baselines. True-law noncentrality cannot become an acquisition oracle. No new experiment was run.

**Corrections to the critique:**

- Stage2 did check frozen-candidate predictions: its independent audit records MSE and uses candidate residuals in likelihood ratios. It did not refit the equation or improve those predictions. We retain that distinction rather than the literal statement that no predictions were checked.
- The stage1 dense exponential MSE test rejected1/20. Stage3’s local uncertainty-aware AND crude MSE rules each rejected10/40. Different samples/designs and test definitions prevent attributing the gap solely to a changed statistic. No controlled between-study causal claim is warranted.
- Independent selection/refit/check splits are a useful starting point, not a blanket validity guarantee. The proposed future protocol must specify the selected-family null and account for whether it contains the true mean; false-family rejection is a power question. The predictive statement also requires full rank and is marginal over refit/check noise, not conditional on realized fitted coefficients. Split-likelihood term guarantees are generally conservative, not exact-size tests. Unknown-variance tests and term-null families need their own derivations. Current known-sigma formulas cannot simply be relabeled F-tests or treated as generally exact after selection.
- Do not release reserved sequence seeds1000–1049 simply because Claude suggested them. A reviewed future protocol must define the new study’s split and rule families explicitly.

The suggested newer experimental-design references are literature leads for the next review, not novelty clearance. The completed [focused map](equation_prior_art.md) already establishes close overlap with symbolic regression and active equation learning. The reusable outcome tonight is tested code and bounded evidence, not a new scientific-discovery method.
