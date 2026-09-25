# Baselines

Current smoke predictors: constant probability 0.5; per-action Beta(1,1) posterior mean over all observations; the same posterior mean using the most recent 20 observations of each action. The window is per action, not global time. No reset is triggered at the hidden switch.

These are known controls, not new methods. An eventual active learner also needs random/passive action policies, matched budgets, a suitable change-adaptive method, stationary controls and component ablations. Select hyperparameters on development runs only. Distinguish action selection from prediction quality.
