# Common input record contract v0.1

This is the Phase 2 ingestion specification. `load_corpus.py` implements the fixed
raw corpus, NTPC extracted-item and IOCL procurement-plan CSV profiles. It maps source fields without changing their wording or
assigning material identities, producing one JSON-compatible record per parsed input row. CSV and
XLSX remain input formats; nested provenance is not flattened into invented codes.

## Record fields

Every record contains all the keys below. Optional source values are strings or
`null`. No numeric coercion, trimming, case folding, unit conversion or inferred
specification is allowed during ingestion. The schema version is `0.1`.

| Key | Type | Meaning |
|---|---|---|
| `schema_version` | string | `0.1` |
| `source_file` | string | Input path relative to the import root; retain the original filename. |
| `source_sha256` | string | SHA-256 of the untouched input bytes. |
| `source_sheet` | string or null | Exact XLSX sheet name; null for CSV. |
| `source_row` | positive integer | CSV data-record ordinal starting at 1, excluding header (not physical line number); XLSX physical worksheet row number. |
| `mapping_id` | string | Versioned mapping profile, including declared constants; ingestion metadata, not a material code. |
| `source_organization` | string or null | Organization column or documented source-profile constant. |
| `source_record_id` | string or null | Existing row ID where supplied; never substitute a generated ID or tender reference. |
| `source_identifiers` | object of strings | Available original identifier/locator columns keyed by their exact names, including blanks. Never concatenate them into a purported material code. |
| `legacy_material_code` | string or null | Only an explicitly supplied material-master code with documented source meaning. |
| `description_original` | string or null | Exact primary description cell. |
| `uom_original` | string or null | Exact source unit; does not imply a base/order UOM or a conversion. |
| `category_original` | string or null | Explicit source category, not an inferred family or human label. |
| `specifications_original` | object of strings | Explicitly mapped technical columns only, retaining original column names and values; empty object when absent. |
| `source_system` | string or null | Explicit source system; no inference from a URL. |
| `source_section` | string or null | Exact section column. |
| `source_url` | string or null | Exact source URL. |
| `document_reference` | string or null | Original document URL/path/name; do not resolve or fabricate URLs. |
| `quantity_original` | string or null | Original quantity text; a procurement-plan quantity does not establish actual consumption. |
| `raw_fields` | object of strings | Every original header and decoded cell, including unrecognized fields and empty strings. Raw files remain the byte-level authority. |
| `field_origins` | object | Each mapped business field records `{kind: column, name: <header>}`, `{kind: constant, value: <value>, evidence: <source>}`, or `{kind: unmapped}`. For identifier/specification objects, record origins per member. |
| `issues` | array of objects | Each issue has `field`, `reason` and `severity`; use the rules below. No match scores or labels. |
| `eligible_for_processing` | boolean | False when any issue has severity `error`; true otherwise. This denotes input readiness only, not a verified material or match. |

The tuple `(source_file, source_sha256, source_sheet, source_row)` locates a source
row in a particular snapshot; it is not a material identity and need not be stable
after the source file changes. Repeated descriptions and identifiers remain separate
rows. Never deduplicate imports by description or by an assumed global ID.

## Current source mappings

Select the known source explicitly with `load_corpus_csv`, `load_ntpc_csv` or
`load_iocl_csv`. Their mapping IDs are `raw-corpus-v0.1`, `raw-ntpc-v0.1` and
`raw-iocl-v0.1`. The functions do not detect an organization from a filename or
description. Use NTPC/IOCL profiles only for those documented sources; their
organization constants are mapping metadata, not values found in the input row.
Each call preserves its own file/row provenance and performs no cross-file merge.
The candidate-file profile is `load_candidates_csv` (`material-candidates-v0.1`).
It leaves omitted system/section fields unmapped. `load_mapped_csv` accepts an
explicit mapping object; `read_mapping` reads it from JSON and rejects duplicate keys.

The corpus and candidates share the mappings in the second column except where
noted. A dash means **unmapped**, not a placeholder value. Profile constants must
carry an origin citing `SOURCES.md` sections 2.2/2.3. They describe the provenance of
these known files, not an organization inferred for arbitrary uploads.

