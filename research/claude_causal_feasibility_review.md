# Review: causal feasibility v0 (spec, code, tests)

**Verdict: approve running the deterministic population calculation, provided the non-blocking fixes below are made or disclosed.** Revise before `SequentialDiagnostic` is described as validated or reused in the finite-sample protocol.

## Mathematical design

I checked the design by hand and it is sound.

- **Worlds:** `confounded_world` (`causal_feasibility.py:49-65`) correctly marginalises U. It also correctly drops the intervened variable's structural equation.
- **Projection:** For a fixed DAG with hard interventions, weighted KL splits into a separate Bernoulli fit per node and parent state. `fit_graph` (`:87-107`) pools the non-intervened regimes, which gives the exact minimiser, so `project_world` finds the global minimum for each graph. Using 0.5 for zero-mass rows is harmless.
- **Expected zero/positive pattern:** It follows from a short argument that does not depend on the author's expectations:
  - Passive data, e=0.5 and the fork world can each be fitted exactly by some DAG.
  - With pair-only interventions, every regime looks like three independent fair bits, so the empty DAG fits exactly. The negative control is correct.
  - With all six interventions, do(X2) shows X0 and X1 correlated, while do(X0) and do(X1) show the other two variables as independent fair bits. I checked every DAG orientation, including X2 as a common parent, and none can produce both. Separation is positive for e<0.5. Passive-plus-pair fails for the same reason.
- **Sequential statistic:** The argument in spec lines 28-30 holds. The per-regime Dirichlet(1/2) predictions use the correct support sizes (8 passive, 4 per intervention). The null supremum is attained because the CPTs form a closed set and the per-graph MLE is exact. E_n ≤ Q_n/L_n(m0) for every null model, and the independent fair model rules out a zero denominator.

## Substantive issues

1. **Tests cannot catch overstated separation** (`tests/test_causal_feasibility.py:30-52`). The positive checks only require KL > 1e-8. A fitting bug that returned worse CPTs would inflate KL and still pass. The MLE tests cover only saturated passive data and one root intervention, never pooling across regimes.
   - **Fix:** For one graph and mixture (e.g. X0→X1 under `privileged_passive_pair`), assert that the fitted KL is ≤ KL at perturbed or grid-searched CPTs. Also add one closed-form case that pools across regimes.
2. **The adaptive-history test is mostly vacuous** (`tests:75-102`). After three steps, E_n is far below 2, so `crossed ≤ .5` cannot fail. `mean_e ≤ 1` follows from the pointwise check. The one meaningful assertion is `value ≤ ratio` (line 87), which catches an underestimated null supremum. This checks arithmetic, not false-alarm behaviour, which spec line 32 already concedes.
   - **Fix:** Add a mutation-style check that a broken statistic fails, e.g. excluding the true graph from the maximum or scoring after updating. Otherwise, stop calling these "crossing probability" checks.
3. **`best_graph` is an arbitrary tie-break** (`causal_feasibility.py:184,192`). Zero-separation cases have many exact fits (X0→X1, X1→X0, supersets). Saving the first index invites reading it as a recovered structure.
   - **Fix:** Save every graph within tolerance of the minimum, or label the field as an arbitrary representative.
4. **The term "identifiability" is wrong** (spec lines 22 and 24; gate `meaning`, `:208`). The calculation tests whether the world can be *distinguished from the null* under a given mixture. It does not identify a graph or a confounder. Spec line 24 says this correctly; the labels should match.
5. **Provenance at run time** (`:232`). All three files are untracked, so `revision` will not contain the code and `dirty=True`. Hashes cover these three files but not `run.py` or `__init__`, and nothing records that the tests passed.
   - **Fix:** Commit first, or hash the full package and record the test command and its result.
6. **Minor points:**
   - The 60 s limit (`:224-226`) is checked after the run finishes, not enforced; this is harmless at this size.
   - Copying tracked outputs to `results/causal_feasibility_v0` (spec line 36) is a manual step not in the code.
   - `allow_nan=False` (`:231`) would crash rather than save if any KL became infinite. Mathematically this should not happen.
   - Spec line 21's reason ("without observing an unmanipulated pair") is loosely worded. The actual reason is that every regime's unmanipulated variables are independent.

## Statistical interpretation and whether a simpler approach is warranted

- **The outcome is known in advance.** The zero/positive pattern follows from the argument above. It is standard material: compare P(X1|X0) with P(X1|do(X0)), or intervene on a third variable. Running the calculation is justified as a code check for the next stage, not as a finding.
- **Record the analytic derivation.** A simpler, more reliable approach is to write this derivation into the spec and treat the run as confirming the code against it.
- **The KL values are not power evidence.** They are per-sample growth rates for fixed mixtures. `research_reset.md` §Corrections 2 already forbids converting them into detection times, and that should hold here.
- **Expect low power later.** The Dirichlet alternative is saturated per regime (`:151-155`), with 25 free parameters and no sharing across regimes. That costs roughly (d/2)·log n in regret. A mixture over DAGs plus one latent common cause would probably be much more powerful. That belongs in the finite-sample protocol, not this version.

## Remaining limitations

- Only three binary variables, one form of confounder and fixed mixtures.
- Perfect hard interventions and stationary mechanisms are assumed.
- Rejecting the null means incompatibility with acyclic, latent-free DAGs. It could equally come from cycles, imperfect interventions or non-stationarity, not only hidden confounding.
- There is no finite-sample, adaptive-policy, power or novelty evidence.
- The literature overlap (universal inference, active model discrepancy, Model Discovery Agent) remains.

## Public description

It overstates the current state.

- **"Learns … by making predictions, choosing experiments and revising its assumptions"** describes a future system. No agent in this thread chooses experiments or revises causal models. The earlier work was passive context selection, now frozen.
- **"Whether interventions can reveal that *its* assumed causal model is incompatible"** implies an agent. The actual next step is an evaluator-side calculation with fixed, partly privileged mixtures and no learner.
- **"Novelty is still being assessed"** is honest but understated. The reset already documents substantial overlap and explicitly makes no novelty claim.

Suggested wording:

> "An open-source research project toward a small artificial scientist for simulated worlds. The current step is a deterministic check, in tiny three-variable worlds, that selected interventions (but not passive observation) make a hidden common cause detectably incompatible with a no-hidden-cause causal model. No learning agent is involved yet; the idea overlaps substantially with prior work and we make no novelty claim."

The repository has a `LICENSE` file, so "open-source" is fine.
