# Project direction — September 25, 2026

## Destination
Build a small artificial scientist that enters an unfamiliar system, explores the effects of its actions, forms competing explanations, predicts with uncertainty, chooses informative experiments, and revises inadequate explanations. **Understanding is the primary objective; winning or an external reward is optional.** This is an aspiration, not demonstrated autonomy or an AGI claim.

The user's chess example means learning through interaction without being handed the game rules, piece semantics or an opponent model. The environment enforces what can happen; attempted actions and outcomes provide evidence. In a simulated universe, the same loop should discover useful regularities without a win/lose condition. A sensor/action interface and learning machinery must still be supplied; this is not learning from literally no assumptions.

Measure understanding through prediction on independent experiments, calibrated uncertainty, efficient acquisition of informative evidence, and models that remain useful across new settings. Raw surprise is not sufficient: irreducible noise must not become the exploration objective. Different models may fit all available evidence, so preserve uncertainty rather than claim a unique discovered law.

An optional task objective can later use the learned model for planning, including winning a game. That is distinct from the core scientific objective. In simulations, discoveries can include non-obvious consequences of the implemented rules; claims about the real universe require independent real-world evidence.

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

The completed [research pass](research_reset.md) provisionally selects detecting wrong causal assumptions through chosen interventions, starting with mathematical and small-world feasibility. That [population check](causal_feasibility_result.md) now passes. The [finite-sample diagnostic check](causal_diagnostic_result.md) is now complete: its strong-case gate passes but the mismatched-family stress case fails. It is one component study, not the project destination. The [interactive switch laboratory](interactive_lab_result.md) now implements that loop: experiment choice, observation, Bayesian updating and independent-query evaluation. It improves the primary supplied-library comparison but loses on the pure-noise control; the flexible fallback is supplied, not invented. Next assess a small stateful world and whether multi-step planning/intrinsic-reward RL is needed. Do not continue an open-ended chain of isolated diagnostic studies. No candidate is novelty-cleared. Multiple universes remain central. New methods need a precise unresolved difference and independent review before implementation; a negative novelty decision is acceptable.

The earlier EPIG/EIG protocol is retained as optional replication groundwork, not the current implementation target. The development benchmark now includes adaptive context selectors and balanced structural-lag cases. Its full shadow bank is present from the start; it does not demonstrate lower total memory, invented features or scientific novelty.

## Working agreement
Codex coordinates the protocol and implementation; Claude is the intended independent critic when available. A distinct Codex reviewer can substitute, identified honestly. Every substantive artifact receives another agent's review. Keep reports short, work inside this repo, use existing access only, and incur no additional spending. Stop at usage limits; never enable paid fallback.

## Close reference points

[MuZero](https://arxiv.org/abs/1911.08265) learns models used for reward/value-guided planning; [DreamerV3](https://arxiv.org/abs/2301.04104) learns world models and behavior through imagined outcomes. These establish substantial overlap with the broad learn-through-interaction vision. They do not establish that our implementation discovers rules, chooses informative experiments or transfers to arbitrary worlds. Here the primary goal is improved understanding; a defensible contribution still needs a narrow comparison with existing discovery/experimental-design methods. Primary abstracts checked September25,2026; no comprehensive new literature review is claimed.
