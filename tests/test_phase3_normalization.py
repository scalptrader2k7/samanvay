import csv
from pathlib import Path
import unittest

from load_corpus import load_candidates_csv
from phase3_attributes import assert_evidence_integrity, derive_description, normalize_description

ROOT = Path(__file__).resolve().parents[1]


class NormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {r['source_record_id']: r for r in load_candidates_csv(ROOT / 'data/processed/material_candidates.csv')}

    def test_real_single_family_examples_preserve_identity_and_description(self):
        expected = {'M000753': 'pipe', 'M002735': 'valve', 'M000830': 'cable', 'M000041': 'pump'}
        for source_id, family in expected.items():
            with self.subTest(source_id=source_id):
                source = self.records[source_id]
                before = dict(source)
                result = derive_description(source)
                self.assertEqual(source, before)
                self.assertEqual(result['source_record_id'], source_id)
                self.assertEqual(result['source_identifiers'], source['source_identifiers'])
                self.assertEqual(result['description_original'], source['description_original'])
                self.assertEqual(result['family'], family)
                assert_evidence_integrity(result)

    def test_ambiguous_and_unknown_families_stay_unknown(self):
        for source_id in ('M000342', 'M000093'):
            result = derive_description(self.records[source_id])
            self.assertIsNone(result['family'])
            self.assertIsNone(result['family_evidence'])
            self.assertEqual(result['derivation_issues'][0]['reason'], 'ambiguous_family')
            assert_evidence_integrity(result)
        result = derive_description(self.records['M000001'])
        self.assertIsNone(result['family'])
        self.assertEqual(result['derivation_issues'], [])

    def test_normalization_is_deterministic_idempotent_and_conservative(self):
        cases = {
            '  CABLE,PWR,240MM2,1C\r\n11KV  ': 'CABLE, PWR, 240MM2, 1C 11KV',
            'Gate Valve, 2" x 300 Class, API 6D': 'Gate Valve, 2" x 300 Class, API 6D',
            'A2  X  3': 'A2 X 3',
            '10X20 MM': '10 x 20 MM',
        }
        for raw, expected in cases.items():
            actual = normalize_description(raw)
            self.assertEqual(actual, expected)
            self.assertEqual(normalize_description(actual), actual)

    def test_all_candidates_preserve_originals_and_valid_family_spans(self):
        for source in self.records.values():
            result = derive_description(source)
            self.assertEqual(result['description_original'], source['description_original'])
            self.assertEqual(result['source_record_id'], source['source_record_id'])
            assert_evidence_integrity(result)


if __name__ == '__main__':
    unittest.main()
