# Project direction — September 25, 2026

## Destination
Build a small artificial scientist that enters an unfamiliar system, observes, forms competing explanations, predicts with uncertainty, chooses informative experiments, and revises its model when evidence contradicts it. Understanding means reliable prediction, intervention outcomes, generalization and awareness of limits. This is an aspiration, not demonstrated autonomy or an AGI claim.

## Multiple universes are central
Use a procedural generator of small worlds with different hidden rules: stable motion, changed coefficients, delayed dependencies, hidden state and noise. Learners see observations and permitted actions, not world identities, equations or change times. Human-designed generators and learning machinery still impose assumptions.

Separate development worlds from held-out evaluation. Start with fresh learners in each world; later test transfer across worlds against fresh-start controls. Different seeds test variation within a family; held-out rule families test broader generalization. Neither alone establishes universal scientific discovery.

## Historical first question — now frozen
Can a learner detect insufficient predictive state, expand it selectively, and recover accurate predictions with lower cumulative memory/compute or fewer observations than strong alternatives?

Demonstrate that the structural-change condition really requires additional predictive information. Include coefficient-only, no-change and noise controls. Compare minimal-state, always-large-state, expressive recurrent and appropriate adaptive/model-order-selection baselines. Fix observation streams initially and disclose data, tuning, capacity and compute budgets. Predefine the accuracy/resource tradeoff before evaluation. Adding memory is not automatically concept invention.

## Architecture remains open
A small neural network trained from scratch may learn representations and predictions; probabilistic or simpler mathematical models may work better for the first test. Compare alternatives. No pretrained LLM inside the initial experimental learner. Codex/Claude assist research and engineering. MLX is optional, never mandatory.

## Next gate and longer path
The first two context selectors have run and are frozen after Claude’s review and Codex’s reproduction; see [the response](selector_review_response.md). They select supplied experts and do not choose experiments. Return-to-simple reproduction confirms contraction but no predictive benefit over the mixture. Do not build v3 or extend selector ablations without a separately justified question.

The completed [research pass](research_reset.md) provisionally selects detecting wrong causal assumptions through chosen interventions, starting with mathematical and small-world feasibility. No candidate is novelty-cleared. Multiple universes remain central. New methods need a precise unresolved difference and independent review before implementation; a negative novelty decision is acceptable.

The earlier EPIG/EIG protocol is retained as optional replication groundwork, not the current implementation target. The development benchmark now includes adaptive context selectors and balanced structural-lag cases. Its full shadow bank is present from the start; it does not demonstrate lower total memory, invented features or scientific novelty.

## Working agreement
Codex coordinates the protocol and implementation; Claude is the intended independent critic when available. A distinct Codex reviewer can substitute, identified honestly. Every substantive artifact receives another agent's review. Keep reports short, work inside this repo, use existing access only, and incur no additional spending. Stop at usage limits; never enable paid fallback.
