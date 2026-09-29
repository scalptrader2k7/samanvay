# Phase 2 ingestion and readiness

Phase 2 is complete for the documented CSV and text-cell XLSX contract. All source
rows are preserved; readiness means a row has an organization and description,
not that it is a verified material. Phase 3 has not started.

## Run from the repository root

Install `requirements.txt` into your chosen Python environment. The checks were
run with Python 3.13; the machine's default Python 3.14 lacks the Phase 1 pandas
dependency. XLSX support requires openpyxl 3.1.5 or later within major version 3.

```powershell
py -3.13 phase2_ingest.py data/raw/huggingface/material_description_corpus.csv --profile corpus --import-root . --output-dir output/phase2/new-corpus
py -3.13 phase2_ingest.py data/raw/huggingface/ntpc_material_items.csv --profile ntpc --import-root . --output-dir output/phase2/new-ntpc
py -3.13 phase2_ingest.py data/raw/huggingface/iocl_procurement_plan_items.csv --profile iocl --import-root . --output-dir output/phase2/new-iocl
py -3.13 phase2_ingest.py data/processed/material_candidates.csv --profile candidates --import-root . --output-dir output/phase2/new-candidates
```

Every destination must be new. Existing directories are refused even if empty.
Raw inputs are never written, and no loader drops or merges repeated records.
Profiles are explicit source declarations, not organization detection. Candidates
are a provisional subset of the corpus; do not add them to the raw population.

For other column names, create a JSON mapping following
[the input contract](common_input_format.md). Use `--mapping your-mapping.json`
instead of `--profile`. `examples/phase2/` includes usable mappings and real CSV
sample uploads for all four profiles.

```powershell
py -3.13 phase2_ingest.py examples/phase2/ntpc/sample.csv --mapping examples/phase2/ntpc/mapping.json --import-root . --output-dir output/phase2/sample-replay
```

For an XLSX file, also pass an exact sheet name and positive physical header row:

```powershell
py -3.13 phase2_ingest.py path/to/upload.xlsx --mapping path/to/mapping.json --sheet "Items" --header-row 1 --output-dir output/phase2/new-xlsx
```

XLSX accepts text and blank cells. Formulas, numeric cells (even quantities),
booleans, dates and error cells fail with coordinates. This prevents silently
losing identifier digits or evaluating formulas. No workbook is repaired or
converted in place. The tests construct CSV/XLSX versions of real sample rows and
verify equivalent business fields, while preserving format-specific provenance.

## Pack contents

- `records.jsonl`: every common-format record, original cells, field origins and
  validation issues; repeated records remain separate.
- `readiness.json` / `readiness.md`: per-field column presence, populated/missing
  counts, issue counts, eligibility and limitations. Missing codes/specifications
  are explicit; transaction modules remain disabled.
- `mapping.json`: exact mapping used, including organization evidence when needed.
- `sample.csv`: first five input rows (change with `--sample-size`); original
  source column names and cell values. No synthetic material records.
- `sample_provenance.json`: sample-row to original file/hash/sheet/row/identifier
  mappings. Reimporting a sample gives it new file provenance; keep this sidecar
  to trace it to the original source snapshot.
- `manifest.json`: written last, with completion status, source hash, record/sample
  counts and hashes of all other pack files.

Structural validation completes before an output directory is created. An I/O
failure while writing may leave an incomplete directory; without `manifest.json`
it is not a completed pack. Retry into a new directory. Imports are in memory,
appropriate for current files; streaming large uploads is not implemented.

Full packs generated during verification are under `output/phase2/` and ignored by
Git because they duplicate the source population. Compact checked-in evidence is
under `reports/phase2/`; the matching small upload files and provenance sidecars
are under `examples/phase2/`. Reproduce the full packs using the commands above.

## Verification

```powershell
py -3.13 -m unittest discover -s tests -v
python verify_raw_data.py
git diff --check
```

The final run passed 38 tests. Reports reconcile 21,513 corpus rows, 486 NTPC
rows, 1,224 IOCL rows and 9,245 candidate rows. All three raw hashes match
`SOURCES.md`. The public data has no confirmed legacy material-code field or
mapped structured specifications/transaction history. Human labels and genuine
sponsor material-master validation remain pending; no accuracy claim is made.
