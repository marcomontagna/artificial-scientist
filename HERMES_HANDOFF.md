# Live handoff for Hermes and Claude

Updated September 25, 2026. The user says Hermes and Claude are running and asked Hermes to check Codex's work. This document is a task handoff, not evidence that either agent has read or accepted it.

Repository: https://github.com/marcomontagna/artificial-scientist

Local checkout on this Mac:
`/Users/marmon/Documents/Codex/2026-09-25/referenced-chatgpt-conversation-this-is-an/outputs/artificial-scientist`

## Current activity and ownership

Codex primary created and tested the scaffold and is publishing it. Seven tests passed; the five-seed baseline smoke output was independently reproduced by another Codex agent. The results are plumbing checks of known baselines, not a research contribution.

A Codex researcher owns `research/prior_art.md` and `research/search_log.md` for a bounded primary-source literature map. A distinct Codex reviewer owns `research/scaffold_review.md`. Codex primary owns root reports, instructions, publication and Notion. Do not edit those files concurrently. Inspect `research/coordination.md` and existing files before acting.

## Task for Hermes

Acknowledge this handoff by creating `research/hermes_ack.md` inside this repository, stating actual session identity, available Claude access and whether existing access has zero additional cost. Do not launch paid API inference or enable paid fallback. If cost cannot be verified, write that limitation and stop external delegation; Codex is already covering research and review.

Coordinate one focused Claude adversarial review after the literature files appear. Give Claude exclusive ownership of `research/claude_critique.md`. Ask it to read AGENTS.md, CLAUDE.md and the map; verify the closest sources; identify which ideas merely reproduce existing work; and evaluate whether action-dependent observability under hidden changes is a defensible evaluation question. Require counterarguments, missing baselines, leakage checks, a falsifier and a reject/revise/test verdict. No implementation or large search sweep. Have a different agent review this artifact before treating it as final.

Write `research/hermes_status.md` with verified participation, findings, blockers and next handoff. Keep all writes inside this repository. If Codex has already written candidate gaps or a decision, critique those instead of producing a competing plan. Do not push or overwrite Codex-owned reports. The Notion update is owned by Codex.

## Hard constraints

No purchases, subscriptions, paid APIs, cloud jobs, new services or additional charges. Existing access only, no credit purchases or automatic paid fallback. Conserve tokens: one focused critique and review; no unlimited loops. Do not alter system settings, inspect secrets, weaken approvals, or make destructive changes. Every substantive new artifact needs another agent's review; record authorship and reviewer honestly. If Claude is unavailable, label any fallback as Codex, not Claude.

## Report destination

Codex created the Notion project report and scheduled an evidence update for September 26, 2026 at 8 p.m. America/Chicago:
https://app.notion.com/p/3e61202c798281d3bb93d2e241f1f009

Record evidence in this checkout so the report can find it. This handoff does not require a six-hour run: prefer a short, useful critique within existing limits.
