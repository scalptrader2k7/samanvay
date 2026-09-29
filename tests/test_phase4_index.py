import json
from pathlib import Path
import unittest

from candidate_retrieval import CandidateIndex

ROOT = Path(__file__).resolve().parents[1]


class IndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'output/phase3-v0.1/material_attributes.jsonl').open(encoding='utf-8') as stream:
            cls.records = [json.loads(line) for line in stream]
        cls.index = CandidateIndex(cls.records)

    def test_repeated_cross_organization_description(self):
        candidates, diagnostic = self.index.base_candidates('M000114')
        self.assertIn('M008245', candidates)
        self.assertTrue(candidates['M008245']['exact_normalized_text'])
        self.assertNotEqual(self.index.records['M000114']['source_organization'],
                            self.index.records['M008245']['source_organization'])
        self.assertNotIn('M000114', candidates)
        self.assertFalse(diagnostic['all_pairs_compared'])

    def test_exact_electrical_cables_cross_organization(self):
        candidates, _ = self.index.base_candidates('M000165')
        self.assertTrue(candidates['M017540']['exact_normalized_text'])
        self.assertTrue(candidates['M018528']['exact_normalized_text'])

    def test_useful_token_pool_is_bounded_and_explained(self):
        candidates, diagnostic = self.index.base_candidates('M000830')
        self.assertLessEqual(len(candidates), 500)
        self.assertLessEqual(len(diagnostic['selected_tokens']), 8)
        self.assertGreater(diagnostic['postings_visited'], 0)
        self.assertTrue(any(item['shared_tokens'] for item in candidates.values()))

    def test_identifier_reasons_retain_exact_field_and_value(self):
        candidates, _ = self.index.base_candidates('M000830')
        found = [reason for item in candidates.values() for reason in item['shared_identifiers']]
        self.assertTrue(any(reason['field'] == 'tender_id' and reason['value'] == '28886' for reason in found))

    def test_index_has_no_pair_matrix(self):
        self.assertFalse(hasattr(self.index, 'pairs'))
        self.assertEqual(len(self.index.records), 9245)
        self.assertLess(sum(len(v) for v in self.index.postings.values()), 9245 * 40)


if __name__ == '__main__':
    unittest.main()
