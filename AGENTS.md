# Repository working agreement

## Active assignment

Read README.md, research/direction.md, research/tool_lab.md and NEXT_STEPS.md. Build a tool-using learner that investigates an unfamiliar persistent simulated world. Complete one observe/propose/predict/act/revise loop before expanding it. The user explicitly retired disconnected equation/calibration/selector exercises. Do not restart the archived studies or require a novel algorithm before implementing a useful prototype.

Known methods are allowed and should be attributed. Claims of novelty, true-law recovery, calibrated uncertainty or general intelligence require their own evidence; none follows from a working demo. Do not hand the learner a catalogue of complete correct world rules or secretly use an LLM/developer to select each experiment.

## Scope and spending

- Work inside this repository. Preserve user changes, ignored raw runs and Git history. The authorized historical cleanup is recorded in archive/retired_paths.json; it is not permission for unrelated deletion.
- No purchases, paid APIs, paid fallback, new services, large downloads, global installs, system changes or credential changes. Existing Claude subscription access is authorized; stop at limits rather than enabling spending.
- Use the local Python environment; no mandatory MLX or pretrained LLM. Keep simulator/tool execution bounded. Do not give generated model programs filesystem, network or arbitrary host-code access.
- No force pushes, history rewrites, remote deletion or releases. Follow the user's existing authorization for normal reviewed commits/pushes; do not repeatedly ask for permission already granted.

## Engineering

The learner sees only its public sensor/action interface and its own history. Hidden laws, world IDs and evaluator-only outcomes cannot guide proposals, actions or revisions. Record predictions before outcomes, model changes, uncertainty limits, failed actions and tool/search costs. Preserve failures and use fresh output directories.

Tests must protect meaningful boundaries and behavior: tool semantics/costs, world persistence, evaluator isolation, safe model execution, prediction timing and bounded termination. Run the relevant tests and one bounded integration check after code changes. Documentation-only cleanup does not require invented tests or an empty test suite advertised as success.

Default session cap 6 hours; individual experiment cap 10 minutes, aggregate experiments 60 minutes, one process at a time, target 2 GB memory/500 MB new artifacts. Tighter prototype limits in the active design take precedence. No background daemon or automatic chain of new experiments.

## Independent review

Every substantive code file, research note, prompt, report or artifact must receive review by a different agent before finalization. Root reviews delegated work; a separate agent reviews root-authored changes. Record ownership, findings, fixes and unresolved limits briefly in research/review_log.md. Reviewer findings are reviewed by the receiving coordinator; avoid infinite review chains. Claude is a critic, not an automatic authority: preserve objections and explain decisions. At most three workers plus coordinator.

Conserve tokens. Ask concise questions only when needed; otherwise continue within the authorized direction. Report what is implemented, what was tested and what remains proposed. Keep user reports short.
