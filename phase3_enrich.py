"""Produce a no-overwrite Phase 3 enrichment pack from candidate input records."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from load_corpus import load_candidates_csv
from phase3_attributes import assert_evidence_integrity, derive_description

EXAMPLE_IDS = ('M000753', 'M000913', 'M010407', 'M003626', 'M000830',
               'M000921', 'M000041', 'M015553', 'M000114', 'M000342')


def enrich(input_path, output_dir, *, import_root=None):
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    input_path = Path(input_path)
    before = input_path.read_bytes()
    records = load_candidates_csv(input_path, import_root=import_root)
    enriched = []
    for record in records:
        result = derive_description(record)
        assert_evidence_integrity(result)
        enriched.append(result)
    if input_path.read_bytes() != before:
        raise ValueError("Input changed during enrichment; no output written")
    if len(enriched) != len(records) or [r['source_record_id'] for r in enriched] != [r['source_record_id'] for r in records]:
        raise ValueError("Output row/identifier reconciliation failed")
    if any(a['description_original'] != b['description_original'] for a, b in zip(enriched, records)):
        raise ValueError("Original description preservation failed")

    family = Counter(r['family'] or 'unknown' for r in enriched)
    coverage = {kind: sum(bool(r['attributes'][kind]) for r in enriched)
                for kind in next(iter(enriched))['attributes']} if enriched else {}
    examples = [r for r in enriched if r['source_record_id'] in EXAMPLE_IDS]
    report = {
        'phase': '3', 'status': 'complete', 'input_sha256': hashlib.sha256(before).hexdigest(),
        'input_rows': len(records), 'output_rows': len(enriched), 'dropped_rows': 0,
        'source_ids_preserved': True, 'original_descriptions_preserved': True,
        'family_counts': dict(sorted(family.items())), 'attribute_record_coverage': coverage,
        'example_ids': [r['source_record_id'] for r in examples],
        'limitations': [
            'Coverage counts are rule outputs, not extraction accuracy.',
            'No human-labeled attribute gold set is available.',
            'Unknown and ambiguous values remain unfilled.',
            'Rules are intentionally narrow and do not convert units or expand abbreviations.',
            'Family/attributes are derived evidence, not source master data.',
            'No candidate matching or equivalence decision is performed.',
        ],
    }
    output.mkdir(parents=True, exist_ok=False)
    with (output / 'material_attributes.jsonl').open('x', encoding='utf-8', newline='\n') as stream:
        for record in enriched:
            stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')
    for name, value in [('report.json', report), ('examples.json', examples)]:
        with (output / name).open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')
    artifacts = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
    with (output / 'manifest.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump({'status': 'complete', 'artifacts': artifacts}, stream, indent=2); stream.write('\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', default='data/processed/material_candidates.csv')
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--import-root', default='.')
    args = parser.parse_args()
    try:
        report = enrich(args.input, args.output_dir, import_root=args.import_root)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Phase 3 failed: {exc}\n')
    print(f"Enriched {report['output_rows']} records into {args.output_dir}")


if __name__ == '__main__':
    main()
