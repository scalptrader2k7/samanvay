from pathlib import Path
import unittest

from load_corpus import load_candidates_csv
from phase3_attributes import assert_evidence_integrity, derive_description

ROOT = Path(__file__).resolve().parents[1]


class AttributeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {r['source_record_id']: r for r in load_candidates_csv(ROOT / 'data/processed/material_candidates.csv')}

    def values(self, source_id, kind):
        result = derive_description(self.source[source_id])
        assert_evidence_integrity(result)
        return [v['value_normalized'] for v in result['attributes'][kind]]

    def test_pipe_values_have_exact_source_evidence(self):
        self.assertEqual(self.values('M000753', 'standard'), ['ASTM A312'])
        self.assertEqual(self.values('M000753', 'size_dimension'), ['9.53MM', '141.3MM', '125NB'])
        self.assertIn('A312-TP304L', self.values('M000913', 'material_grade'))
        self.assertIn('80S', self.values('M000913', 'size_dimension'))

    def test_valve_standard_size_pressure_and_conflicts_stay_separate(self):
        first = derive_description(self.source['M010407'])
        second = derive_description(self.source['M003626'])
        self.assertEqual([x['value_normalized'] for x in first['attributes']['standard']], ['API 6D'])
        self.assertEqual([x['value_normalized'] for x in first['attributes']['pressure']], ['300 CLASS'])
        self.assertEqual([x['value_normalized'] for x in second['attributes']['pressure']], ['5000 PSI'])
        self.assertNotEqual(first['attributes']['pressure'][0]['value_normalized'], second['attributes']['pressure'][0]['value_normalized'])
        assert_evidence_integrity(first); assert_evidence_integrity(second)

    def test_exact_identity_conflict_examples_retain_different_values(self):
        pipe_a = self.values('M000913', 'size_dimension')
        pipe_b = self.values('M000927', 'size_dimension')
        cable_a = self.values('M000830', 'size_dimension')
        cable_b = self.values('M000834', 'size_dimension')
        self.assertIn('15MM', pipe_a); self.assertIn('25MM', pipe_b)
        self.assertIn('150MM2', cable_a); self.assertIn('240MM2', cable_b)
        self.assertNotEqual(set(pipe_a), set(pipe_b))
        self.assertNotEqual(set(cable_a), set(cable_b))

    def test_cable_voltage_is_not_power_current_or_frequency(self):
        self.assertEqual(self.values('M000830', 'voltage'), ['11KV'])
        self.assertIn('150MM2', self.values('M000830', 'size_dimension'))
        values = self.values('M000921', 'voltage')
        self.assertEqual(values, ['6.6KV'])
        description = self.source['M000921']['description_original']
        for excluded in ('750KW',):
            self.assertNotIn(excluded, values)
            self.assertIn(excluded, description)

    def test_pump_model_and_standard_require_explicit_text(self):
        self.assertEqual(self.values('M000041', 'standard'), ['API 610'])
        models = self.values('M015553', 'model_part')
        self.assertEqual(models, ['MODEL NAT 12 P 160'])
        self.assertEqual(self.values('M000114', 'model_part'), [])

    def test_missing_and_uncertain_values_remain_empty(self):
        result = derive_description(self.source['M000114'])
        self.assertEqual(result['family'], 'pump')
        self.assertTrue(all(not values for values in result['attributes'].values()))
        result = derive_description(self.source['M000795'])
        self.assertEqual(result['voltage'] if 'voltage' in result else None, None)
        self.assertEqual([x['value_normalized'] for x in result['attributes']['voltage']], ['33KV', '33KV'])

    def test_all_candidate_attribute_spans_are_exact_and_ids_unchanged(self):
        for source_id, source in self.source.items():
            result = derive_description(source)
            self.assertEqual(result['source_record_id'], source_id)
            self.assertEqual(result['description_original'], source['description_original'])
            assert_evidence_integrity(result)


if __name__ == '__main__':
    unittest.main()
