"""Run a paired, passive-action smoke comparison and save auditable artifacts."""
import argparse
import csv
import hashlib
import json
import platform
import random
import statistics
import subprocess
import time
from pathlib import Path

from .baselines import BetaBernoulli, Constant
from .environment import SwitchingBernoulli
from .metrics import scores


def git_info(root):
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, stderr=subprocess.DEVNULL,
            text=True).strip()
        dirty = bool(subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=root, text=True).strip())
        return {"revision": revision, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"revision": None, "dirty": None}


def simulate(config):
    steps, change = config["steps"], config["change_at"]
    if not isinstance(steps, int) or not 0 < change < steps:
        raise ValueError("require 0 < change_at < steps")
    seeds = config["seeds"]
    if not seeds or len(seeds) != len(set(seeds)):
        raise ValueError("nonempty distinct seeds required")
    rows, summaries = [], []
    for seed in seeds:
        env = SwitchingBernoulli(seed, config["before"], config["after"], change)
        actions = random.Random(seed + 1000003)
        n_actions = len(config["before"])
        learners = {"constant": Constant(), "cumulative_beta": BetaBernoulli(n_actions),
                    "windowed_beta": BetaBernoulli(n_actions, config["window"])}
        for step in range(steps):
            action = actions.randrange(n_actions)
            predictions = {name: learner.predict(action) for name, learner in learners.items()}
            outcome = env.step(action)
            for name, learner in learners.items():
                rows.append(dict(seed=seed, step=step, action=action, outcome=outcome,
                                 baseline=name, probability=predictions[name],
                                 phase="before" if step < change else "after",
                                 **scores(predictions[name], outcome)))
                learner.update(action, outcome)
        for name in learners:
            for phase in ("before", "after"):
                subset = [r for r in rows if r["seed"] == seed and
                          r["baseline"] == name and r["phase"] == phase]
                summaries.append(dict(seed=seed, baseline=name, phase=phase, n=len(subset),
                                      **{m: statistics.mean(r[m] for r in subset)
                                         for m in ("brier", "log_loss")}))
    return rows, summaries


def run(config_path, output):
    root = Path(__file__).resolve().parents[1]
    output = Path(output).resolve()
    if root not in output.parents:
        raise ValueError("output must be inside this repository")
    if output.exists():
        raise FileExistsError("choose a fresh output directory")
    config_bytes = Path(config_path).read_bytes()
    config = json.loads(config_bytes)
    started = time.perf_counter()
    rows, summaries = simulate(config)
    output.mkdir(parents=True, exist_ok=False)
    (output / "config.json").write_bytes(config_bytes)
    with (output / "predictions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / "summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    metadata = dict(git_info(root), python=platform.python_version(), platform=platform.platform(),
                    elapsed_seconds=time.perf_counter() - started,
                    config_sha256=hashlib.sha256(config_bytes).hexdigest(),
                    purpose="plumbing smoke test; not novelty evidence")
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("experiments/smoke.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.config, args.output)
    print("Saved smoke artifacts to", args.output)


if __name__ == "__main__":
    main()
