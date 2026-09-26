**Short answer: yes, you are missing something more basic, you are slightly overstating progress, and the proposed milestone risks being scripted.**

**The more fundamental issue: active choice is not yet shown to matter**
- Random sampling on the simple world (.000262) matches guided (.000288) and partial-guided (.000263).
- Coverage beats every variant on the harder world (.0213 vs .0265–.0538).
- Final coefficients are nearly identical across variants, and a full-history refit reproduces them. So the proposal tweaks barely change the model. What differs is which rows get collected.
- With one seed, the harder-world gaps (about 2×) could be noise.

That is why it feels circular. Each change was judged on the same single-seed evaluator, without a success criterion set in advance. Those numbers cannot tell you whether anything worked. "Connected investigator" is real *integration* progress. It is not yet evidence that choosing experiments beats trivial strategies. I would put it in the report exactly that way.

**Your diagnosis is right about:**
- Proposal micro-tuning is drift away from the goal.
- The capacity ceiling is a known, provable limit.
- Attributing the numerical error to fewer training rows is unproven.

**Where your milestone risks being scripted**
"Investigate a declared symmetry/independent-axis assumption" names the exact assumption the developer knows the challenge breaks. If the toolbox offers only the relaxations the challenge needs, the answer is encoded.

Mitigations:
- Predeclare a *generic* menu of relaxations: per-axis coefficients, cross-axis terms, state/velocity-dependent terms, higher-order terms, heteroscedastic noise.
- Apply it identically across several hidden worlds.
- Include a **null world** where the symmetric model is correct. Relaxing there counts as a false discovery.
- Include a world broken in a way the menu *cannot* fix. The agent should report "unexplained" rather than overfit.

**ONE milestone: residual-triggered model-class revision with discriminating experiments**

Across at least 4 hidden worlds (null, asymmetry/coupling, drag, one unfixable) and at least 5 seeds each, with a fixed action budget, the agent must:
1. Flag structured residuals from its *own* intervention data. It may use only runtime observations.
2. Choose experiments that discriminate among competing relaxations, and log the predicted information gain for each choice.
3. Adopt a relaxation only when it improves prediction on fresh held-out interventions. Otherwise keep the model, or report the failure.

**Pass criteria (set before running):**
- Better held-out MSE than the unchanged learner and than ordinary vector regression given the same data.
- Better held-out MSE than random and coverage sampling feeding the same revision logic. This is the test that the *experiment choice* matters.
- No relaxation adopted in the null world.
- An honest "unexplained" in the unfixable world.

If the vector-regression baseline wins, that is useful information too: the symbolic layer isn't earning its keep yet.

This closes the loop you actually want: failure → hypothesis about which assumption is wrong → targeted experiment → revised representation → better independent prediction. It also blocks both hand-adding the formula and further shortlist tuning.
