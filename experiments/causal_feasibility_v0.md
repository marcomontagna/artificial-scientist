# Causal falsification feasibility v0

Status: specified before calculation, September 25, 2026. Codex primary author; distinct Codex independent_review accepted the mathematical design before implementation. Claude reviews the resulting specification and code before the full calculation. This is a distinguishability/implementation check of known methods, not a new learner, policy comparison or novelty result.

## Worlds and actions

Three observed binary variables; episodes are stationary. A fair hidden U influences one of the three variable pairs: each member is U XOR an independent Bernoulli(e) noise; the remaining variable is an independent fair bit. Enumerate all three pairs at e in {0.5, 0.35, 0.2, 0.05}, preserving e=0.5 as an in-class control. An additional observed-fork control uses X0 fair and Xi=X0 XOR Bernoulli(0.2), i=1,2. No sampling or seeds: sum latent states/noises exactly using floating-point arithmetic.

Seven actions: observe, do(Xi=0), do(Xi=1). Each returns one joint sample; intervention replaces only the manipulated structural equation. Passive support has eight outcomes; hard-intervention support has four. True probabilities and hidden pair are evaluator-only. This calculation deliberately has privileged access; a future learner must not.

## Fixed comparisons

For each of 13 worlds, use five fixed action mixtures: passive only; uniform over all seven; uniform over six interventions; uniform over the four interventions on the true confounded pair; uniform over passive plus those four. The last two are privileged designs, supplied the pair. For the fork control their designated pair is (1,2). No optimization, parameter sweep beyond this declared grid, or adaptive policy.

The null is the union of all 25 acyclic graphs on three labeled observed variables, with independent exogenous noise and arbitrary fixed binary CPTs. For every graph, minimize sum_a w_a KL(P_a || P_a^G) by pooling expected parent/outcome counts across regimes where the node is not intervened, then fitting each conditional proportion. A zero-mass row uses 0.5 without affecting the objective. Enumerating all graphs gives the global null minimum for the specified mixture. Save all 25 distances, fitted CPTs and all minimizing graphs within tolerance; the representative index is an arbitrary tie-break, not a recovered structure.

## Predefined checks and interpretation

- Normalized distributions, correct do support, exactly 25 unique DAGs, and nonnegative KL up to 1e-10 roundoff.
- Passive-only and e=0.5 have zero separation (absolute tolerance 1e-10); the observed-fork null has zero under every mixture.
- Pair-only interventions also have zero separation: they erase the confounded pair correlation; all remaining random variables in those regimes are independent. This deliberate negative control must be retained.
- For e<0.5, the uniform-seven, uniform-six and passive-plus-pair mixtures should have separation above 1e-8. Distances must agree across relabelings within 1e-10. These are numerical distinguishability checks, not practical effect thresholds.

A passed check means some declared action sets distinguish these population distributions from the null. It does not establish finite-budget power, faster discovery, uniqueness of a confounding diagnosis, calibrated prediction, transfer, a learning policy or a literature gap. A failed check is saved and investigated without changing this version's worlds to manufacture a pass.

## Independent analytical reference

For these balanced mixtures, let r=(1-e)^2+e^2, c be the weight of passive/third-variable interventions, and a the weight of interventions on either one pair member. Both members receive the same total weight. Fitting the explanation A→B gives q=(c*r+a/2)/(c+a) and minimum distance c*KL(Bern(r)||Bern(q)) + a*KL(Bern(1/2)||Bern(q)). Zero-weight terms contribute zero. The independent third variable and balanced intervention values make every complete DAG ordering give this value; smaller DAGs embed in complete ones and cannot improve it. This reference was separately checked by Codex independent_review before running, and agrees with Claude's qualitative argument. It is not claimed for arbitrary mixtures.

Use the reference as a numerical check of graph enumeration/projection. Perturbing the pooled optimum should worsen its objective. This is a known distinguishability pattern and an implementation check, not a discovered effect.

## Sequential arithmetic validation only

Implement reusable exact null maximum likelihood from observed regime counts and a saturated Dirichlet(1/2) predictive model per regime. Form log E_n = log Q_n - max_G log L_n(G), with every Q factor predicted before its outcome. Under each fixed null, E_n is dominated by its likelihood-ratio supermartingale; the reviewed argument in research/research_reset.md supplies the anytime guarantee under the stated assumptions. Tests cannot supply the proof.

Compute in log space; no probability clipping that could lower the null supremum. Outcomes inconsistent with a hard intervention are rejected as malformed input. With the present unrestricted CPT null, every finite support-consistent history has positive null likelihood (the independent fair model witnesses this), so the denominator cannot be zero. A particular deterministic null may assign a path zero probability; exhaustive checks omit only such zero-weight paths. On broader future nulls, zero supremum and zero/zero cases require a new explicit convention before reuse.

Tests independently compare marginal predictions with closed-form Dirichlet evidence, maximized likelihood with simple analytical cases, and exhaustive short histories under a predictable outcome-dependent action rule. Check likelihood domination and normalization, including boundary-CPT nulls; do not claim this short horizon tests rejection behavior. A deliberate post-update-scoring calculation must fail normalization. These small checks validate arithmetic only, not power or general false-alarm control.

## Execution and artifacts

Standard library, one local process, at most 60 seconds for the full deterministic calculation, no downloads or paid services. Write to a fresh repo-scoped results/runs/causal_feasibility_* directory. Preserve config, every fitted graph/distance, concise gate summary, source/spec hashes, Python/platform, Git state and runtime. Track small outputs under results/causal_feasibility_v0. No existing result is overwritten; sequence-world reserved seeds remain untouched.

After tests and separate code review, commit the source, then run exactly this version once under an external 60-second timeout. Copy tracked artifacts explicitly and record the test result in the report. If distinguishability checks pass, the next task is a reviewed finite-sample protocol, including a fixed world distribution, equal action budgets, prediction loss and censored detection outcomes—not immediate invention of a new policy.
