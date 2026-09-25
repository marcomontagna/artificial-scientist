# Project direction — September 25, 2026

## Destination
Build a small artificial scientist that enters an unfamiliar system, observes, forms competing explanations, predicts with uncertainty, chooses informative experiments, and revises its model when evidence contradicts it. Understanding means reliable prediction, intervention outcomes, generalization and awareness of limits. This is an aspiration, not demonstrated autonomy or an AGI claim.

## Multiple universes are central
Use a procedural generator of small worlds with different hidden rules: stable motion, changed coefficients, delayed dependencies, hidden state and noise. Learners see observations and permitted actions, not world identities, equations or change times. Human-designed generators and learning machinery still impose assumptions.

Separate development worlds from held-out evaluation. Start with fresh learners in each world; later test transfer across worlds against fresh-start controls. Different seeds test variation within a family; held-out rule families test broader generalization. Neither alone establishes universal scientific discovery.

## First research question (candidate, not novelty-cleared)
Can a learner detect insufficient predictive state, expand it selectively, and recover accurate predictions with lower cumulative memory/compute or fewer observations than strong alternatives?

Demonstrate that the structural-change condition really requires additional predictive information. Include coefficient-only, no-change and noise controls. Compare minimal-state, always-large-state, expressive recurrent and appropriate adaptive/model-order-selection baselines. Fix observation streams initially and disclose data, tuning, capacity and compute budgets. Predefine the accuracy/resource tradeoff before evaluation. Adding memory is not automatically concept invention.

## Architecture remains open
A small neural network trained from scratch may learn representations and predictions; probabilistic or simpler mathematical models may work better for the first test. Compare alternatives. No pretrained LLM inside the initial experimental learner. Codex/Claude assist research and engineering. MLX is optional, never mandatory.

## Next gate and longer path
The initial prior-art audit and baseline protocol are complete; see state_revision_prior_art.md and ../RESULTS.md. Next specify and independently review a state-expansion candidate and stronger comparators before implementation and held-out evaluation. Active experiment choice, raw pixels, richer universes and visual planetary simulations are later stages, conditional on useful evidence.

The earlier EPIG/EIG protocol is retained as optional replication groundwork, not the current implementation target. The four-world development benchmark and offline replay now validate known baselines. No selective state-expansion learner or novelty claim has been demonstrated.

## Working agreement
Codex coordinates the protocol and implementation; Claude is the intended independent critic when available. A distinct Codex reviewer can substitute, identified honestly. Every substantive artifact receives another agent's review. Keep reports short, work inside this repo, use existing access only, and incur no additional spending. Stop at usage limits; never enable paid fallback.
