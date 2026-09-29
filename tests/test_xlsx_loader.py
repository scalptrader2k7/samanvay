"""Temporary XLSX transport fixtures; no source workbook is rewritten."""
import csv
import hashlib
from pathlib import Path
import tempfile
import unittest

from openpyxl import Workbook

from load_corpus import CORPUS_COLUMNS, IDENTIFIER_COLUMNS, load_mapped_csv
from load_xlsx import load_mapped_xlsx

ROOT = Path(__file__).resolve().parents[1]
MAPPING = {'mapping_id': 'raw-corpus-v0.1', 'columns': CORPUS_COLUMNS,
           'identifiers': list(IDENTIFIER_COLUMNS)}


class XlsxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        with (ROOT / 'data/raw/huggingface/material_description_corpus.csv').open(encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f); self.headers = reader.fieldnames
            self.rows = [next(reader) for _ in range(3)]

    def workbook(self):
        book = Workbook(); sheet = book.active; sheet.title = 'Source rows'
        sheet.append(['Import example'])
        sheet.append(self.headers)
        for row in self.rows:
            sheet.append([row[h] for h in self.headers])
        return book, sheet

    def test_csv_xlsx_real_sample_equivalence_and_provenance(self):
        csv_path = self.root / 'sample.csv'; xlsx_path = self.root / 'sample.xlsx'
        with csv_path.open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=self.headers); w.writeheader(); w.writerows(self.rows)
        book, sheet = self.workbook(); book.save(xlsx_path); book.close()
        before = xlsx_path.read_bytes()
        csv_records = load_mapped_csv(csv_path, MAPPING)
        records = load_mapped_xlsx(xlsx_path, MAPPING, sheet='Source rows', header_row=2)
        self.assertEqual(len(records), 3)
        for c, x in zip(csv_records, records):
            for key in set(c) - {'source_file', 'source_sha256', 'source_sheet', 'source_row'}:
                self.assertEqual(c[key], x[key], key)
            self.assertEqual(x['source_row'], c['source_row'] + 2)
            self.assertEqual(x['source_sheet'], 'Source rows')
            self.assertEqual(x['source_sha256'], hashlib.sha256(before).hexdigest())
        self.assertEqual(xlsx_path.read_bytes(), before)

    def test_text_leading_zeros_repeated_and_blank_rows(self):
        self.rows[0]['corpus_id'] = '000012'
        self.rows[0]['description'] = ' NA\nN/A '
        self.rows = [self.rows[0], dict.fromkeys(self.headers, ''), self.rows[0]]
        book, sheet = self.workbook(); path = self.root / 'text.xlsx'; book.save(path); book.close()
        records = load_mapped_xlsx(path, MAPPING, sheet='Source rows', header_row=2)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]['source_record_id'], '000012')
        self.assertEqual(records[0]['raw_fields'], self.rows[0])
        self.assertEqual(records[2]['raw_fields'], self.rows[0])
        self.assertFalse(records[1]['eligible_for_processing'])
        self.assertEqual([r['source_row'] for r in records], [3, 4, 5])

    def test_formulas_numeric_ids_and_other_typed_cells_are_rejected(self):
        for value, fmt, expected in [('=1+1', 'General', 'formula'), (12, '000000', 'non-text'),
                                     (True, 'General', 'non-text'), ('#VALUE!', 'General', 'non-text')]:
            with self.subTest(value=value):
                book, sheet = self.workbook(); sheet['A3'] = value; sheet['A3'].number_format = fmt
                path = self.root / 'typed.xlsx'; book.save(path); book.close()
                before = path.read_bytes()
                with self.assertRaisesRegex(ValueError, f'Source rows!A3: {expected}'):
                    load_mapped_xlsx(path, MAPPING, sheet='Source rows', header_row=2)
                self.assertEqual(path.read_bytes(), before)

    def test_explicit_sheet_header_and_schema_validation(self):
        book, sheet = self.workbook(); path = self.root / 'invalid.xlsx'; book.save(path)
        for name, header in [(None, 2), ('Missing', 2), ('Source rows', None), ('Source rows', 0), ('Source rows', True), ('Source rows', 100), ('Source rows', 1)]:
            with self.subTest(sheet=name, header=header), self.assertRaises(ValueError):
                load_mapped_xlsx(path, MAPPING, sheet=name, header_row=header)
        sheet['B2'] = sheet['A2'].value; book.save(path); book.close()
        with self.assertRaisesRegex(ValueError, 'Duplicate worksheet headers'):
            load_mapped_xlsx(path, MAPPING, sheet='Source rows', header_row=2)


if __name__ == '__main__':
    unittest.main()
