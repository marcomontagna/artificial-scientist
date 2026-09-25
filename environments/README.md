# Environments

The executable smoke environment is `artificial_scientist/environment.py`: two actions, binary observations, one evaluator-owned probability switch. Each step costs one observation. Actions are passive uniform random choices in the runner; all predictors receive the same actions and outcomes. Change time and law vectors are visible to the evaluator only, not passed to learner methods. Use a stationary configuration with equal before/after vectors as a control.

Future environments must specify interventions, observables, latent laws, observation noise, identifiability assumptions, termination and budget. Avoid giving a learner privileged latent coordinates unless this is an explicitly labeled condition. Do not mistake this binary toy for a causal discovery benchmark.
