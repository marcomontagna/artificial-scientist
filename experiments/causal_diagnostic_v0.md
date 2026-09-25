# Finite-sample causal diagnostic v0

September 25, 2026. Protocol fixed before sample generation; reviewed by Claude Opus 5.5; revised before implementation to address its blocking findings. Scope: compare two known sequential diagnostic numerators under fixed schedules, not invent an action policy or demonstrate novelty. Prior population distinguishability check and proof are in causal_feasibility_v0.md and research/research_reset.md.

## Question and fixed budget

Can the prespecified **structured-mixture** diagnostic detect strong excluded confounding with useful power by 400 samples? Saturated KT is the comparison, not an alternative primary selected after results. Alpha=0.05; both receive every identical action/outcome in an episode, with equal 400-sample budgets and no resets. All episodes continue to sample400 even after alarm, preserving first crossings and enabling comparison.

Two sampled schedules: independent uniform random over seven regimes; deterministic round-robin actions0..6 starting at0. Round-robin has58 passive observations and57 of each other action. Passive-only is an invariant unit check, not a sampled power/null cell: both numerators are mixtures of distributions contained in a saturated passive DAG model, so Q_n≤sup L_n and log E_n≤0 on every passive history. Schedules are unprivileged and see no world labels/hidden parameters. No pair-targeted or evaluator-informed schedule.

Use new development seeds200..399 (200 replications per world/schedule). All are inspected development data after this study, not a held-out confirmation. No reserved sequence seeds1000..1049. Snapshots100,200,400 are fixed in advance; final400 is primary.

## Fifteen world cells

Nine out-of-class worlds: all three variable pairs × noise e in {0.05,0.20,0.35}, using the existing symmetric hidden-fair-U generator and independent fair third variable. Keep weak cases regardless of results.

Five null controls: (1) independent fair roots; (2) independent biased roots with P1=(0.2,0.5,0.8); (3) fork X0→X1,X2 with root0.5 and independent flip noise0.2; (4) boundary fork with root0.5, X1=X0 and X2=1-X0; (5) a DAG sampled uniformly from the25 graphs for each seed, with each CPT probability independently uniform[0.1,0.9], fixed throughout its episode. Save every sampled graph/CPT, not merely its seed. These probe implementation, not all possible null distributions.

One additional out-of-numerator-family stress cell: biased common cause U~Bernoulli(0.2) for pair(0,1), noise0.05 on both, third independent fair. Its interventional table is summed explicitly. Do not use this cell to tune the numerator or gate.

Each world is stationary, interventions are perfect and correctly labeled, all three outcomes are observed. Rejection means failure of this joint assumption set, not a unique confounder diagnosis.

## Two normalized numerator distributions

**Structured mixture (primary):** 30 fixed candidate worlds = three pairs × e=(0.025+0.05k), k=0..9, with equal prior weights, hidden U fair and third variable fair. No true pair/noise/label is supplied to the diagnostic. Update component likelihoods only from the observed action/outcome and use stable log-sum-exp. This numerator deliberately supplies the same family form as the main benchmark; its grid excludes the tested true noise values. Any advantage is an informative-family-prior benefit, not discovered representation or general scientific reasoning. The biased-U stress cell lies outside this family.

**Saturated KT:** independent Dirichlet(1/2) predictive tables for each regime: eight outcomes passive, four feasible outcomes for each hard intervention. No pooling or model selection across regimes.

Q_n is the product of normalized predictions made BEFORE their outcomes. Both diagnostics share the same null denominator: exact maximum likelihood over all25 observed-only DAGs with unrestricted fixed CPTs. Optimize via pooled non-intervened counts. An incremental implementation caching12 node/parent-set scores is required, with equivalence tests against the previous exact helper, including intervened/deterministic cases. Floating-point arithmetic approximates the mathematical maximum; comparisons must agree within1e-9 on test histories. No clipping or reduced graph subset.

## Statistic, validity and numerical convention

log E_n = log Q_n - max_m log L_n(m). Record first alarm at log E_n >= log(20)+1e-9. The positive1e-9 guard is fixed and conservative; it is not a certified numerical error bound. The exact-arithmetic statistic is dominated under each fixed null by a likelihood-ratio supermartingale. Ville's inequality gives probability(any alarm)≤0.05 when the numerator is normalized, interventions are recorded correctly, mechanisms are fixed, and actions depend only on past information/model-independent randomization. Empirical false alarms do not prove this guarantee.

Only support-consistent observations are accepted. The independent fair null witnesses positive denominator on every valid finite history. Deterministic null paths of zero probability are never sampled. Preserve the existing support checks.

