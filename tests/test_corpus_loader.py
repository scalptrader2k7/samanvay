"""Preservation checks on real data and temporary CSV edge-case fixtures."""

import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from load_corpus import load_corpus_csv


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data/raw/huggingface/material_description_corpus.csv"


class CorpusLoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "corpus.csv"
        with CORPUS.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            self.headers = reader.fieldnames
            self.example = next(reader)

    def write_rows(self, rows, headers=None, bom=False):
        with self.path.open("w", encoding="utf-8-sig" if bom else "utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=headers or self.headers)
            writer.writeheader()
            writer.writerows(rows)

    def test_real_corpus_preserves_every_cell_and_row(self):
        before = CORPUS.read_bytes()
        source_rows = list(csv.DictReader(io.StringIO(before.decode("utf-8-sig"), newline="")))
        records = load_corpus_csv(CORPUS, import_root=ROOT)
        self.assertEqual(len(records), 21513)
        self.assertEqual([r["raw_fields"] for r in records], source_rows)
        self.assertEqual([r["source_row"] for r in records], list(range(1, 21514)))
        expected_mapping = {
            "source_record_id": "corpus_id", "source_organization": "organization",
            "description_original": "description", "source_system": "source_system",
            "source_section": "source_section", "source_url": "source_url",
            "document_reference": "document_url", "uom_original": "unit",
            "category_original": "product_category", "quantity_original": "quantity",
        }
        digest = hashlib.sha256(before).hexdigest()
        for record, source in zip(records, source_rows):
            self.assertEqual(record["source_file"], CORPUS.relative_to(ROOT).as_posix())
            self.assertEqual(record["source_sha256"], digest)
            self.assertIsNone(record["source_sheet"])
            for target, column in expected_mapping.items():
                self.assertEqual(record[target], source[column] if source[column].strip() else None)
                self.assertEqual(record["field_origins"][target], {"kind": "column", "name": column})
            self.assertEqual(record["source_identifiers"], {k: source[k] for k in ("corpus_id", "tender_reference", "tender_id")})
            self.assertIsNone(record["legacy_material_code"])
            self.assertEqual(record["specifications_original"], {})
            self.assertTrue(record["eligible_for_processing"])
        self.assertLess(len({r["description_original"] for r in records}), len(records))
        json.dumps(records, allow_nan=False)
        self.assertEqual(CORPUS.read_bytes(), before)

    def test_exact_text_bom_multiline_and_repeated_ids(self):
        row = dict(self.example, corpus_id="000012", description='  Valve, "quoted"\r\nsecond line  ',
                   organization="NA", unit="N/A", quantity="0", product_category="null", extra=" unknown ")
        self.write_rows([row, row], [*self.headers, "extra"], bom=True)
        before = self.path.read_bytes()
        records = load_corpus_csv(self.path)
        self.assertEqual([r["raw_fields"] for r in records], [row, row])
        self.assertEqual([r["source_row"] for r in records], [1, 2])
        for record in records:
            self.assertEqual(record["source_record_id"], "000012")
            self.assertEqual(record["description_original"], row["description"])
            self.assertEqual(record["source_organization"], "NA")
            self.assertEqual(record["uom_original"], "N/A")
            self.assertEqual(record["quantity_original"], "0")
            self.assertEqual(record["category_original"], "null")
            self.assertIn({"field": "source_record_id", "reason": "duplicate", "severity": "warning"}, record["issues"])
            self.assertTrue(record["eligible_for_processing"])
        self.assertEqual(self.path.read_bytes(), before)

    def test_blank_values_are_retained_with_issues(self):
        row = dict(self.example, corpus_id=" ", description="\t", organization="", unit="  ", tender_id=" ")
        self.write_rows([row])
        record = load_corpus_csv(self.path)[0]
        self.assertEqual(record["raw_fields"], row)
        self.assertIsNone(record["source_record_id"])
        self.assertIsNone(record["description_original"])
        self.assertIsNone(record["source_organization"])
        self.assertIsNone(record["uom_original"])
        self.assertFalse(record["eligible_for_processing"])
        self.assertEqual(record["source_identifiers"]["corpus_id"], " ")
        self.assertEqual(record["field_origins"]["legacy_material_code"], {"kind": "unmapped"})
        for field, reason, severity in [
            ("description_original", "blank", "error"), ("source_organization", "blank", "error"),
            ("source_record_id", "blank", "warning"), ("uom_original", "blank", "warning"),
            ("source_identifiers.tender_id", "blank", "warning"),
            ("legacy_material_code", "unmapped", "warning"),
            ("specifications_original", "unmapped", "warning"),
        ]:
            self.assertIn(dict(field=field, reason=reason, severity=severity), record["issues"])

    def test_invalid_structure_and_encoding_fail_without_writes(self):
        self.write_rows([self.example])
        valid = self.path.read_bytes()
        header = valid.split(b"\r\n", 1)[0]
        cases = [
            (b"", "headers"),
            (header + b",corpus_id\r\n", "duplicate headers"),
            (header + b", \r\n", "empty headers"),
            (header.replace(b"description,", b"renamed_description,") + b"\r\n", "missing mapped columns"),
            (valid + b"too,few\r\n", "row width"),
            (valid + b"," * len(self.headers) + b"\r\n", "row width"),
            (valid + b"\r\n", "row width"),
            (valid + b'"unterminated', "malformed CSV"),
            (valid + b"\xff", "UTF-8"),
        ]
        for contents, message in cases:
            with self.subTest(message=message, contents=contents[-40:]):
                self.path.write_bytes(contents)
                with self.assertRaisesRegex(ValueError, message):
                    load_corpus_csv(self.path)
                self.assertEqual(self.path.read_bytes(), contents)

    def test_header_only_file_has_no_invented_rows(self):
        self.write_rows([])
        self.assertEqual(load_corpus_csv(self.path), [])

    def test_import_root_must_contain_source(self):
        self.write_rows([self.example])
        with self.assertRaisesRegex(ValueError, "inside import_root"):
            load_corpus_csv(self.path, import_root=Path(self.temp.name) / "other")


if __name__ == "__main__":
    unittest.main()
