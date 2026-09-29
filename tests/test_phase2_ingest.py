import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from openpyxl import Workbook

from input_profiles import get_profile
from load_corpus import load_mapped_csv, load_corpus_csv, load_ntpc_csv, load_iocl_csv, load_candidates_csv
from phase2_ingest import ingest

ROOT = Path(__file__).resolve().parents[1]


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def small_csv(self):
        source = ROOT / 'data/raw/huggingface/ntpc_material_items.csv'
        with source.open(encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f); headers = reader.fieldnames; row = next(reader)
        path = self.root / 'source.csv'
        with path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers); writer.writeheader(); writer.writerows([row, row])
        return path, row

    def test_report_counts_traceable_sample_and_no_overwrite(self):
        path, row = self.small_csv(); before = path.read_bytes(); output = self.root / 'pack'
        report = ingest(path, get_profile('ntpc'), output, import_root=self.root)
        self.assertEqual(report['input_rows'], 2)
        self.assertEqual(report['output_records'], 2)
        self.assertEqual(report['eligible_rows'] + report['ineligible_rows'], 2)
        self.assertEqual(report['repeated_description_rows_beyond_first'], 1)
        unit = report['fields']['uom_original']
        self.assertTrue(unit['column_present']); self.assertEqual(unit['populated_rows'], 0)
        self.assertFalse(report['fields']['legacy_material_code']['column_present'])
        self.assertEqual(report['fields']['legacy_material_code']['missing_rows'], 2)
        self.assertEqual(report['readiness']['specifications'], 'missing')
        self.assertFalse(report['readiness']['transaction_modules_enabled'])
        with (output / 'sample.csv').open(encoding='utf-8', newline='') as f:
            self.assertEqual(list(csv.DictReader(f)), [row, row])
        locators = json.loads((output / 'sample_provenance.json').read_text())
        self.assertEqual([r['source_row'] for r in locators], [1, 2])
        self.assertEqual([r['sample_row'] for r in locators], [1, 2])
        self.assertTrue(all(r['source_sha256'] == hashlib.sha256(before).hexdigest() for r in locators))
        manifest = json.loads((output / 'manifest.json').read_text())
        for file, digest in manifest['artifact_sha256'].items():
            self.assertEqual(hashlib.sha256((output / file).read_bytes()).hexdigest(), digest)
        saved = {p.name: p.read_bytes() for p in output.iterdir()}
        with self.assertRaises(FileExistsError):
            ingest(path, get_profile('ntpc'), output)
        self.assertEqual(saved, {p.name: p.read_bytes() for p in output.iterdir()})
        self.assertEqual(path.read_bytes(), before)

    def test_invalid_input_does_not_create_pack(self):
        path, _ = self.small_csv(); path.write_bytes(path.read_bytes() + b'too,few\n')
        with self.assertRaises(ValueError):
            ingest(path, get_profile('ntpc'), self.root / 'invalid')
        self.assertFalse((self.root / 'invalid').exists())

    def test_empty_file_report_retains_header_presence(self):
        path, _ = self.small_csv()
        header = path.read_text().splitlines()[0]
        path.write_text(header + '\n')
        report = ingest(path, get_profile('ntpc'), self.root / 'empty')
        self.assertEqual(report['input_rows'], 0)
        self.assertTrue(report['fields']['uom_original']['column_present'])
        self.assertEqual(report['fields']['uom_original']['missing_rows'], 0)

    def test_cli_csv_and_xlsx_packs(self):
        path, row = self.small_csv()
        book = Workbook(); sheet = book.active; sheet.title = 'Items'
        sheet.append(list(row)); sheet.append(list(row.values())); sheet.append(list(row.values()))
        xlsx = self.root / 'source.xlsx'; book.save(xlsx); book.close()
        mapping_path = self.root / 'custom.json'
        mapping_path.write_text(json.dumps(get_profile('ntpc')))
        reports = []
        for index, (source, flags) in enumerate([
            (path, ['--profile', 'ntpc']),
            (xlsx, ['--mapping', str(mapping_path), '--sheet', 'Items', '--header-row', '1'])]):
            output = self.root / f'cli{index}'
            command = [sys.executable, str(ROOT / 'phase2_ingest.py'), str(source), *flags,
                       '--output-dir', str(output), '--import-root', str(self.root)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            reports.append(json.loads((output / 'readiness.json').read_text()))
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        for key in ('input_rows', 'fields', 'issues', 'readiness'):
            self.assertEqual(reports[0][key], reports[1][key])

    def test_serializable_profiles_match_existing_apis(self):
        sources = [('corpus', 'data/raw/huggingface/material_description_corpus.csv', load_corpus_csv),
                   ('ntpc', 'data/raw/huggingface/ntpc_material_items.csv', load_ntpc_csv),
                   ('iocl', 'data/raw/huggingface/iocl_procurement_plan_items.csv', load_iocl_csv),
                   ('candidates', 'data/processed/material_candidates.csv', load_candidates_csv)]
        for name, path, loader in sources:
            with self.subTest(profile=name):
                self.assertEqual(load_mapped_csv(ROOT / path, get_profile(name)), loader(ROOT / path))


if __name__ == '__main__':
    unittest.main()
