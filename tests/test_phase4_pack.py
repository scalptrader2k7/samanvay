import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from phase4_retrieve import generate

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'output/phase3-v0.1/material_attributes.jsonl'


class PackTests(unittest.TestCase):
    def test_full_pack_reconciles_is_bounded_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'pack'; before = SOURCE.read_bytes()
            report = generate(SOURCE, output, top_k=10)
            self.assertEqual(report['query_records'], 9245)
            self.assertEqual(report['output_query_records'], 9245)
            self.assertLessEqual(report['candidate_pool']['maximum'], 500)
            self.assertLessEqual(report['comparisons']['maximum_per_query'], 500)
            self.assertFalse(report['comparisons']['all_pairs_compared'])
            self.assertEqual(report['example_coverage']['found'], report['example_coverage']['total'])
            self.assertFalse(report['semantic_retrieval']['enabled'])
            rows = [json.loads(line) for line in (output / 'candidates.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(rows), 9245)
            self.assertEqual(len({r['query_source_record_id'] for r in rows}), 9245)
            self.assertTrue(all(len(r['candidates']) <= 10 for r in rows))
            self.assertTrue(all(c['status'] == 'candidate_only' for r in rows for c in r['candidates']))
            manifest = json.loads((output / 'manifest.json').read_text())
            for name, digest in manifest['artifacts'].items():
                self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), digest)
            with self.assertRaises(FileExistsError):
                generate(SOURCE, output)
            self.assertEqual(SOURCE.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
