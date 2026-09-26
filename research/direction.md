# Direction: investigate an unfamiliar world

The goal is an artificial scientist that uses experiments to improve its understanding. It should enter a world without its governing equations, maintain competing explanations, choose what to try, predict outcomes, learn from failures, and express useful regularities as inspectable models or formulas.

The user's “Move 37” ambition means finding a useful experiment or explanation that we did not script as the solution. It is an aspiration. Surprise becomes interesting when it yields reproducible predictive or practical benefit on fresh interventions; rarity or a compelling story is insufficient.

## What we supply

A sensor/action interface, memory, a model-building language, search and planning machinery, an investigation objective, and finite budgets. Tools alone cannot supply those. Cartesian coordinates, time, mathematical primitives, noise assumptions and reset privileges are explicit inductive assumptions. We do not give the learner a finite catalogue of complete correct world rules.

## First system

A persistent 2D laboratory with one movable object. Observe noisy positions; push, wait and reset through the permitted interface. Infer temporal regularities, compose candidate predictive programs, and choose experiments that distinguish useful explanations. Preserve uncertainty and admit when the toolbox cannot explain observations. [Concrete first design](tool_lab.md).

Understanding is primary. A later target-reaching task can test whether a learned explanation enables useful planning, without making winning the definition of intelligence. Multiple universes and transfer remain the destination, after one coherent loop works.

## Focus

Known components are welcome. We do not need to invent regression or establish paper-level novelty before building the prototype. Any later novelty claim must face the [closest prior work](references.md) and serious alternatives. The previous disconnected statistical exercises are [retired](../archive/README.md); their failures remain evidence, not the active roadmap.

Current status: the first laboratory loop is implemented and its bounded demonstration is complete; see the [results](tool_lab_result.md). Experiment choice remains a demonstrated limitation. No promised AGI, universal discovery or guaranteed breakthrough.
