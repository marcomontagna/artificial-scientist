# Reproduce the one-revision study

Use a clean checkout with the source/config hashes recorded in the published run metadata, Python3.9 or later, and the repository as the working directory. The experiment uses only the standard library. Do not overwrite the original run or edit frozen thresholds. These commands use new output directories; choose another unique suffix if they already exist. The original smoke/full records remain the evidence for the published result.

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python - <<'PYTHON'
import subprocess, sys
from pathlib import Path
smoke = Path('results/runs/equation_revision_v0_reproduction_smoke')
full = Path('results/runs/equation_revision_v0_reproduction')
if smoke.exists() or full.exists():
    raise SystemExit('Use fresh output paths; preserve existing results.')
base = [sys.executable, '-m', 'artificial_scientist.equation_revision',
        '--config', 'experiments/equation_revision_v0.json']
subprocess.run(base + ['--output', str(smoke), '--smoke'], check=True, timeout=150)
subprocess.run(base + ['--output', str(full), '--smoke-evidence', str(smoke)],
               check=True, timeout=150)
PYTHON
```

The runner must validate smoke hashes, time/disk projections and a clean source state before full execution. An incomplete smoke has a false full-study completion flag by design; resource readiness is recorded separately. Preserve partial output on failure and investigate rather than silently resampling. A failing scientific utility screen is a result, not a command error or reason to retry.

The fixed full study uses development seeds1200–1259; this is computational reproduction, not untouched confirmation. All five pipelines share each dataset's88observations. Common evaluation points lie inside the wide observation domain; outer-shell error is not an extrapolation claim. Earlier source/data are unchanged.
