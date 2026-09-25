# Causal-world feasibility result — September 25, 2026

**Passed as a code/foundations check.** Some declared action mixtures distinguish these hidden-common-cause worlds from every observed-only DAG. Passive observation and pair-only interventions do not. This expected mathematical pattern is not a new scientific finding, a learned policy or a power result.

The [fixed specification](../experiments/causal_feasibility_v0.md) enumerates 13 population worlds × five action mixtures × 25 graphs. All 65 zero/positive comparisons passed; distributions/support and relabeling checks passed. All 37 unit tests passed. The calculation took 0.118 seconds using clean source commit `14e722734c4e8e5666037e96d07701fa754ffeea`. No random samples or seeds were used.

## Quantitative check

Minimum weighted KL from the true interventional distributions to the observed-only DAG class, nats per sample under each fixed mixture. These are population discrepancies, not observed learner losses or finite-sample detection rates. All three pair relabelings agree within tolerance; the table shows one pair.

| Noise e | Passive | Uniform seven | Uniform six interventions | Privileged pair only | Privileged passive + pair |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0.50 | 0 | 0 | 0 | 0 | 0 |
| 0.35 | 0 | 0.000696 | 0.000677 | 0 | 0.000541 |
| 0.20 | 0 | 0.011610 | 0.011233 | 0 | 0.008925 |
| 0.05 | 0 | 0.074474 | 0.070120 | 0 | 0.053694 |

The observed-fork null control has zero discrepancy under every mixture. Values within 1e-10 of zero are shown as zero. Privileged designs receive the true confounded pair; they are evaluator references, not learner policies. They are not claimed optimal. Pair-only interventions make the unmanipulated variables independent and erase the relevant evidence; more targeting is not automatically informative. Multiple graphs tie for the best fit, and no graph has been identified.

The independent closed-form reference is in the specification. Unit tests verify the pooled CPT optimum and perturbations, normalized pre-outcome predictions, exact Dirichlet evidence, and likelihood domination on short adaptive histories including boundary probabilities. A deliberately post-update prediction fails normalization. These checks support implementation correctness; the statistical argument supplies the conditional anytime guarantee. No false-alarm or detection-power study was run.

## Reviews, provenance and next decision

Claude Opus 5.5 independently [reviewed the design and code](claude_causal_feasibility_review.md), identifying weak optimum tests, a vacuous crossing assertion, ambiguous graph labels and interpretation/provenance issues. Codex applied the fixes; a distinct Codex reviewer checked the final source and specification before the run. The original Claude review describes the pre-fix version. Its suggested alternative numerator for a future finite-sample test remains a hypothesis, not an implemented improvement.

[Summary](../results/causal_feasibility_v0/summary.json), [all graph fits](../results/causal_feasibility_v0/graph_fits.json), [gate](../results/causal_feasibility_v0/gate.json), [config](../results/causal_feasibility_v0/config.json), [source and artifact hashes](../results/causal_feasibility_v0/metadata.json). Reproduce from the repository root into a fresh directory:

```sh
python3 -m unittest discover -s tests -v
python3 -m artificial_scientist.causal_feasibility --output results/runs/causal_feasibility_reproduction
```

**Next:** preregister a small finite-sample check of known sequential diagnostics under fixed non-privileged designs before comparing adaptive policies. Establish whether the statistic can achieve useful power within the sample budget while preserving its false-alarm guarantee. Specify the alternative predictive distribution, stationary null and confounded worlds, action schedule, stopping/censoring, primary metrics and thresholds before running. Retain weak/no-separation cases. The saturated alternative may be statistically costly; compare justified alternatives without adding an untested policy at the same time.

No new autonomous scientist, causal learning policy, model repair, law-change adaptation, transfer, or novelty is demonstrated. V1/v2 remain frozen. No paid service, dependency or system change; original sequence-world reserved seeds remain unused.
