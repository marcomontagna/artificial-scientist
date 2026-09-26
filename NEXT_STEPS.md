# Next step: understand a guided-search failure

The observation-guided proposer is implemented. It links recorded prediction failures to a shortlist of local formula changes and then to actual experiment choices. [Results](research/guided_proposal_result.md) · [Replay](results/guided_v1/replay.html). All runs are finished.

Guided search uses fewer candidate fits and improves the simple-world check, but roughly doubles error on the harder world. Keep it opt-in; enumeration remains the default. This is a meaningful selective-search mechanism, not proof that copying human reasoning is better.

Inspect why the useful motion/input approximation appears only after action 39 in the harder-world trace. Incumbent changes, sparse one-tick evidence, permanent exclusions and the limited representation are hypotheses to examine, not diagnosed causes. Review one concrete repair with Claude before further code or runs. Preserve both controls and all failures; no additional sweep or detached statistical study.

The goal remains an investigator that uses observations to build and test useful explanations. A new primitive, neural model or RL policy should solve a demonstrated limitation. No extra spending.
