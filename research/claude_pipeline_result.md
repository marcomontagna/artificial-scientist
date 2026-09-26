I've finished reading the files and am writing up the critique.

# Independent critique: same-equation pipeline v0

**Bottom line:** the pipeline runs correctly, but the screen it passed could barely fail. The data point to inefficient inference as the bottleneck, not where challenge points are placed. I don't think the proposed next experiment is the strongest one.

## 1. The screen passing tells you little
- **False terms:** confirmation uses a split likelihood-ratio e-value ("universal inference") with threshold 120 (`equation_pipeline.py:98`). That bound is known to be very conservative, so 0/60 false confirmations is what you'd expect. The ≤6/60 guard was close to impossible to trip.
- **Strong recall:** strong coefficients were 10× the weak ones, and recall came out at 100%.
- **Conclusion:** "screen passes" shows the plumbing works and nothing more. The report half-says this; it should say it outright.

## 2. The report's weak-term table leaves out an important comparison
In weak_quadratic, **fixed_full** (all six terms fitted on 48 observations, no selection) did better than selected_refit:

| weak_quadratic | selected_refit | fixed_full |
|---|---:|---:|
| True terms confirmed | 45/115 | 56/115 |
| C MSE | 0.0137 | 0.0093 |
| Extrapolation MSE | 0.021 | 0.014 |

In weak_affine, selected_refit won on recall (88 vs 60/180). Fixed_full also has a valid whole-form test. So the report should compare selected_refit against fixed_full, not only pooled BIC. Stating the result only relative to pooled BIC makes selected_refit look like "valid but slightly worse", when against the other valid option it wins one family and loses the other.

A smaller point: the summary has two recall numbers, a per-dataset mean of 0.439 and a pooled 45/115 = 0.391. The report should say which one it uses.

## 3. Where recall is actually lost
- In weak_quadratic, selected_refit picks 85.6% of true terms, but only 47% of those selected terms get confirmed. The loss happens in the C test, not in selection.
- Two things drive it:
  - the conservative e-value; and
  - the fact that the e-value's numerator is the frozen B fit, made on [-1,1]², then evaluated on C in [-2,2]². Coefficient error gets amplified when extrapolating, which inflates the candidate's error and pushes evidence down.
- So C is doing two jobs that pull against each other: the wide domain helps the adequacy check and hurts term confirmation.
- The better tool is already available. With known σ and a stated full-family null, an exact z/χ² test of each β_j on held-out data is valid under the same assumptions and much more powerful. Universal inference is meant for cases where no tractable null distribution exists; this isn't one.

## 4. The extra split may not be needed
With Gaussian noise and known σ, data fission/thinning (Rasines & Young; Leiner et al. 2023) turns y into y+τZ and y−Z/τ, which are independent. Selection and inference can then each use all 64 points and keep independence. This goes straight at the cost the report found ("pooled BIC … better"). It's a known method, and it should be tried before building on 24/24/16 splits.

## 5. Adequacy calibration
- The Q derivation is right: conditional on A and the designs, r = ε_C − X_C(X_BᵀX_B)⁻¹X_Bᵀε_B, so Q ~ χ²₁₆ exactly.
- But the empirical rejection rates for sufficient supports are 6/60, 6/60, 5/60, 6/52 and 6/45, against 3 expected. Each alone is unremarkable, but all sit above nominal. Because they share noise, you can't treat them as independent confirmation either way.
- A KS/QQ comparison of the 60 fixed_full Q values against χ²₁₆ is cheap, and more informative than counting rejections. I'd check the covariance code against a simulation before building more on Q.

## 6. The "discovery" framing
- The learner picks a subset of six supplied monomials. Nothing new is discovered.
- The outside-family worlds (exp, cubic, sine on [-2,2]²) are rejected 60/60 because they are grossly non-quadratic. That's a sanity check, not evidence the check can spot subtle misspecification. The report says so; keep it.
- The erratum is handled properly: counts are kept and interval claims withdrawn.

## 7. Is the proposed next experiment warranted?
Not as the next step.
- **The outcome is mostly predictable.** For in-family omitted terms, optimal design theory already gives the answer: D-/T-optimal designs for quadratics on a square sit at corners, edge midpoints and the centre (Atkinson–Fedorov model discrimination). Beating random or space-filling points there would mainly rediscover that. If you do run it, the baseline must be the known optimal design, not only random/space-filling.
- **Validity is fragile.** Choosing C locations from A is fine. Letting B influence them would break the marginal χ² derivation, because β̂_B error becomes correlated with X_C. The protocol would need to state that restriction and test it.
- **It doesn't touch the demonstrated bottleneck,** which is inference efficiency (points 3–4).

## Recommended order
1. **Cheap fix:** swap in exact held-out coefficient tests, add the Q calibration diagnostic, and compare sample splitting against data fission, on fresh seeds.
2. **Then the real "discover and challenge" step:** a closed loop in which an adequacy rejection triggers a proposed extra primitive from a held-out or expandable grammar, re-tested on fresh data with explicit sequential error control (alpha-spending or e-value products). Use outside-family worlds of graded subtlety, e.g. cubic terms scaled down to the weak regime, rather than gross ones.

That tests whether the whole-form check makes the learner better, which is the claim this line of work needs. Active design is worth adding later, inside that loop, where the alternatives are genuinely unknown.