| Target | Corpus / candidates | NTPC extracted items | IOCL procurement plan |
|---|---|---|---|
| `source_organization` | `organization` | constant `NTPC Limited` | constant `Indian Oil Corporation Limited` |
| `source_record_id` | `corpus_id` | - | - |
| `source_identifiers` | `corpus_id`, `tender_reference`, `tender_id` | `nit_id`, `doc_name`, `line_no` | `source_pdf`, `page`, `sl_no` |
| `legacy_material_code` | - | - | - |
| `description_original` | `description` | `item_text` | `item_description` |
| `uom_original` | `unit` | `unit` | `unit` |
| `category_original` | `product_category` | - | - |
| `specifications_original` | empty object | empty object | empty object |
| `source_system` | `source_system` (corpus only) | - | - |
| `source_section` | `source_section` (corpus only) | - | `section` |
| `source_url` | `source_url` | - | - |
| `document_reference` | `document_url` | `doc_name` | `source_pdf` |
| `quantity_original` | `quantity` | `quantity` | `quantity` |

All columns are also retained in `raw_fields`. In particular, `description_kind`,
`item_type_hint`, `location`, `pattern`, `row_raw`, and `estimated_value_rs_crores`
must survive. IOCL `section` is a source section, not a material category.
NTPC `pattern` is extraction metadata. Neither is promoted to a human label.

Candidate-only fields `major_item_category`, the seven `has_*` columns,
`classification_reason` and `provisional_status` remain in `raw_fields` as Phase 1
derived metadata. They are not supplied technical values or validated labels.
Candidate records can be traced to the corpus by `corpus_id`; this version does
not silently fill the omitted system/section fields by joining another file.
Review sheets and `sample_records.csv` are audit/review outputs, not default
ingestion sources. The sample generator's constructed `record_id` values must not
be treated as source material codes.

## Missing values and validation

- An unmapped scalar field becomes `null` with reason `unmapped` in `issues`.
  A mapped empty/whitespace-only cell becomes `null` with reason `blank`; its exact
  contents remain in `raw_fields`. Empty specification/identifier objects get an
  `unmapped` issue when no columns were mapped. Blank mapped object members remain
  exact strings and get individual `blank` issues.
- All other text, including literal `NA`, `N/A`, `null`, `0`, leading zeros and
  surrounding whitespace, is retained verbatim. Do not apply pandas default NA
  inference. A supplied mapping can later declare source-specific null tokens,
  but must version and record that choice.
- Missing organization or description is an `error`; retain the traceable row
  with issues for reporting, but mark it ineligible for downstream processing.
  Other missing business fields are `warning`s. Missing legacy codes are expected
  for current surrogates and do not prevent ingestion.
- Duplicate source IDs are warnings, not permission to drop/merge rows. Blank or
  absent IDs use snapshot/row provenance; never fabricate a replacement ID.
  The corpus loader uses reason `duplicate` on every occurrence of a repeated
  nonblank ID, comparing exact values without normalization.
- Unreadable encoding, duplicate/empty headers, wrong CSV row width, nonexistent
  mapped columns, ambiguous mappings or an unspecified XLSX sheet/header must fail
  clearly before producing a successful import. The current CSV profiles use
  UTF-8 (optional BOM), comma delimiter and standard CSV quoting. Other encodings
  require an explicit option, never lossy decoding.
  Each fixed profile requires every mapped column to exist; missing columns
  are structural errors, while empty cells are retained as row-level issues.
  A header-only file returns no records. A blank physical row outside a quoted
  field fails the width check rather than silently disappearing.
- XLSX must preserve text identifiers; formulas, numeric identifiers with ambiguous
  formatting and unsupported cell types require explicit issues or a decision,
  not guessed lost digits or silent string conversion. The XLSX policy below deliberately rejects non-text cells rather than converting them.
- No structured specification columns exist in these current inputs. Do not
  extract them from descriptions in Phase 2; that is Phase 3. Retain future
  explicitly mapped technical columns without interpreting their values.
- Report field presence separately from populated-row counts. No current input
  provides PR/PO/stock/issue history. IOCL estimated values and planned quantities
  do not unlock transaction, savings or obsolescence claims.

## Inspected snapshot and code implications

Counts below were measured from local CSVs with `csv.DictReader`; a populated cell
has non-whitespace text. These are completeness counts, not accuracy measurements.

