import json
from pathlib import Path
import unittest

from pair_evidence import compare_attributes

ROOT = Path(__file__).resolve().parents[1]


class Phase5ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "output/phase3-v0.1/material_attributes.jsonl").open(encoding="utf-8") as stream:
            cls.records = {item["source_record_id"]: item for item in map(json.loads, stream)}

    def compare(self, left, right):
        return compare_attributes(self.records[left], self.records[right])

    def test_pipe_size_conflict_blocks_identity(self):
        result = self.compare("M000913", "M000927")
        self.assertEqual(result["fields"]["size_dimension"]["status"], "conflict")
        self.assertTrue(result["identity_merge_blocked"])
        self.assertIn("size_dimension.different_linear_dimension_mm",
                      {x["reason_code"] for x in result["critical_conflicts"]})

    def test_cable_cross_section_conflict_blocks_identity(self):
        result = self.compare("M000830", "M000834")
        field = result["fields"]["size_dimension"]
        self.assertEqual(field["status"], "conflict")
        self.assertEqual(field["conflicts"][0]["comparison_type"], "cross_section_area_mm2")

    def test_matching_pipe_specs_are_compatible_and_traceable(self):
        result = self.compare("M000753", "M000925")
        self.assertEqual(result["fields"]["size_dimension"]["status"], "compatible")
        self.assertEqual(result["fields"]["standard"]["status"], "compatible")
        for field in result["fields"].values():
            for group in field.get("compatible", []) if isinstance(field.get("compatible"), list) else []:
                for side in ("left_evidence", "right_evidence"):
                    for evidence in group[side]:
                        record = self.records[evidence["source_record_id"]]
                        self.assertEqual(record["description_original"][evidence["start"]:evidence["end"]],
                                         evidence["value_raw"])

    def test_pressure_class_and_psi_are_not_equated_and_block_identity(self):
        result = self.compare("M010407", "M003626")
        pressure = result["fields"]["pressure"]
        self.assertEqual(pressure["status"], "conflict")
        self.assertEqual(pressure["conflicts"][0]["reason_code"],
                         "pressure.incompatible_rating_bases")
        self.assertTrue(result["identity_merge_blocked"])

    def test_missing_values_are_unknown_not_agreement(self):
        result = self.compare("M000114", "M008245")
        self.assertEqual(result["fields"]["size_dimension"]["status"], "unknown")
        self.assertEqual(result["fields"]["size_dimension"]["missing"], ["left", "right"])
        self.assertTrue(result["review_required"])

    def test_voltage_compatible_units_and_diameter_not_area(self):
        def record(source_id, text, size, voltage):
            return {"source_record_id": source_id, "description_original": text,
                    "family": "cable", "family_evidence": None,
                    "attributes": {"size_dimension": size, "voltage": voltage,
                                   "material_grade": [], "standard": [], "pressure": [], "model_part": []}}
        left = record("L", "15 mm cable 1 kV",
                      [{"value_raw": "15 mm", "value_normalized": "15 MM", "start": 0, "end": 5, "rule_id": "size.metric"}],
                      [{"value_raw": "1 kV", "value_normalized": "1 KV", "start": 12, "end": 16, "rule_id": "voltage.explicit"}])
        right = record("R", "15 mm2 cable 1000 V",
                       [{"value_raw": "15 mm2", "value_normalized": "15 MM2", "start": 0, "end": 6, "rule_id": "size.metric"}],
                       [{"value_raw": "1000 V", "value_normalized": "1000 V", "start": 13, "end": 19, "rule_id": "voltage.explicit"}])
        result = compare_attributes(left, right)
        self.assertEqual(result["fields"]["voltage"]["status"], "compatible")
        self.assertEqual(result["fields"]["size_dimension"]["status"], "uncertain")
        self.assertFalse(result["fields"]["size_dimension"]["compatible"])


if __name__ == "__main__":
    unittest.main()
