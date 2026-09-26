# Claude Opus 5.5 — follow-up C result critique

Verbatim review of supplied figures, without tools.

**Critique of the Study C interpretation (no tools used; raw numerical audit still pending, so all of this is provisional)**

**Headline correction.** "The gain persists" is true but credits the wrong component. On world a, `history_active` beats `ordinary_active` by 71.4% and wins 3/3 pairs. But `history_random` does better still: mean 0.0101, and two seeds near 0.001. `history_coverage` is also better in 2 of 3 seeds. So the persistent gain comes from the **history vocabulary**, not from investigation. Relative to random, the active loop adds negative value on both worlds. A defensible headline: *"History representation transfers to independently authored worlds; the active loop under-uses it, and its warnings miss partial explanations."*

**The strongest finding you underplay.** On world a, the history reference fitted on the active runs' own data reaches about 0.00066. The active data therefore contained the own-lag-3 signal, yet all three learners stopped at `v+u+lag(other_u,6)`. For world a this makes the bottleneck **model construction and revision**, not acquisition. Your 4-term vs 3-term point supports this. For seeds 2 and 3 the reference did not need the 8-term cap, so its advantage there is not just capacity.

**Counterarguments to anticipate**

1. **The primary baseline is weak.** `ordinary` has no lag terms, so any lag-capable fitter would pass the ≥20% criterion. The criterion shows representation adequacy, not scientific behaviour.
2. **The worlds were chosen to fit the tool.** They were capability-aligned and source-separated, not blind. World a lies inside the runtime vocabulary, so success there is recovery within a supplied basis. You already avoid claiming causal discovery or formula recovery; keep it that way.
3. **n = 3 with heavy tails.** The coverage seed at 0.1097 and the world b active seed at 0.1346 dominate the means. Report medians or per-seed results next to the means.
4. **The world b status screen is nearly vacuous.** When every run is poor, "3/3 poor flagged" is easy. Ordinary also flags 3/3. Random raises a false alarm, and coverage has one poor run left unflagged.
5. **The warnings measure gross misfit, not incompleteness.** The two unflagged poor runs on world a are exactly the cases where a partial explanation fits well in-sample. That is the failure mode that matters most for a scientist.
6. **Acquisition does matter in one place.** Coverage data sometimes defeats even the reference (reference MSE 0.048 on a, 0.032 on b). So "acquisition is irrelevant" would be an overcorrection.

**Recommended next direction (tomorrow, no new study)**

1. **Trace diagnosis, no fits.** For each world a active run, record the cycle where `lag(u,3)` first became estimable from the collected data. Then check whether it was proposed, how it scored, and why it was rejected: term cap, penalty, search order, validation split, or adoption threshold. Classify each wasted revision opportunity.
2. **Smallest loop change, guided by (1).** Make revision residual-driven. After fitting, the agent checks whether residuals correlate with lagged inputs or outputs it has already observed. Those correlations then become both:
   - candidate terms for revision, and
   - the "unresolved" warning, so the warning reflects missing structure rather than raw MSE.

   This is the observation→explanation→revision step the user wants, and it tackles the warning failure directly.
3. **Baselines inside the same loop.** Run the audited sparse history fitter as the strong construction baseline on identical data. Keep matched-budget random acquisition as the comparison for any active-acquisition claim. Active acquisition only needs justifying once construction stops wasting the data.

**Do not** promote a default, tune gates, or claim that active acquisition helps. State that the three studies (96 runs) show history representation transfers, while the agent's revision and warning behaviour is not yet trustworthy.

This critique is my own artifact, so another agent should review it.