| File | Rows | Columns | Populated description | Populated unit | Populated quantity | Populated source category |
|---|---:|---:|---:|---:|---:|---:|
| `data/raw/huggingface/material_description_corpus.csv` | 21,513 | 15 | 21,513 | 397 | 484 | 12,758 |
| `data/raw/huggingface/ntpc_material_items.csv` | 486 | 7 | 486 | 0 | 0 | absent |
| `data/raw/huggingface/iocl_procurement_plan_items.csv` | 1,224 | 9 | 1,224 | 928 | 1,123 | absent |
| `data/processed/material_candidates.csv` | 9,245 | 23 | 9,245 | 391 | 474 | 5,082 |

The 23,223 raw rows include overlapping extraction stages, not 23,223 distinct
materials. Candidates are a provisional corpus subset, not an additional source
population. None of the four files has a confirmed legacy material-code field.

`profile_data.py` has file-specific description mappings and reads pandas strings
with default NA conversion. `curate_material_candidates.py` generates heuristic
flags and selects 23 columns, omitting `source_system` and `source_section`.
`review_classification.py` demonstrates lossless CSV string reading and header/
row-shape checks, while protecting reviewer fields. `verify_raw_data.py` checks
the three raw hashes against `SOURCES.md`. Phase 2 must add a separate loader;
the completed Phase 1 generators need not change.

## Planning references and scope

Read from the user-supplied `Samanvay_Master_Phase_Plan (2).docx` (Phase 2 Common
input schema and readiness; Ralph-loop workflow) and
`CPSE_Material_Harmonization_Research_Blueprint.pdf` (pages 8-9, input fields and
readiness; pages 14-15, provenance). They are reference material. Their suggested
build schedules, synthetic examples, sample codes and future features are not
instructions to execute in this iteration. The user's one-task scope controls.

The blueprint cites a different Hugging Face account from the acquired snapshot.
For these local bytes, retain the existing `SOURCES.md` download provenance and
hashes; do not silently replace it with the blueprint's source URL.

## Explicit mapping configuration

A mapping object has a nonblank versioned `mapping_id`, `columns` (target scalar
field to exact header), optional `identifiers` and `specifications` (lists of
exact headers), and optional `organization_constant` with `value` and `evidence`.
All listed headers must exist. Scalar targets must be unique and a source column
cannot feed multiple scalar targets. Identifier columns may also feed a scalar
field (e.g. a row ID); specification columns cannot overlap those roles. Unknown
keys, conflicting constants, duplicate entries and ambiguous mappings fail.
A legacy-code column requires `legacy_code_evidence` describing its source meaning.
No default legacy-code mapping exists for the public data. Users must version
mapping IDs when changing a mapping; origins record every mapped field.

Example for explicitly renamed corpus columns (not new source data):

```json
{"mapping_id":"renamed-corpus-v1","columns":{"source_record_id":"Original row","source_organization":"Publisher","description_original":"Original text"},"identifiers":["Original row"]}
```

Omitted fields stay unmapped; missing organization/description gives row-level
errors. A mapped header absent from the file is a structural error. Candidate
heuristic columns remain untouched in `raw_fields`; they do not become supplied
specifications, human annotations or measured accuracy.

## XLSX adapter policy

`load_xlsx.load_mapped_xlsx(path, mapping, sheet=..., header_row=...,
import_root=...)` requires an exact sheet name and a positive physical header row.
It uses the same mapping/record contract, with physical worksheet row numbers and
the input workbook hash. Every row after the selected header through the used
range is retained, including blank rows (which receive missing-field errors).

This version supports text cells and blanks only, preserving text identifiers and
leading zeros. Formulas, error cells, numeric values (including formatted numeric
IDs), booleans and dates fail with a worksheet/cell coordinate before any records
are returned. No cached formula value, number formatting or lost digits are
silently converted. Upload explicit source text; this adapter never repairs or
rewrites workbooks. Other worksheets are not ingested implicitly. Headers must
be nonblank and unique across the used column range. This conservative limitation
also applies to numeric quantities; broader typed-cell support is future work.
`openpyxl>=3.1.5,<4` is required; the checked runtime already had 3.1.5 installed.
