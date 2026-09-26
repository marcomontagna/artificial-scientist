# Domain-study RNG erratum — September 26, 2026

Claude’s review of the next protocol exposed a seed-spacing defect also present in the completed domain study. A separate Codex critic verified **38 cross-seed stream collisions**: audit-noise generator10100011+s equals audit-input generator10100009+(s+2), for s=850…887. The same PRNG stream therefore contributes noise to one dataset and inputs to another.

Within each dataset, its training, audit-input and audit-noise streams remain distinct. The individual known-Gaussian predictive-test derivation is unaffected under its stated null. Recorded counts, rates and fixed engineering-screen outcome are unchanged. However, independent-seed assumptions behind aggregate Wilson intervals and paired standard errors are not justified. **Do not interpret those intervals as validated uncertainty estimates or use them for population-level precision claims.** A special pivotal-statistic independence argument could exist for some null checks; none was established here.

The affected full run is `results/runs/equation_domain_v0_20260926`, source `7b19220`. Raw and compact artifacts are preserved unchanged, including mechanically calculated intervals. Earlier independent audits reproduced calculations correctly but did not establish joint random-stream independence. This erratum supplements those audits rather than silently replacing the evidence.

The first equation-fitting and second confirmation studies use offsets separated by roughly100,000 and are not affected by this particular collision. The next pipeline protocol now spaces streams by100,000 and tests uniqueness across all law/input/noise stream IDs for study, smoke and fixture seeds. Intentional pairing across worlds within a seed remains explicit.

No retrospective tuning or rerun was performed. A new pipeline run cannot be presented as a direct replication of the old local-versus-wide comparison. Any confirmatory rerun of that comparison needs its own reviewed protocol and fresh streams.
