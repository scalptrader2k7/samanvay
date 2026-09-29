import csv
import hashlib
import json
from pathlib import Path
import unittest

from phase6_sample import HUMAN_FIELDS, OUTCOMES, generate

ROOT = Path(__file__).resolve().parents[1]


class Phase6SampleTests(unittest.TestCase):
    def test_sample_is_unique_balanced_traceable_and_unlabeled(self):
        output = ROOT / "output/phase6-v0.1"
        with (output / "review_sample.csv").open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 100)
        keys = {tuple(sorted((row["left_source_record_id"], row["right_source_record_id"])))
                for row in rows}
        self.assertEqual(len(keys), 100)
        for outcome in OUTCOMES:
            self.assertEqual(sum(row["automated_outcome"] == outcome for row in rows), 20)
        self.assertTrue(any(row["automated_evidence_disposition"] == "insufficient_evidence" for row in rows))
        self.assertTrue(any(row["automated_evidence_disposition"] == "supported_incompatibility" for row in rows))
        self.assertTrue(any(row["left_source_organization"] != row["right_source_organization"] for row in rows))
        for row in rows:
            self.assertTrue(row["left_source_record_id"] and row["right_source_record_id"])
            self.assertTrue(row["left_description_original"] and row["right_description_original"])
            self.assertTrue(json.loads(row["retrieval_directions_json"]))
            self.assertTrue(all(row[field] == "" for field in HUMAN_FIELDS))

    def test_report_reconciles_directions_and_manifest(self):
        output = ROOT / "output/phase6-v0.1"
        report = json.loads((output / "sample_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["directed_phase4_pairs"], 89381)
        self.assertLess(report["unique_unordered_pairs"], report["directed_phase4_pairs"])
        self.assertEqual(report["human_labeled_pairs"], 0)
        self.assertFalse(report["accuracy_metrics_reported"])
        self.assertEqual(report["validation_status"], "pending_human_review")
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        for name, expected in manifest["artifacts"].items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), expected)
        with self.assertRaises(FileExistsError):
            generate(ROOT / "output/phase3-v0.1/material_attributes.jsonl",
                     ROOT / "output/phase4-v0.1/candidates.jsonl", output)


if __name__ == "__main__":
    unittest.main()
