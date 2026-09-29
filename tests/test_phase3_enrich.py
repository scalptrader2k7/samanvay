import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from phase3_attributes import assert_evidence_integrity
from phase3_enrich import enrich

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/processed/material_candidates.csv'


class EnrichTests(unittest.TestCase):
    def test_full_pack_reconciles_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'pack'; before = SOURCE.read_bytes()
            report = enrich(SOURCE, output, import_root=ROOT)
            self.assertEqual(report['input_rows'], 9245)
            self.assertEqual(report['output_rows'], 9245)
            self.assertEqual(report['dropped_rows'], 0)
            records = [json.loads(line) for line in (output / 'material_attributes.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(records), 9245)
            self.assertEqual(len({r['source_record_id'] for r in records}), 9245)
            for record in records:
                assert_evidence_integrity(record)
            examples = {r['source_record_id']: r for r in json.loads((output / 'examples.json').read_text())}
            self.assertEqual(examples['M000114']['attributes']['model_part'], [])
            self.assertNotEqual(examples['M010407']['attributes']['pressure'][0]['value_normalized'],
                                examples['M003626']['attributes']['pressure'][0]['value_normalized'])
            manifest = json.loads((output / 'manifest.json').read_text())
            for name, digest in manifest['artifacts'].items():
                self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), digest)
            with self.assertRaises(FileExistsError):
                enrich(SOURCE, output)
            self.assertEqual(SOURCE.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
