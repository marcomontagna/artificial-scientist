# Historical prototypes — preserved, retired

All original source, tests, configurations, reports, compact results, citations and replays are preserved at immutable commit **`0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9`**. The active checkout no longer presents these disconnected studies as the current system.

[Browse the complete snapshot](https://github.com/marcomontagna/artificial-scientist/tree/0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9) · [Historical results](https://github.com/marcomontagna/artificial-scientist/blob/0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9/RESULTS.md) · [Code](https://github.com/marcomontagna/artificial-scientist/tree/0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9/artificial_scientist) · [Tests](https://github.com/marcomontagna/artificial-scientist/tree/0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9/tests) · [Research and reviews](https://github.com/marcomontagna/artificial-scientist/tree/0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9/research) · [Replays](https://github.com/marcomontagna/artificial-scientist/tree/0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9/visualization).

Retired groups: Bernoulli scaffold, sequence/context selectors, causal diagnostics, switch/room prototypes and all equation studies. Do not copy one archived module back without its dependency/test/config group. The original 103-test suite belongs to this snapshot, not the new laboratory.

[retired_paths.json](retired_paths.json) lists every removed tracked path and its original SHA-256. Kept files may have been rewritten for the new direction; their original versions also remain in the snapshot. No Git history was rewritten. Ignored local `results/runs/` records, environment and caches were not deleted. Raw runs were never all tracked on GitHub; reconstruct missing ones only from the matching historical protocol if explicitly needed.

Read a historical file without changing the checkout:

```sh
git show 0c7c3e4dbe3405a0f681b31fbc92e47aefac9ad9:research/equation_revision_result.md
```

For execution, use a separate checkout of the snapshot and its original instructions. Current commands and imports intentionally do not run the archived studies. The [RNG erratum](../research/equation_domain_rng_erratum.md) remains applicable; preserve negative results and evidence limitations.
