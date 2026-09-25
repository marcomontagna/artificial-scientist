# Multiple universes v0: benchmark calibration

Status: independently reviewed by distinct Codex research_critic; accepted for baseline-only implementation. No new method or novelty claim. This stage validates reusable environments and known prediction baselines; it cannot establish the main adaptive-state hypothesis.

## Worlds and information
Generate binary sequences of 1,200 observations, initialized with five hidden fair bits. Ticks are zero-based: observations 0–599 use the initial rule; observation 600 is the first changed sample. Before evaluator-only tick 600, the target is the latest bit and is returned with probability 0.8 (otherwise flipped). After that tick choose a condition:
- stable: unchanged;
- parameter: latest bit, match probability 0.2;
- noise: latest bit, match probability 0.5;
- structural: latest bit XOR the bit k positions back, match probability 0.8; sample k uniformly from 2..5 with an independent law RNG.

Draw one noise-uniform stream per seed and reuse across conditions for pairing. All learners in a condition see exactly the same outcomes. A learner receives neither condition, k, change time nor hidden initialization. It predicts the next bit from its observed history, then sees and learns that bit. Use a missing-history sentinel initially. Because 0.2 flip probability gives every finite history positive probability, histories with the same latest bit and different kth bit have distinct conditional distributions in structural worlds. Latest-bit state is therefore insufficient. This is a deliberately supplied finite family of sequence rules, not discovered physics or arbitrary universes.

## Known baselines
Compare discounted Beta(1,1) context predictors of order 1 and 5, and a fixed-share mixture of order 1..5 predictors. Beta(1,1) pseudocounts stay fixed; only accumulated data counts decay. Every tick discounts each stored success/failure count by 0.99, then adds the observed outcome to the prior context. Predict using counts before that update. Each component uses the last K observed bits, with sentinel padding. Mixture prior is uniform; update weights using each component's pre-update Bernoulli likelihood and then apply share 0.01 toward uniform for the next tick. This is a simple known-expert switching comparator, not a faithful reproduction of a named context-tree algorithm or a proposed new adaptive learner.

All models receive the same observation budget and fixed untuned settings. Count both successes/failures and all context-key entries for every stored context, allocated history capacity and mixture weights; count all mixture components, including unselected models. These are logical storage counts, not measured bytes or runtime. No claim of efficiency from mixture selection.

## Evaluation and stop gate
Development seeds 0..4 only. Seeds 1000..1049 are reserved for later held-out evaluation and must not run now. These are held-out instances within the supplied rule family, not unseen rule families. Report per-seed/per-condition pre/post mean log loss (nats), Brier and mean logical state size, plus predictions, config and revision metadata. Five development seeds provide descriptive plumbing evidence only: no significance, calibration, novelty or superiority claim.

The benchmark gate passes only if deterministic replay, exact switch semantics, predict-before-update scoring, hidden-metadata isolation by interface, structural-state insufficiency, mixture normalization and artifact scope/overwrite checks pass. Publish every condition regardless of outcome. Negative or equal baseline results are acceptable. Before a scientific comparison, audit model-order-selection prior art, add strong adaptive and recurrent comparators, specify the candidate trigger/state revision mechanism, preregister an accuracy/resource criterion, tune only on development worlds and independently review the revised protocol. Active acquisition and across-world transfer remain later stages.

## Execution limits
Standard-library Python; no dependencies or paid services. One run, under 10 minutes, under 2 GB memory/500 MB outputs. Preserve existing smoke code/results. Reviewer must accept this protocol before implementation and independently review code before the development run. Store output in a fresh results/runs/state_revision_v0_* directory; no overwrites.
