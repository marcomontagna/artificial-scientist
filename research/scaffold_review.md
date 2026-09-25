# Independent scaffold review

Reviewed 2026-09-25 by a separate Codex subagent. This is not a Claude Code review. Scope: repository scaffold, executable Python, tests, tracked smoke artifacts, research brief, coordination instructions, README, and initial results. No code was edited by this reviewer. Obsolete orchestration-only follow-ups were removed during repository cleanup; original text remains in Git history.

## Outcome

No blocking correctness defect found in the supplied smoke experiment. All seven unit tests passed under the available Python. Independently rerunning `simulate` reproduced every recorded prediction row and the complete seed-level summary exactly; the rounded aggregate values in RESULTS.md also match. Scoring precedes updates, all baselines receive paired observations, and hidden change metadata does not enter learner methods. Existing-output protection and repository output scope are covered by passing tests.

The README and results correctly call this a plumbing check, make no novelty or AGI claim, and disclose that active experimentation, causal discovery, calibration diagnostics, and learned representations remain unimplemented. The baseline documentation correctly identifies the forgetting window as per-action rather than global time.

## Limitations and future work

- The five seeds, known switching probabilities, and fixed window are development smoke settings. They cannot establish a general adaptation advantage or a novel research gap.
- Log loss is clipped at 1e-12 as documented; it is a finite numerical approximation at endpoint probabilities.
- Runtime metadata records a dirty working tree and a local revision that may differ from browser publication. Exact artifact reproduction was independently verified, but future research runs should preserve a clean source revision or source snapshot/hash as well as the config hash.
- The runner is intentionally small and holds predictions in memory. Respect the documented resource cap; do not scale its configuration without considering memory and runtime.
- GitHub publication, authentication, actual external-agent availability, automation delivery, and Notion page contents were outside this file review. No claim that external agents ran or that tomorrow's report is scheduled follows from these checks.

## Verification performed

`python3 -m unittest discover -s tests -v` — 7 passed.

A separate read-only Python check compared fresh simulation output to all stored CSV fields and the complete summary JSON, then independently aggregated the metrics printed in RESULTS.md — passed.

## Independent first-phase literature review

Reviewed research/prior_art.md and research/search_log.md after the separate research worker completed them. No blocking claim defect found. This was a limited substantive review, not an independent reconstruction of every search query or audit of all twelve bibliography records.

Opened and checked the four closest primary texts: [BOCPD](https://arxiv.org/html/0710.3742v1), [Deep Adaptive Design](https://proceedings.mlr.press/v139/foster21a/foster21a.pdf), [Adaptive Conformal Inference](https://arxiv.org/pdf/2106.00170), and [causal intervention design](https://arxiv.org/html/2209.04744v2). The map accurately reports BOCPD's within-segment independence assumptions and run-length uncertainty; DAD's 30-design location-finding setup and listed controls; ACI's distinction between long-run and per-step coverage; and the causal intervention paper's main known-DAG/unknown-weight setting.

The proposed direction is explicitly a candidate question, not an established gap. The report correctly identifies active change detection, controlled sensing, dual control, nonstationary bandits, and recent literature as missing coverage that blocks novelty claims. The uncertain 2026 source is quarantined, not used to support a result. This evidence is sufficient for a bounded first-phase map; it does not yet justify selecting a novel method or declaring the entire research program complete.
