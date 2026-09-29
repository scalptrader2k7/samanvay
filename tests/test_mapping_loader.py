import csv
import json
from pathlib import Path
import tempfile
import unittest

from load_corpus import load_candidates_csv, load_mapped_csv, read_mapping, validate_mapping

ROOT = Path(__file__).resolve().parents[1]


class MappingTests(unittest.TestCase):
    def test_candidates_trace_to_corpus_without_promoting_heuristics(self):
        path = ROOT / 'data/processed/material_candidates.csv'
        before = path.read_bytes()
        with (ROOT / 'data/raw/huggingface/material_description_corpus.csv').open(encoding='utf-8', newline='') as f:
            corpus = {r['corpus_id']: r for r in csv.DictReader(f)}
        with path.open(encoding='utf-8', newline='') as f:
            source = list(csv.DictReader(f))
        records = load_candidates_csv(path, import_root=ROOT)
        self.assertEqual(len(records), 9245)
        self.assertEqual([r['raw_fields'] for r in records], source)
        for r in records:
            original = corpus[r['source_record_id']]
            for key in set(original) & set(r['raw_fields']):
                self.assertEqual(original[key], r['raw_fields'][key])
            self.assertEqual(r['category_original'], r['raw_fields']['product_category'] or None)
            self.assertEqual(r['specifications_original'], {})
            self.assertIsNone(r['source_system'])
            self.assertIsNone(r['source_section'])
            self.assertNotIn('human_label', r)
            self.assertIn('provisional_status', r['raw_fields'])
        self.assertEqual(path.read_bytes(), before)

    def test_explicit_renaming_and_supported_specification(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'renamed.csv'
            with (ROOT / 'data/raw/huggingface/material_description_corpus.csv').open(encoding='utf-8', newline='') as f:
                real = next(csv.DictReader(f))
            row = {'Original row': real['corpus_id'], 'Publisher': real['organization'],
                   'Original text': real['description'], 'Supplied spec': '', 'Extra': 'NA'}
            with path.open('w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=row); w.writeheader(); w.writerows([row, row])
            mapping = {'mapping_id': 'renamed-test-v1', 'columns': {
                'source_record_id': 'Original row', 'source_organization': 'Publisher',
                'description_original': 'Original text'}, 'identifiers': ['Original row'],
                'specifications': ['Supplied spec']}
            records = load_mapped_csv(path, mapping)
            self.assertEqual(len(records), 2)
            for r in records:
                self.assertEqual(r['raw_fields'], row)
                self.assertEqual(r['source_record_id'], real['corpus_id'])
                self.assertEqual(r['description_original'], real['description'])
                self.assertEqual(r['specifications_original'], {'Supplied spec': ''})
                self.assertIn({'field': 'specifications_original.Supplied spec', 'reason': 'blank', 'severity': 'warning'}, r['issues'])
            mapping['columns']['uom_original'] = 'Missing'
            with self.assertRaisesRegex(ValueError, 'missing mapped columns'):
                load_mapped_csv(path, mapping)

    def test_invalid_and_ambiguous_mappings_fail(self):
        bad = [None, {}, {'mapping_id': 'v1', 'columns': {'unknown': 'x'}},
               {'mapping_id': 'v1', 'columns': {'source_record_id': ['x']}},
               {'mapping_id': 'v1', 'columns': {'source_record_id': 'x', 'description_original': 'x'}},
               {'mapping_id': 'v1', 'columns': {}, 'identifiers': ['x', 'x']},
               {'mapping_id': 'v1', 'columns': {'source_organization': 'x'}, 'organization_constant': {'value': 'x', 'evidence': 'source'}},
               {'mapping_id': 'v1', 'columns': {}, 'organization_constant': {'value': 'x'}},
               {'mapping_id': 'v1', 'columns': {'legacy_material_code': 'x'}},
               {'mapping_id': 'v1', 'columns': {'description_original': 'x'}, 'specifications': ['x']}]
        for mapping in bad:
            with self.subTest(mapping=mapping), self.assertRaises(ValueError):
                validate_mapping(mapping)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'mapping.json'
            path.write_text('{"mapping_id":"v1","columns":{"description_original":"a","description_original":"b"}}')
            with self.assertRaisesRegex(ValueError, 'Duplicate mapping key'):
                read_mapping(path)

    def test_unmapped_required_fields_are_errors_without_fabricated_values(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'minimal.csv'; path.write_text('extra\nNA\n', encoding='utf-8')
            records = load_mapped_csv(path, {'mapping_id': 'empty-v1', 'columns': {}})
            self.assertFalse(records[0]['eligible_for_processing'])
            self.assertIsNone(records[0]['source_record_id'])
            self.assertEqual(records[0]['source_identifiers'], {})
            self.assertEqual(records[0]['field_origins']['source_identifiers'], {'kind': 'unmapped'})


if __name__ == '__main__':
    unittest.main()
