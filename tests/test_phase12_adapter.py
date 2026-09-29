from pathlib import Path
import csv
import json
import tempfile
import unittest

from candidate_retrieval import CandidateIndex
from integration_adapter import preview_rows, write_adapter_pack
from pair_evidence import compare_pair


class Phase12AdapterTests(unittest.TestCase):
    def setUp(self):
        self.public_headers = ["organization", "corpus_id", "description", "unit",
                               "product_category", "extra"]
        self.public_rows = [{
            "organization": "NTPC Limited", "corpus_id": "M000753",
            "description": ", PIPE ASTM A312,9.53MM,141.3MM,125NB ,",
            "unit": "", "product_category": "Pipes", "extra": "retained-public"}, {
            "organization": "NTPC Limited", "corpus_id": "M000925",
            "description": "Pipe Astm A312,9.53mm,141.3mm,125nb",
            "unit": "EA", "product_category": "Pipes", "extra": "retained-public-2"}]
        self.public_mapping = {"mapping_id": "phase12-public-v1", "columns": {
            "source_organization": "organization", "source_record_id": "corpus_id",
            "description_original": "description", "uom_original": "unit",
            "category_original": "product_category"}, "identifiers": ["corpus_id"]}
        self.sap_headers = ["Company", "External Row ID", "Short Text", "Base UOM",
                            "Material Group", "Standard Supplied", "Unused Sponsor Field"]
        self.sap_rows = [{
            "Company": row["organization"], "External Row ID": row["corpus_id"],
            "Short Text": row["description"], "Base UOM": row["unit"],
            "Material Group": row["product_category"], "Standard Supplied": "ASTM A312",
            "Unused Sponsor Field": "preserved-" + str(index)}
            for index, row in enumerate(self.public_rows, 1)]
        self.sap_mapping = {"mapping_id": "phase12-sap-shaped-v1", "columns": {
            "source_organization": "Company", "source_record_id": "External Row ID",
            "description_original": "Short Text", "uom_original": "Base UOM",
            "category_original": "Material Group"}, "identifiers": ["External Row ID"],
            "specifications": ["Standard Supplied"]}

    def test_two_schemas_feed_the_unchanged_matching_core(self):
        public = preview_rows(self.public_headers, self.public_rows, self.public_mapping,
                              source_name="public-example.csv")
        sap = preview_rows(self.sap_headers, self.sap_rows, self.sap_mapping,
                           source_name="sap-shaped-example.csv")
        self.assertEqual(public["report"]["matching_ready_records"], 2)
        self.assertEqual(sap["report"]["matching_ready_records"], 2)
        for left, right in zip(public["matching_records"], sap["matching_records"]):
            for field in ("source_organization", "source_record_id", "description_original",
                          "description_normalized", "family", "attributes"):
                self.assertEqual(left[field], right[field])
        self.assertEqual(sap["canonical_records"][0]["specifications_original"],
                         {"Standard Supplied": "ASTM A312"})
        self.assertEqual(sap["canonical_records"][0]["raw_fields"], self.sap_rows[0])
        self.assertIn("Unused Sponsor Field", sap["report"]["unmapped_source_columns"])
        comparison = compare_pair(*sap["matching_records"])
        self.assertEqual(comparison["outcome"]["label"], "near_duplicate")
        retrieved, _ = CandidateIndex(sap["matching_records"]).retrieve("M000753", top_k=1)
        self.assertEqual(retrieved[0]["candidate_source_record_id"], "M000925")

    def test_missing_optional_required_duplicate_and_invalid_values(self):
        rows = [dict(self.sap_rows[0], **{"Base UOM": "", "Material Group": "",
                                        "External Row ID": ""})]
        result = preview_rows(self.sap_headers, rows, self.sap_mapping)
        record = result["canonical_records"][0]
        self.assertIsNone(record["uom_original"])
        self.assertIsNone(record["category_original"])
        self.assertFalse(record["eligible_for_processing"])
        self.assertEqual(result["report"]["matching_ready_records"], 0)
        self.assertTrue(any(issue["reason"] == "required_for_matching_workflow"
                            for issue in record["issues"]))
        duplicate = preview_rows(self.sap_headers, [self.sap_rows[0], self.sap_rows[0]],
                                 self.sap_mapping)
        self.assertEqual(duplicate["report"]["matching_ready_records"], 0)
        bad = dict(self.sap_rows[0]); bad["Base UOM"] = 5
        with self.assertRaisesRegex(ValueError, "must be text"):
            preview_rows(self.sap_headers, [bad], self.sap_mapping)

    def test_deterministic_preview_and_no_overwrite_pack(self):
        first = preview_rows(self.sap_headers, self.sap_rows, self.sap_mapping)
        second = preview_rows(self.sap_headers, self.sap_rows, self.sap_mapping)
        self.assertEqual(first, second)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "source.csv"; output = root / "pack"
            with source.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=self.sap_headers)
                writer.writeheader(); writer.writerows(self.sap_rows)
            report = write_adapter_pack(source, self.sap_mapping, output, import_root=root)
            self.assertEqual(report["matching_ready_records"], 2)
            records = [json.loads(line) for line in
                       (output / "matching_records.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual([row["source_record_id"] for row in records],
                             ["M000753", "M000925"])
            with self.assertRaises(FileExistsError):
                write_adapter_pack(source, self.sap_mapping, output, import_root=root)


if __name__ == "__main__":
    unittest.main()
