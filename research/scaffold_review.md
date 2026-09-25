# Independent scaffold review

Reviewed 2026-09-25 by a separate Codex subagent. This is not a Claude Code review. Scope: repository scaffold, executable Python, tests, tracked smoke artifacts, research brief, coordination instructions, README, and initial results. No code was edited by this reviewer.

## Outcome

No blocking correctness defect found in the supplied smoke experiment. All seven unit tests passed under the available Python. Independently rerunning `simulate` reproduced every recorded prediction row and the complete seed-level summary exactly; the rounded aggregate values in RESULTS.md also match. Scoring precedes updates, all baselines receive paired observations, and hidden change metadata does not enter learner methods. Existing-output protection and repository output scope are covered by passing tests.

The README and results correctly call this a plumbing check, make no novelty or AGI claim, and disclose that active experimentation, causal discovery, calibration diagnostics, and learned representations remain unimplemented. The baseline documentation correctly identifies the forgetting window as per-action rather than global time.

## Required documentation follow-up

The user's latest instruction requires another agent to review anything created. At the time of this review, AGENTS.md did not impose a general review gate; the Hermes prompt requested Claude review after implementation but allowed progress when that agent was unavailable. Require a distinct available agent to review new code and substantive artifacts, record reviewer identity and findings, and label unreviewed work as draft. A second Codex agent is an honest substitute for independent review when Claude is unavailable; never label that review Claude's. The parent was notified before publication of this review.

## Limitations and future work

- The five seeds, known switching probabilities, and fixed window are development smoke settings. They cannot establish a general adaptation advantage or a novel research gap.
- Log loss is clipped at 1e-12 as documented; it is a finite numerical approximation at endpoint probabilities.
- Runtime metadata records a dirty working tree and a local revision that may differ from browser publication. Exact artifact reproduction was independently verified, but future research runs should preserve a clean source revision or source snapshot/hash as well as the config hash.
- The runner is intentionally small and holds predictions in memory. Respect the documented resource cap; do not scale its configuration without considering memory and runtime.
- GitHub publication, authentication, actual Hermes/Claude availability, automation delivery, and Notion page contents were outside this file review. No claim that overnight agents ran or that tomorrow's report is scheduled follows from these checks.

## Verification performed

`python3 -m unittest discover -s tests -v` — 7 passed.

A separate read-only Python check compared fresh simulation output to all stored CSV fields and the complete summary JSON, then independently aggregated the metrics printed in RESULTS.md — passed.

## Follow-up review: review gate and Notion setup report

The new mandatory independent-review sections in AGENTS.md, CLAUDE.md, HERMES_OVERNIGHT_PROMPT.md and research/overnight_brief.md were inspected and resolve the required documentation finding above. They cover code, notes, prompts and reports; require a distinct reviewer; distinguish Codex from Claude; retain draft status without review; and require review of substantive fixes. The latest coordination entry honestly records the active Codex researcher/reviewer and says Hermes/Claude have not launched. The ledger's opening status should be aligned with that latest entry.

Read-only inspection of the Notion activity page confirmed its smoke metrics match the independently reproduced artifacts. Its initial setup account is historical and now needs a dated update for the Codex review and first-phase research. Publication completion must follow verified remote evidence. The Next step property should distinguish the optional Hermes handoff from the current Codex-managed work. A scheduled-report claim requires confirmed automation, and the working agreement should include the user's latest zero-additional-spending constraint. These corrections were sent to the director; this review does not certify a future Notion update before it exists.

## Independent first-phase literature review

Reviewed research/prior_art.md and research/search_log.md after the separate research worker completed them. No blocking claim defect found. This was a limited substantive review, not an independent reconstruction of every search query or audit of all twelve bibliography records.

Opened and checked the four closest primary texts: [BOCPD](https://arxiv.org/html/0710.3742v1), [Deep Adaptive Design](https://proceedings.mlr.press/v139/foster21a/foster21a.pdf), [Adaptive Conformal Inference](https://arxiv.org/pdf/2106.00170), and [causal intervention design](https://arxiv.org/html/2209.04744v2). The map accurately reports BOCPD's within-segment independence assumptions and run-length uncertainty; DAD's 30-design location-finding setup and listed controls; ACI's distinction between long-run and per-step coverage; and the causal intervention paper's main known-DAG/unknown-weight setting.

The proposed direction is explicitly a candidate question, not an established gap. The report correctly identifies active change detection, controlled sensing, dual control, nonstationary bandits, and recent literature as missing coverage that blocks novelty claims. The uncertain 2026 source is quarantined, not used to support a result. This evidence is sufficient for a bounded first-phase map; it does not yet justify selecting a novel method or declaring the entire overnight mission complete.

## Bounded handoff and cost review

Reviewed HERMES_HANDOFF.md and the explicit zero-additional-spending clauses in the agent instructions, master prompt and overnight brief. The handoff requests acknowledgment rather than asserting receipt, limits work to one focused critique, assigns exclusive files, preserves Codex ownership of publication/Notion, and requires honest agent attribution and separate review. It forbids additional charges and paid fallback, and stops external delegation when billing status is unclear. No blocking issue found. The director confirmed successful creation of the dated report automation; this reviewer did not independently inspect the scheduling tool response. Hermes/Claude participation remains user-reported until repository evidence confirms it.
