import json
import math
from pathlib import Path
import tempfile
import unittest

from artificial_scientist.environment import SwitchingBernoulli
from artificial_scientist.baselines import BetaBernoulli
from artificial_scientist.metrics import scores
from artificial_scientist.run import simulate, run

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "experiments/smoke.json").read_text())


class CoreTests(unittest.TestCase):
    def test_hidden_change_boundary(self):
        env = SwitchingBernoulli(0, [0], [1], 2)
        self.assertEqual([env.step(0) for _ in range(4)], [0, 0, 1, 1])

    def test_invalid_environment(self):
        with self.assertRaises(ValueError):
            SwitchingBernoulli(0, [1.1], [0], 2)
        with self.assertRaises(ValueError):
            SwitchingBernoulli(0, [0], [1], 2).step(-1)

    def test_posterior_and_forgetting(self):
        learner = BetaBernoulli(1, window=2)
        self.assertEqual(learner.predict(0), 0.5)
        learner.update(0, 1)
        self.assertAlmostEqual(learner.predict(0), 2 / 3)
        learner.update(0, 0)
        learner.update(0, 0)
        self.assertEqual(learner.predict(0), 0.25)

    def test_scores(self):
        self.assertEqual(scores(0.5, 1)["brier"], 0.25)
        self.assertAlmostEqual(scores(0.5, 0)["log_loss"], math.log(2))
        self.assertTrue(math.isfinite(scores(0, 1)["log_loss"]))
        for p in (-0.1, 1.1, float("nan")):
            with self.assertRaises(ValueError):
                scores(p, 0)

    def test_reproducible_paired_predict_before_update(self):
        first = simulate(CONFIG)
        self.assertEqual(first, simulate(CONFIG))
        rows, summary = first
        self.assertEqual(len(rows), 5 * 200 * 3)
        self.assertEqual(len(summary), 5 * 3 * 2)
        for i in range(0, len(rows), 3):
            group = rows[i:i + 3]
            self.assertEqual(len({(r["action"], r["outcome"]) for r in group}), 1)
        self.assertTrue(all(r["probability"] == 0.5 for r in rows if r["step"] == 0))

    def test_artifacts_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            output = Path(directory) / "run"
            run(ROOT / "experiments/smoke.json", output)
            self.assertEqual({p.name for p in output.iterdir()},
                             {"config.json", "summary.json", "metadata.json", "predictions.csv"})
            self.assertEqual(json.loads((output / "config.json").read_text()), CONFIG)
            with self.assertRaises(FileExistsError):
                run(ROOT / "experiments/smoke.json", output)

    def test_scope_guard(self):
        with self.assertRaises(ValueError):
            run(ROOT / "experiments/smoke.json", ROOT.parent / "outside-run")


if __name__ == "__main__":
    unittest.main()
