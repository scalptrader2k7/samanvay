import json
from pathlib import Path
import unittest

from candidate_retrieval import CandidateIndex

ROOT = Path(__file__).resolve().parents[1]


class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'output/phase3-v0.1/material_attributes.jsonl').open(encoding='utf-8') as stream:
            cls.records = [json.loads(line) for line in stream]
        cls.index = CandidateIndex(cls.records)

    def ids(self, query, top_k=20, **kwargs):
        results, diagnostic = self.index.retrieve(query, top_k=top_k, **kwargs)
        return [r['candidate_source_record_id'] for r in results], results, diagnostic

    def test_exact_repeat_is_first_and_candidate_only(self):
        ids, results, diagnostic = self.ids('M000114', cross_organization_only=True)
        self.assertEqual(ids[0], 'M008245')
        self.assertEqual(results[0]['status'], 'candidate_only')
        self.assertEqual(results[0]['retrieval_score'], 1.0)
        self.assertTrue(any(r['method'] == 'exact_normalized_text' for r in results[0]['reasons']))
        self.assertLessEqual(diagnostic['fuzzy_comparisons'], 500)

    def test_near_formatting_pipe_variant_is_retrieved(self):
        ids, results, _ = self.ids('M000753', top_k=20)
        self.assertIn('M000925', ids)
        result = results[ids.index('M000925')]
        self.assertTrue(any(r['method'] == 'fuzzy_character_trigrams' for r in result['reasons']))

    def test_different_size_candidate_is_proposed_without_decision(self):
        ids, results, _ = self.ids('M000830', top_k=30)
        self.assertIn('M000834', ids)
        candidate = results[ids.index('M000834')]
        self.assertEqual(candidate['status'], 'candidate_only')
        self.assertNotIn('decision', candidate)
        self.assertNotIn('match', candidate)
        sizes = [x['value_normalized'] for x in candidate['candidate_attributes']['size_dimension']]
        self.assertIn('240MM2', sizes)

    def test_top_k_is_deterministic_limited_and_validated(self):
        first, _, _ = self.ids('M000830', top_k=7)
        second, _, _ = self.ids('M000830', top_k=7)
        self.assertEqual(first, second)
        self.assertLessEqual(len(first), 7)
        for invalid in (True, 0, 51, 1.5):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.index.retrieve('M000830', top_k=invalid)


if __name__ == '__main__':
    unittest.main()