## Outcomes and decision rule

For each world/schedule/numerator, report200 independent seed replications, detections by100/200/400, and pointwise95% Wilson intervals. Let T=first crossing, infinite if no crossing. Save null for missing T in JSON, explicit censoring, and capped stopping time min(T,401), treating missing T as401. Report means of capped times over ALL200 seeds; do not substitute a median among detected cases. Preserve per-episode snapshot logE, maximum logE, first crossing and prequential numerator log loss. That prediction loss is on schedule-selected data and is only comparable between numerators on the same world/schedule, not a common query-risk measure.

The exploratory feasibility gate passes only if the PRIMARY structured-mixture lower Wilson power bound at400 is at least0.8 (at least172 detections out of200 with the fixed Wilson formula) for EACH of the three e=.05 pairs under BOTH random7 and roundrobin7. Do not replace the primary with KT after viewing results. This is a practical development screen, not simultaneous statistical confirmation. Show intermediate/weak/stress outcomes and KT even if the gate passes.

Null rates are descriptive implementation checks. If any null cell/numerator has an observed rate>0.10, hold the overall decision for a code/statistical audit; this debug threshold is neither an alternative alpha nor proof of validity. Keep all null rates and intervals. Pair/schedule/numerator results share seeds and are correlated; never pool them as independent trials. No claimed adaptive-policy advantage follows.

## Randomness, resource limits and artifacts

Independent standard-library Random streams: observation uniforms seed+1000003, random actions seed+2000003, random-null generation seed+3000003. Reuse observation uniform at the same tick across schedules/worlds for paired comparisons; each realized outcome is inverse-CDF sampled from its own regime table. This coupling preserves each marginal world law. The random-null draw for a seed is shared across schedules. No diagnostic receives generator streams or true tables.

A performance/correctness smoke uses seeds190..194 and two fixed cells (null_fair and pair01_e0.05), both schedules,400 steps:20 episodes/8000 observations. Preserve its outputs but use it only for correctness/resource decisions, with no effect-based tuning. Proceed only if1.25×(smoke elapsed/20)×6000≤350seconds; otherwise report a resource no-go without automatically changing study size. Record these seeds as inspected. Full run:6000 episodes,2.4million observations, two diagnostics. Loop seed-major, then world, then schedule, so completed seeds are balanced. One process, internal500s deadline, external540s kill,100MB output cap. Preserve partial evidence on limits; no automatic reduced study.

Before the full run: Claude reviews protocol; independent source/tests review; complete required tests and smoke; commit source/config/spec. Save config, all fixed/sampled world definitions, per-episode action/outcome strings sufficient for replay, both diagnostic records, aggregates/gate, source/config/artifact hashes, Git state, Python/platform and timing. New repo-scoped causal_diagnostic_* output directory only; preserve partial failure status. Keep larger traces ignored, track compact aggregate/provenance evidence. No downloads, dependencies, paid services or unrelated writes.

If the gate passes, independently design a later adaptive action comparison with a shared observation budget and compute accounting. If it fails, retain the result and assess the specific diagnostic/family assumptions; do not start tuning in this version.

## Predictions and interpretation fixed before sampling

Claude expects high structured-mixture power for e=.05, little power for e=.35, and limited/marginal power for e=.20; KT may be underpowered at400 because it does not share information across regimes. These are qualitative predictions, not finite-sample guarantees derived from KL rates. We expect the biased-U stress cell to expose the supplied-family numerator's weakness. Fair independent roots are a closer null to that numerator than biased-root controls. Report all outcomes even if these predictions fail.

The reviewed JSON fixes null/stress definitions, KT prior, Wilson constant, cap, stream offsets, smoke budget, external timeout and six primary gate cells. The null debugging trigger is strictly more than20 alarms out of200 in any one null cell/numerator. Primary completion requires exactly the declared6000 episodes; partial summaries cannot pass. Optional extra numerators/survival-threshold analyses from the review are deferred to avoid scope growth.

## Relationship to the user's goal

The destination is an agent entering an unfamiliar game or simulated universe, learning action constraints and predictive rules from interaction, forming/revising hypotheses, and improving understanding through calibrated predictions and informative experiments. Task goals such as winning are optional, not the primary objective. This diagnostic is one component: recognizing when an assumed model family is inadequate. It does not learn an action policy, discover a new representation, infer an opponent or autonomously acquire a goal. After this bounded run, prioritize a tiny interactive unknown-rule game prototype; do not turn this component into an open-ended sequence of statistical gates.
