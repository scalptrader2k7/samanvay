# Phase 2 progress

Read this log and `../PHASE2.md` before selecting the next task. Limit: one task per
iteration. Current authorization permits continuing through P2-06 after recording
each task result; stop at Phase 2 completion or a blocker requiring user input.

## 2026-09-27 Iteration 1

- Selected task: P2-01, common input contract and current column map.
- Starting state: clean working tree at `fd9a613`; Phase 1A-1C complete. No
  `AGENTS.md` found in the repository or checked workspace ancestor directories.
- Read both supplied planning documents and inspected repository documentation,
  Python data/review scripts, existing tests and all 12 CSV headers.
- Added the Phase 2 task list and `common_input_format.md` v0.1: original-value
  fields, snapshot/row provenance, explicit source mappings and missing-data rules.
  No loader, normalization, matching, labels or frontend was implemented.
- Result: P2-01 complete. Stopped after this task; Phase 2 as a whole is unfinished.
- Verification:
  - Read-only Python `csv.DictReader` inspection covered all 12 CSV headers.
    Assertions passed for the contract's four row/column counts, description,
    unit, quantity and category coverage, unique headers and consistent row widths.
    Raw counts: 21,513 / 486 / 1,224; candidate count: 9,245.
  - Corpus and candidate `corpus_id` values are nonblank and unique within each
    file. All 9,245 candidate IDs exist in the raw corpus; every shared source
    cell matches exactly. Review-sheet and batch human fields remain blank.
  - `python verify_raw_data.py`: all three SHA-256 checks passed.
  - `py -3.13 -m unittest discover -s tests -v`: all 15 existing tests passed.
    Initial default-Python (3.14) attempt could not import pandas; installed
    Python 3.13 already has pandas 3.0.1 / numpy 2.4.3. No packages were installed.
    Any synthetic labels inside existing tests were confined to temporary fixtures.
  - `git diff --exit-code -- data reports SOURCES.md LABELING_GUIDE.md`: passed;
    preserved tracked datasets, identifiers, reports, review sheets and provenance.
  - `git diff --check`: passed. Only the README and three new Markdown documents
    changed; no application code or data artifacts changed.
- Next task: P2-02, read-only raw-corpus CSV loader with preservation and validation
  checks. Read this log, the task list and contract first.
- Blockers for P2-01: none. Sponsor material codes and transaction history are
  absent; human labels remain pending. They limit later claims but do not block
  the next surrogate-ingestion task. Context/frontend skill names are not supplied.

## 2026-09-27 Iteration 2

- Selected task: P2-02 only. Read this log first, then the task list, contract and
  existing CSV reader/tests. Prior iteration's README and new planning documents
  were still uncommitted; retained that work. No repository `AGENTS.md` found.
- Added `load_corpus.py` with `load_corpus_csv(path, import_root=...)`, using only
  the Python standard library. It reads one immutable byte snapshot, hashes it,
  validates the full CSV before returning records, and writes no files.
- The fixed raw-corpus profile preserves every input cell in `raw_fields`, exact
  identifiers/descriptions/provenance, source order and repeated descriptions.
  Unknown columns also survive. No material codes, labels or specifications are
  inferred. All duplicate nonblank IDs receive warnings and remain separate rows.
- Blank values and unmapped fields receive distinct issues/origins. Rows lacking
  organization or description remain present with errors. Documented the explicit
  `eligible_for_processing` boolean required to mark those rows ineligible; it is
  not evidence of material suitability. Missing mapped headers fail structurally.
- Added six focused tests in `tests/test_corpus_loader.py` and README usage.
- Checks and results:
  - `py -3.13 -m unittest discover -s tests -p test_corpus_loader.py -v`:
    **6 tests passed**. The real-corpus test loaded all **21,513 rows**, compared
    every original cell and mapped business field, checked source locators/hashes,
    confirmed repeated descriptions survive, and checked unchanged input bytes.
  - Temporary fixtures passed for BOM, quoted multiline CRLF text, literal
    `NA`/`N/A`/`null`, leading zeros, zero quantities, whitespace, unknown columns,
    duplicate/blank IDs, missing-value issues and processing eligibility.
  - Invalid UTF-8, missing/duplicate/empty headers, missing mapped columns,
    short/long/blank rows, malformed quoting and an invalid import root were
    rejected. Invalid inputs remained unchanged; header-only input returned `[]`.
  - `python verify_raw_data.py`: **all three raw SHA-256 checks passed**.
  - `git diff --exit-code -- data reports SOURCES.md LABELING_GUIDE.md`: passed.
    No raw files, processed data, reports or review work changed.
  - `git diff --check`: passed. Existing Phase 1 code and dependencies were not
    changed; the focused loader tests use no pandas dependency.
