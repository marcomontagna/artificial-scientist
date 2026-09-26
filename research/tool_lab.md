# First tool-based laboratory

**Design, not an implemented agent.** Deliver one complete investigation trace before expanding the system. The first demonstrator is one object in 2D, not a suite of paper-style component studies.

## Boundary and tools

The learner receives timestamped noisy Cartesian positions and the public tool contract. It gets no velocity sensor, forces, masses, coefficients, world identity, change times, hidden state or simulator source. Predictive programs receive observed action history and elapsed time alongside position history. They may construct temporal features from those records. Define multi-tick wait and push-sequence predictions using only these public inputs and the candidate model itself; no simulator rollout may supply hidden dynamics. Keep hidden dynamics/evaluator code separate from learner imports; test that boundary. Candidate programs run through a restricted interpreter with no filesystem/network/host-code access.

| Tool | Public effect | Prototype cost |
|---|---|---:|
| observe | Advance one tick and return one position reading | 1 |
| push(angle, magnitude) | Apply bounded input (magnitude 0–1), advance one tick, return position | 1 |
| wait(k) | Advance 1–8 ticks; return the final position | k |
| reset | Return object to its fixed home state; retain agent memory and hidden law; return position | 8 |

All clocks/costs are recorded; sensor noise is not rewound by reset. A fixed home state is a supplied privilege, not a discovered ability. Count resets, observations and unsuccessful actions. First-demo engineering caps: 80 cost units, 120 CPU-seconds and 10 MB of trace data. Stop with an explicit incomplete/unexplained status if a cap is reached.

## The learner

Maintain an append-only action/outcome notebook and up to 8 competing executable models. A bounded search composes arithmetic, fitted constants, temporal differences/lags, absolute value and simple conditions; it does not look up a complete law by world label. Begin with small expressions; cap expression size at 12 nodes and search within the total CPU budget. The implementation must publish the exact primitive semantics, tie rules and constant-fitting method before execution. Failure to find a model does not authorize unbounded search or a hidden-law hint.

Rank candidates using prediction errors recorded before outcomes, a complexity cost, and an explicitly estimated sensor-noise component. New proposals need fresh predictive evidence; do not label in-sample fit as validation or heuristic weights as calibrated probabilities. Coefficients may be updated from observations, with every change logged.

Choose among legal short action sequences by predicted disagreement beyond estimated observation noise, divided by their tool cost, with a small declared coverage component to avoid a committee's shared blind spots. This is a starting engineering heuristic, not a novel algorithm or a guarantee of information gain. Freeze predictions and scores before execution. Pure noise should not attract endless investigation. Separate measurement uncertainty from model error where observations permit; otherwise explicitly mark them as unresolved. Do not automatically reclassify unexplained dynamics as noise and suppress further investigation.

## The visible loop

Observe → propose explanations → predict a discriminating experiment → execute tools → compare prediction with observation → retain/revise explanations. The replay must show actual actions, alternative predictions, model edits, failures, and the scores used to choose an action. Do not invent an after-the-fact rationale. Start with a readable event trace; a small HTML replay follows once the trace is correct.

## When the first demonstrator is complete

The learner must choose actions from its own acquired models and produce a fresh-intervention prediction before seeing the outcome. A separate evaluator checks independent interventions at equal costs; compare the same learner with random actions and a simple direction/magnitude coverage policy. Include a simple predictive reference where useful. Report failed predictions and limited identifiability; no scripted success path or aggregate-score-only demo.

Have a different agent define the hidden dynamics/challenge and commit them before learner tuning. This reduces co-design; it is not formal blinding when the coordinator can inspect the repository. Keep a correctable development world, then one independent challenge and a noise check only after the loop runs. Threshold friction, different surfaces, delay, multiple objects and law changes are candidates for later capability checks, not an immediate five-world benchmark or a list of answers exposed to the learner.

A candidate “Move 37” moment needs a reproducible benefit: an experiment exposes a regularity or distinguishes explanations, improves independent predictions/planning, and was not scripted as the solution. Low action frequency, committee collapse or human surprise alone cannot establish it. Claims apply to the tested simulator and supplied toolbox.
