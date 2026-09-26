# Follow-up C evaluator-world specification

Private-to-reviewer numeric specification until all declared C outcomes exist. Author saw the frozen protocol and general grammar, not B learner results, traces or fitted models. Coefficients were chosen once before these simulator tests; no investigator or model fit was run. This is capability-aligned source separation, not formal blinding or sampling random physical laws. Root must not inspect this specification or numeric world source before all24outcomes.

## Inherited interface and provenance

`make_transfer_world(seed, variant)` accepts transfer_a/transfer_b. It inherits `lab_world._World` and public `lab_api` tools unchanged: frozen noisy tick/x/y observations; push/observe1, wait1–8, reset8; cap80. Every elapsed tick consumes sensor noise, including unobserved waits. Sigma=.01, fixed law and seeded noise. Cached initial is not a free repeated sample. Reset restores zero position, velocity and all pending-input memory but never rewinds global time/noise. Invalid or unaffordable commands fail before changing any state. World modules, labels and hidden buffers are evaluator-only.

Hash this module, its tests/contract, lab_world.py and lab_api.py. Independent reviewer checks them before sealing; no law adjustment after learner outcomes. Seeds alter noise only. Same-seed comparisons are paired, not independent laws. Only synthetic seed7 is used for tests.

## Numeric laws and representational capacity

Let v be velocity immediately before the current transition, u its bounded Cartesian input, and L_k u the input applied to the transition starting k ticks earlier. Position advances by new velocity. Both coordinates update simultaneously. Missing history is zero; reset clears it.

**transfer_a:**

```
vx' = .58 vx + .31 ux + .18 L3 ux + .25 L6 uy
vy' = .74 vy + .43 uy - .23 L3 uy + .17 L6 ux
```

Exactly four common feature expressions suffice: v, u, lag(u,3), lag(other_u,6), with separate axis coefficients. Delayed input terms cannot generically be absorbed into immediate input, previous input or instantaneous motion under arbitrary allowed action histories. This is latent-state expressibility: noisy finite-difference velocity is not an exact latent measurement.

**transfer_b:**

```
vx' = .54 vx + .16 vy + .27 ux + .24 L4 ux - .21 L9 uy
vy' = .61 vy - .12 vx + .34 uy - .19 L4 uy + .26 L9 ux
```

Five common expressions are required: v, other_v, u, lag(u,4), lag(other_u,9). All have nonzero substantial coefficients; no zero-filled extra term merely inflates the count. Current input and the two distinct lagged channels can vary independently, while earlier inputs vary the two velocity components. On reachable open sets, these five linear dependencies cannot be replaced by four of the declared primitive/abs/positive/product feature expressions: nonlinear products are not arbitrary sums of linear variables. The sparse eight-feature reference can represent the law. This is a structural statement over input histories, not a claim that every finite trace defeats all four-term approximations or that external MSE must exceed .01.

## Stability and evaluator exposure

For a, homogeneous velocity contraction in infinity norm is at most .74. For b, the two absolute momentum row sums are .70 and .73, hence at most .73. Bounded current and delayed inputs give bounded velocities; positions may drift in the unbounded plane, but remain finite over the80-unit budget. No law switches or hidden reward mechanisms occur.

The unchanged fourth evaluation sequence has nonzero pulses starting relative ticks0,5,10 and ends at tick16. Its first pulse (.8 at angle .61) has nonzero x/y components. For a, that pulse's delayed components enter transitions starting3 and6, visible by positions at relative ticks5 and10. For b they enter starting4 and9, visible at ticks5 and10. Later pulses also produce delayed effects before tick16. No delayed component is outside all evaluation horizons. This is an analytic timing check, not an oracle fit or a search for a passing performance regime. Existing external actions are not used to choose learner features, parameters or adoption decisions.

## Review and tests

Tests cover cached/noisy observations, same-seed repeatability, wait batching, full latent reset, invalid-command/budget atomicity, finite bounded-budget dynamics, simultaneous vector updates and lag indexing. They do not execute a learner, fit a model or score evaluation performance. Independent reviewer receives this numeric specification directly; coordinator receives only readiness and sealed hashes before completion. No commit before review and coordinator sealing.
