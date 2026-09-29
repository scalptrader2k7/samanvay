from pathlib import Path
import unittest

from phase6_inspect import inspect_sample

ROOT = Path(__file__).resolve().parents[1]


class Phase6InspectionTests(unittest.TestCase):
    def test_sample_safety_invariants(self):
        report = inspect_sample(ROOT / "output/phase6-v0.1/review_sample.csv")
        self.assertEqual(report["rows"], 100)
        self.assertEqual(report["exact_rows"], 20)
        self.assertEqual(report["conflict_rows"], 20)
        self.assertGreater(report["insufficient_evidence_rows"], 0)
        self.assertEqual(report["failures"], [])


if __name__ == "__main__":
    unittest.main()