- Result: **P2-02 complete**. No blocker. The loader is in-memory and supports
  only the corpus CSV profile; other profiles, XLSX and report export remain pending.
- Next task: **P2-03**, explicit NTPC and IOCL CSV mapping profiles and their checks.
  Not started. Re-read this log and the contract before the next iteration.
- Stopped after this one task. Sponsor codes, transaction history and human
  validation remain unavailable; no accuracy claim is made.

## 2026-09-27 Iteration 3

- Selected task: P2-03 only, after reading `PHASE2.md`, the common input contract
  and this log. Inspected the loader, corpus tests, source headers and `SOURCES.md`
  sections 2.2/2.3. Prior iterations' uncommitted work was retained. No repository
  `AGENTS.md` found.
- Added explicit `load_ntpc_csv` and `load_iocl_csv` functions in `load_corpus.py`,
  sharing the existing read-only parsing and validation through a private helper.
  The corpus API and mapping ID remain unchanged. No configurable mapping API or
  candidate-file profile was added.
- Organization constants carry `kind: constant`, their exact value and evidence
  citing `SOURCES.md` section 2.2 or 2.3. NTPC retains `nit_id`, `doc_name`,
  `line_no`; IOCL retains `source_pdf`, `page`, `sl_no`, without concatenation.
  Neither source supplies a row ID or confirmed legacy code: these remain null
  with unmapped warnings. All input cells and repeated rows survive independently.
- Added `tests/test_source_loaders.py`; updated README usage and contract notes.
- Exact checks and results (from the repository root):
  - `py -3.13 -m unittest discover -s tests -p '*loader*.py' -v`: **10 tests
    passed** (six existing corpus tests plus four new source-profile tests).
    Compared every raw cell, mapped field, identifier component and origin across
    **486 NTPC** and **1,224 IOCL** rows. Verified row order, SHA-256 provenance,
    organization evidence, unmapped warnings, JSON compatibility and unchanged
    input bytes. The corpus regression still preserves all **21,513 rows**.
  - Temporary fixture checks preserved repeated rows and identical text across
    files with distinct source locators; preserved BOM/multiline text, unknown
    columns, leading-zero locator values and literal `NA`. Blank descriptions and
    locator components remained traceable with issues; missing mapped headers
    and malformed rows failed without modifying input.
  - `python verify_raw_data.py`: **all three raw SHA-256 checks passed**.
  - `git diff --exit-code -- data reports SOURCES.md LABELING_GUIDE.md`: **passed**;
    raw/processed data, source documentation and review files remain unchanged.
  - `git diff --check` and whitespace checks on new/untracked files: **passed**.
- Result: **P2-03 complete**. Blockers: **none**. No dependencies added; no CPSE
  material codes, human labels, specifications or accuracy claims invented.
- Next task: **P2-04**, configurable CSV mappings and candidate-file profile.
  **Not started.** Re-read this log, task list and contract before that iteration.
- Stopped after P2-03; XLSX, readiness reports and later phases remain pending.

## 2026-09-27 Iteration 4

- Read the progress log, task list, contract and loader before selecting P2-04.
  User authorized the remaining Phase 2 tasks in separate bounded loops.
- Added explicit mapping validation/JSON loading, `load_mapped_csv` and
  `load_candidates_csv`. Original cells, source IDs and repeated rows survive;
  required unmapped fields are errors, absent mapped headers fail structurally.
  Supplied specification fields retain original headers/values, and legacy-code
  mappings require source evidence. Conflicting mappings fail clearly.
