import json
from pathlib import Path
import tempfile
import unittest

from phase5_build import generate

ROOT = Path(__file__).resolve().parents[1]


class Phase5PackTests(unittest.TestCase):
    def test_authoritative_pack_reconciles_and_examples_pass(self):
        output = ROOT / "output/phase5-v0.1"
        report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        examples = json.loads((output / "examples.json").read_text(encoding="utf-8"))
        phase4_pairs = 0
        with (ROOT / "output/phase4-v0.1/candidates.jsonl").open(encoding="utf-8") as stream:
            for line in stream:
                phase4_pairs += len(json.loads(line)["candidates"])
        with (output / "pair_evidence.jsonl").open(encoding="utf-8") as stream:
            output_pairs = sum(1 for _ in stream)
        self.assertEqual(report["source_records"], 9245)
        self.assertEqual(report["phase4_query_records"], 9245)
        self.assertEqual(report["pair_results"], phase4_pairs)
        self.assertEqual(output_pairs, phase4_pairs)
        self.assertEqual(sum(report["outcome_rule_counts"].values()), phase4_pairs)
        self.assertTrue(all(case["passed"] for case in examples))
        self.assertEqual(report["automatic_merges"], 0)
        self.assertEqual(report["common_codes_assigned"], 0)

    def test_manifest_hashes_and_no_overwrite(self):
        output = ROOT / "output/phase5-v0.1"
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        import hashlib
        for name, expected in manifest["artifacts"].items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), expected)
        with self.assertRaises(FileExistsError):
            generate(ROOT / "output/phase3-v0.1/material_attributes.jsonl",
                     ROOT / "output/phase4-v0.1/candidates.jsonl", output)


if __name__ == "__main__":
    unittest.main()
