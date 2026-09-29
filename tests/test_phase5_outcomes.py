import json
from pathlib import Path
import subprocess
import sys
import unittest

from pair_evidence import compare_pair

ROOT = Path(__file__).resolve().parents[1]


class Phase5OutcomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "output/phase3-v0.1/material_attributes.jsonl").open(encoding="utf-8") as stream:
            cls.records = {item["source_record_id"]: item for item in map(json.loads, stream)}

    def outcome(self, left, right, retrieval=None):
        return compare_pair(self.records[left], self.records[right], retrieval)

    def test_exact_duplicate_keeps_unknowns_and_requires_review(self):
        result = self.outcome("M000114", "M008245")
        self.assertEqual(result["outcome"]["label"], "exact_duplicate")
        self.assertTrue(result["outcome"]["review_required"])
        self.assertIn("pressure", result["outcome"]["critical_unknown_or_uncertain_fields"])
        self.assertEqual(result["left"]["description_original"], "Centrifugal Pump")

    def test_near_duplicate_with_matching_specifications(self):
        result = self.outcome("M000753", "M000925")
        self.assertEqual(result["outcome"]["label"], "near_duplicate")
        self.assertEqual(result["field_comparisons"]["standard"]["status"], "compatible")

    def test_possible_equivalent_is_reviewer_only(self):
        result = self.outcome("M000041", "M000114")
        self.assertEqual(result["outcome"]["label"], "possible_functional_equivalent")
        self.assertTrue(result["outcome"]["qualified_reviewer_required"])
        self.assertTrue(result["outcome"]["identity_merge_blocked"])
        self.assertIn("engineering equivalence is not established", result["outcome"]["explanation"])

    def test_critical_conflict_precedes_similar_text(self):
        result = self.outcome("M000830", "M000834")
        self.assertEqual(result["outcome"]["label"], "conflict")
        self.assertTrue(result["outcome"]["identity_merge_blocked"])

    def test_different_explicit_families_are_no_match(self):
        result = self.outcome("M000114", "M000165")
        self.assertEqual(result["outcome"]["label"], "no_match")
        self.assertIn("family.different_explicit_family", result["outcome"]["reason_codes"])
        self.assertEqual(result["outcome"]["evidence_disposition"], "supported_incompatibility")

    def test_unrelated_records_with_generic_shared_words_are_no_match(self):
        def record(source_id, description, family, start, end):
            return {"source_record_id": source_id, "source_organization": "test",
                    "description_original": description, "description_normalized": description,
                    "family": family,
                    "family_evidence": {"value_raw": description[start:end],
                        "value_normalized": family, "start": start, "end": end,
                        "rule_id": f"family.{family}.explicit"},
                    "attributes": {name: [] for name in
                        ("size_dimension", "material_grade", "standard", "pressure", "voltage", "model_part")}}
        left = record("TEST-P", "industrial spare pump", "pump", 17, 21)
        right = record("TEST-V", "industrial spare valve", "valve", 17, 22)
        result = compare_pair(left, right)
        self.assertIn("industrial", result["supporting_text_evidence"]["shared_useful_tokens"])
        self.assertEqual(result["outcome"]["label"], "no_match")

    def test_insufficient_evidence_is_not_confirmed_no_match(self):
        def record(source_id, description):
            return {"source_record_id": source_id, "source_organization": "test",
                    "description_original": description, "description_normalized": description,
                    "family": None, "family_evidence": None,
                    "attributes": {name: [] for name in
                        ("size_dimension", "material_grade", "standard", "pressure", "voltage", "model_part")}}
        result = compare_pair(record("TEST-A", "assembly item"), record("TEST-B", "general component"))
        self.assertEqual(result["outcome"]["label"], "no_match")
        self.assertEqual(result["outcome"]["evidence_disposition"], "insufficient_evidence")
        self.assertTrue(result["outcome"]["review_required"])
        self.assertIn("confirmed incompatibility", result["outcome"]["explanation"])

    def test_exact_text_keeps_unknowns_and_conflict_still_precedes_text(self):
        exact = self.outcome("M000114", "M008245")
        self.assertTrue(exact["supporting_text_evidence"]["exact_normalized_text"])
        self.assertEqual(exact["outcome"]["evidence_disposition"], "supported_duplicate_text")
        self.assertTrue(exact["outcome"]["critical_unknown_or_uncertain_fields"])
        conflict = self.outcome("M000830", "M000834")
        self.assertEqual(conflict["outcome"]["evidence_disposition"], "supported_incompatibility")

    def test_retrieval_score_is_separate_and_cannot_change_outcome(self):
        base = {"status": "candidate_only", "retrieval_version": "test", "rank": 1,
                "reasons": [], "query_source_record_id": "M000830",
                "candidate_source_record_id": "M000834"}
        high = self.outcome("M000830", "M000834", {**base, "retrieval_score": 1.0})
        low = self.outcome("M000830", "M000834", {**base, "retrieval_score": 0.01})
        self.assertEqual(high["outcome"], low["outcome"])
        self.assertNotIn("retrieval_score", high["outcome"])
        self.assertEqual(high["retrieval"]["retrieval_score"], 1.0)

    def test_cli_returns_readable_traceable_json(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "phase5_compare.py"), "M000913", "M000927",
             "--candidates", ""], cwd=ROOT, text=True, capture_output=True, check=True)
        result = json.loads(completed.stdout)
        self.assertEqual(result["outcome"]["label"], "conflict")
        self.assertEqual(result["left"]["source_record_id"], "M000913")
        self.assertEqual(result["right"]["source_record_id"], "M000927")


if __name__ == "__main__":
    unittest.main()
