# Reproducing the three equation studies

**Historical reproduction warning:** the domain study has [cross-seed RNG reuse](equation_domain_rng_erratum.md). These commands preserve/reproduce that historical design; they are not a corrected independent replication, and its aggregate intervals lack validated coverage. Use the new pipeline protocol for its distinct integration question.

Run from the repository root in a clean, independently reviewed checkout. No installation, API key or paid service is needed. These commands repeat already inspected development seeds, not held-out evaluation. Do not change thresholds or regenerate outcomes to seek a passing screen.

Protocols: [equation fitting](../experiments/equation_discovery_v0.md), [independent term confirmation](../experiments/equation_confirmation_v0.md), [domain challenge](../experiments/equation_domain_v0.md).

All three studies have implemented modules and fixed protocols. Use the final reviewed checkout and inspect each completed run before interpreting its screen. The same execution safeguards apply to every stage.

First run the tests:

```sh
python3 -m unittest discover -s tests -v
```

Then use this bounded reproduction wrapper. Each study gets a fresh smoke directory and a separate fresh full-run directory. A failed smoke, resource no-go, timeout or full run stops the sequence. Preserve earlier runs.

```sh
python3 - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

root = Path.cwd().resolve()
status = subprocess.run(
    ['git', 'status', '--porcelain'], cwd=root,
    check=True, capture_output=True, text=True)
if status.stdout:
    raise SystemExit('Use a clean reviewed checkout before sampling.')

studies = ['equation_discovery', 'equation_confirmation', 'equation_domain']

stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
for study in studies:
    config = root / 'experiments' / (study + '_v0.json')
    if not config.is_file():
        raise SystemExit('Missing reviewed configuration: ' + str(config))
    smoke = root / 'results' / 'runs' / (study + '_reproduction_smoke_' + stamp)
    full = root / 'results' / 'runs' / (study + '_reproduction_full_' + stamp)
    if smoke.exists() or full.exists():
        raise SystemExit('Choose fresh output names; existing runs are preserved.')
    base = [sys.executable, '-m', 'artificial_scientist.' + study,
            '--config', str(config)]
    subprocess.run(base + ['--output', str(smoke), '--smoke'],
                   cwd=root, check=True, timeout=150)
    subprocess.run(base + ['--output', str(full),
                           '--smoke-evidence', str(smoke)],
                   cwd=root, check=True, timeout=150)
    print('Completed:', full)
PY
```

Each runner also enforces its internal deadline, artifact-size cap and smoke projection gate; the wrapper does not bypass them or shrink the study. Source, helper, protocol, test and configuration hashes must match the smoke evidence. Freeze files between smoke and full execution. Preserve incomplete artifacts after an interruption; incomplete runs cannot pass.

Use the recorded source commit and hashes to reproduce exact statistics. Deterministic numerical outputs should match on compatible runtimes; timing and metadata timestamps vary, and small floating-point differences may occur across platforms. Compact evidence lives in tracked `results/` folders; complete raw runs live under ignored `results/runs/`. Review both metadata and completeness before interpreting results.