- `py -3.13 -m unittest discover -s tests -p '*loader*.py' -v`: 14 tests passed,
  including renamed fields, invalid/ambiguous mappings, duplicate JSON keys and
  all 9,245 candidate IDs/shared cells traced to the raw corpus. Candidate
  heuristics remain raw metadata. Existing three-source tests also pass.
- `python verify_raw_data.py`: all three hashes passed. No raw data changed.
- P2-04 complete; no blocker. Next iteration: P2-05 XLSX adapter. No Phase 3 work.

## 2026-09-27 Iteration 5

- Re-read iteration 4 progress before selecting P2-05. Inspected the common mapper
  and installed XLSX library (openpyxl 3.1.5). Added only the XLSX adapter/tests
  and its dependency/contract documentation in this iteration.
- Added read-only `load_mapped_xlsx` with explicit sheet/header, physical source
  rows, exact text cells and the workbook snapshot hash. Formula/non-text cells
  fail clearly with coordinates instead of silently changing values or ID digits.
  Text-cell-only policy is documented, including numeric quantity limitations.
- `py -3.13 -m unittest discover -s tests -p '*loader*.py' -v`: 18 tests passed.
  Four XLSX tests cover equivalent CSV/XLSX real samples, leading-zero text IDs,
  blank/repeated rows, formulas, numeric formatted IDs, booleans/error cells,
  explicit sheet/header requirements, duplicate headers and unchanged bytes.
- `python verify_raw_data.py`: all three hashes passed.
- P2-05 complete; no blocker. No user workbook was modified. Next: P2-06 readiness
  reports and traceable sample uploads in new output directories. No Phase 3 work.

## 2026-09-27 Iteration 6

- Re-read iteration 5 before selecting P2-06. Added `phase2_ingest.py` (CLI and
  import API) and serializable source profiles in `input_profiles.py`.
  Structural validation precedes output creation; existing destinations are
  refused. Each pack contains every normalized record with raw cells/issues,
  readiness JSON/Markdown, mapping, real sample CSV, source-locator sidecar and
  a completion manifest with artifact hashes. No input file is rewritten.
- Reports separate absent columns from blank cells and reconcile input/output,
  eligible/ineligible and populated/missing counts. Missing legacy codes and
  specifications are explicit; no transaction adapter/history is inferred from
  quantities or estimated values. No deduplication or Phase 3 parsing was added.
- `py -3.13 -m unittest discover -s tests -p test_phase2_ingest.py -v`:
  **5 tests passed**. Verified counts, source sample links, artifact hashes,
  no-overwrite behavior, empty/invalid input, CSV/XLSX CLI paths, and exact parity
  between serializable profiles and all four existing loader APIs.
- Generated full packs under `output/phase2/{corpus,ntpc,iocl,candidates}` using
  `phase2_ingest.ingest` with `import_root='.'`. Reconciled 21,513 / 486 / 1,224 /
  9,245 records respectively. All are input-eligible, not human-verified materials.
  All records lack confirmed legacy codes and mapped structured specifications.
- Saved compact per-input reports and `summary.json` in `reports/phase2/` and
  five-row real samples with mapping/provenance in `examples/phase2/`. Reloaded
  all four samples and compared every raw cell, source hash, row and identifier
  to the original first five rows. Full duplicate data packs are Git-ignored;
  `docs/phase2_usage.md` documents reproduction and failure/format limitations.
- Final regression: `py -3.13 -m unittest discover -s tests -v`: **38 tests passed**
  (including all 15 existing Phase 1 tests). `python verify_raw_data.py`: **all
  three raw hashes passed**. All previously tracked data, Phase 1 reports,
  review files, `SOURCES.md` and `LABELING_GUIDE.md` remain unchanged.
- `git diff --check` and whitespace checks on added code/docs passed.
- P2-06 complete. No decision blocker. **Phase 2 is ready to close** within its
  documented scope. XLSX is text/blank-cell only; imports are in memory; sponsor
  codes, transactions and human validation are still missing. No accuracy,
  savings, material codes or human labels were invented.
- Stopped: all Phase 2 tasks are complete. Phase 3 is not started or authorized
  by this run. A later iteration must read this log before selecting new work.
