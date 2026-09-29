"""Real-source preservation and temporary edge cases for the two fixed profiles."""
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from load_corpus import load_ntpc_csv, load_iocl_csv


ROOT = Path(__file__).resolve().parents[1]
PROFILES = (
    (load_ntpc_csv, "ntpc_material_items.csv", 486, "NTPC Limited", "2.2",
     "raw-ntpc-v0.1", ("nit_id", "doc_name", "line_no"),
     {"description_original": "item_text", "uom_original": "unit",
      "quantity_original": "quantity", "document_reference": "doc_name"}),
    (load_iocl_csv, "iocl_procurement_plan_items.csv", 1224,
     "Indian Oil Corporation Limited", "2.3", "raw-iocl-v0.1",
     ("source_pdf", "page", "sl_no"),
     {"description_original": "item_description", "uom_original": "unit",
      "quantity_original": "quantity", "document_reference": "source_pdf",
      "source_section": "section"}),
)


class SourceLoaderTests(unittest.TestCase):
    def source(self, filename):
        path = ROOT / "data/raw/huggingface" / filename
        snapshot = path.read_bytes()
        rows = list(csv.DictReader(io.StringIO(snapshot.decode("utf-8-sig"), newline="")))
        return path, snapshot, rows

    def write_rows(self, path, rows):
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_real_files_preserve_all_rows_fields_and_origins(self):
        for loader, filename, count, org, section, profile, ids, mapping in PROFILES:
            with self.subTest(filename=filename):
                path, before, rows = self.source(filename)
                records = loader(path, import_root=ROOT)
                self.assertEqual(len(records), count)
                self.assertEqual([r["raw_fields"] for r in records], rows)
                self.assertEqual([r["source_row"] for r in records], list(range(1, count + 1)))
                for record, row in zip(records, rows):
                    self.assertEqual(record["schema_version"], "0.1")
                    self.assertEqual(record["mapping_id"], profile)
                    self.assertEqual(record["source_sha256"], hashlib.sha256(before).hexdigest())
                    self.assertEqual(record["source_file"], path.relative_to(ROOT).as_posix())
                    self.assertIsNone(record["source_sheet"])
                    self.assertEqual(record["source_organization"], org)
                    self.assertEqual(record["field_origins"]["source_organization"],
                                     {"kind": "constant", "value": org, "evidence": f"SOURCES.md section {section}"})
                    self.assertEqual(record["source_identifiers"], {key: row[key] for key in ids})
                    self.assertEqual(record["field_origins"]["source_identifiers"],
                                     {key: {"kind": "column", "name": key} for key in ids})
                    for target, column in mapping.items():
                        self.assertEqual(record[target], row[column] if row[column].strip() else None)
                        self.assertEqual(record["field_origins"][target], {"kind": "column", "name": column})
                        if not row[column].strip():
                            self.assertIn({"field": target, "reason": "blank", "severity": "warning"}, record["issues"])
                    unmapped = ["source_record_id", "legacy_material_code", "category_original", "source_system", "source_url"]
                    if "source_section" not in mapping:
                        unmapped.append("source_section")
                    for target in unmapped:
                        self.assertIsNone(record[target])
                        self.assertEqual(record["field_origins"][target], {"kind": "unmapped"})
                        self.assertIn({"field": target, "reason": "unmapped", "severity": "warning"}, record["issues"])
                    self.assertEqual(record["specifications_original"], {})
                    self.assertTrue(record["eligible_for_processing"])
                json.dumps(records, allow_nan=False)
                self.assertEqual(path.read_bytes(), before)

    def test_repeated_records_and_cross_file_text_stay_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            combined = []
            shared_text = self.source(PROFILES[0][1])[2][0]["item_text"]
            for loader, filename, _, _, _, _, ids, mapping in PROFILES:
                row = self.source(filename)[2][0].copy()
                row[mapping["description_original"]] = shared_text
                # Test-only text formatting changes; no material codes or labels.
                row[ids[-1]] = "00028"
                row["unit"] = "NA"
                row["quantity"] = "0"
                row["extra"] = ' untouched, "text"\r\nsecond line '
                path = root / filename
                self.write_rows(path, [row, row])
                before = path.read_bytes()
                records = loader(path, import_root=root)
                self.assertEqual([r["raw_fields"] for r in records], [row, row])
                self.assertEqual([r["source_row"] for r in records], [1, 2])
                for record in records:
                    self.assertEqual(record["source_identifiers"][ids[-1]], "00028")
                    self.assertEqual(record["uom_original"], "NA")
                    self.assertEqual(record["quantity_original"], "0")
                    self.assertIsNone(record["source_record_id"])
                self.assertEqual(path.read_bytes(), before)
                combined.extend(records)
            self.assertEqual(len(combined), 4)
            self.assertEqual(len({r["description_original"] for r in combined}), 1)
            self.assertEqual(len({(r["source_file"], r["source_sha256"], r["source_sheet"], r["source_row"]) for r in combined}), 4)

    def test_blank_description_and_locator_do_not_drop_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            for loader, filename, _, _, _, _, ids, mapping in PROFILES:
                row = self.source(filename)[2][0].copy()
                row[mapping["description_original"]] = " \t"
                row[ids[-1]] = " "
                path = Path(directory) / filename
                self.write_rows(path, [row])
                record = loader(path)[0]
                self.assertEqual(record["raw_fields"], row)
                self.assertFalse(record["eligible_for_processing"])
                self.assertIn({"field": "description_original", "reason": "blank", "severity": "error"}, record["issues"])
                self.assertEqual(record["source_identifiers"][ids[-1]], " ")
                self.assertIn({"field": f"source_identifiers.{ids[-1]}", "reason": "blank", "severity": "warning"}, record["issues"])

    def test_missing_profile_columns_and_malformed_rows_fail_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            for loader, filename, _, _, _, _, ids, mapping in PROFILES:
                row = self.source(filename)[2][0].copy()
                path = Path(directory) / filename
                for column in set(mapping.values()) | set(ids):
                    with self.subTest(filename=filename, missing=column):
                        self.write_rows(path, [{k: v for k, v in row.items() if k != column}])
                        before = path.read_bytes()
                        with self.assertRaisesRegex(ValueError, "missing mapped columns"):
                            loader(path)
                        self.assertEqual(path.read_bytes(), before)
                self.write_rows(path, [row])
                malformed = path.read_bytes() + b"too,few\r\n"
                path.write_bytes(malformed)
                with self.assertRaisesRegex(ValueError, "row width"):
                    loader(path)
                self.assertEqual(path.read_bytes(), malformed)


if __name__ == "__main__":
    unittest.main()
