# SIH 26099: Phase 1 ? Dataset Foundation, Profiling & Curation

Phase 1A-1C and Phase 2 are complete for the documented input contract. Phase 2
supports fixed/configurable CSV mappings, the provisional candidate subset,
text-cell XLSX uploads, readiness reports and traceable sample files.
See [Phase 2 usage and checks](docs/phase2_usage.md) and
[readiness evidence](reports/phase2/summary.json).
Phase 3 is now complete for conservative description normalization and
evidence-bearing technical attribute extraction. See the [Phase 3 checklist](PHASE3.md),
[contract](docs/phase3_contract.md), [progress](docs/phase3_progress.md), and
[real-example review](reports/phase3/review_examples.md).
Phase 4 candidate retrieval is now complete with bounded exact, token and fuzzy
retrieval. See the [Phase 4 checklist](PHASE4.md), [contract](docs/phase4_contract.md),
[progress](docs/phase4_progress.md), and [diagnostic examples](reports/phase4/review_examples.md).
Phase 5 has not started.
See the [Phase 2 task list](PHASE2.md),
[input format](docs/common_input_format.md) and [iteration log](docs/phase2_progress.md).

From the repository root, use the loader in Python (returns records in memory;
does not write files):

```python
from load_corpus import load_corpus_csv, load_ntpc_csv, load_iocl_csv

records = load_corpus_csv(
    "data/raw/huggingface/material_description_corpus.csv", import_root="."
)
ntpc_records = load_ntpc_csv(
    "data/raw/huggingface/ntpc_material_items.csv", import_root="."
)
iocl_records = load_iocl_csv(
    "data/raw/huggingface/iocl_procurement_plan_items.csv", import_root="."
)
```

These examples use fixed source profiles; select the documented source explicitly.
NTPC/IOCL organizations are provenance-backed profile constants. Structural errors raise `ValueError`;
row-level issues remain attached to preserved records. Run its focused checks with
`py -3.13 -m unittest discover -s tests -p '*loader*.py' -v`.

This repository contains **Phase 1** of **SIH26099: AI-Driven Standardization & Harmonization of Material Codes Across CPSEs**.

In accordance with Phase 1 scope requirements:
- **Phase 1A Scope:** Data acquisition, schema auditing, material vs. service filtering assessment, cross-file overlap detection, and statistical profiling.
- **Phase 1B Scope:** Preparation for human validation of material classification, creation of a stratified review sample (400 records), curation of provisional material candidates (`data/processed/material_candidates.csv`), and deep provenance overlap audit.
- **Out of Scope for Phase 1:** No matching models, APIs, databases, or UIs are built. No synthetic CPSE material codes or hypothetical accuracy metrics are created.

---

## 1. Quick Start (Windows PowerShell)

Open Windows PowerShell in the project directory:

```powershell
# 1. Install required dependencies
py -m pip install -r requirements.txt

# 2. (Optional) Re-download raw files from Hugging Face if needed
py download_data.py

# 3. Run Phase 1A: Master Data Profiler
py profile_data.py

# 4. Run Phase 1B: Material Curation & Stratified Review Pipeline
py curate_material_candidates.py
```

*(Note: On systems where `python` is aliased directly, you can use `python` instead of `py`.)*

---

## 2. Dataset Architecture

### A. Raw Untouched Datasets (`data/raw/huggingface/`)
Preserved byte-for-byte in their original raw format:

| File Name | Rows | Columns | Size | Description |
|---|---|---|---|---|
| `material_description_corpus.csv` | **21,513** | 15 | 6.11 MB | Master working corpus (OIL India, NTPC, IOCL) |
| `ntpc_material_items.csv` | **486** | 7 | 54.4 KB | Granular line items extracted from NTPC tender PDFs |
| `iocl_procurement_plan_items.csv` | **1,224** | 9 | 180.5 KB | Extracted lines from IOCL Future Procurement Plan |

See [SOURCES.md](SOURCES.md) for full licensing details (CC-BY-4.0), download URLs, SHA-256 hashes, and provenance notes.

Raw CSVs are marked `-text` in `.gitattributes` so Git preserves their original
line endings: CRLF for NTPC and IOCL, LF for the main corpus. Verify the downloaded
or checked-out bytes with `py verify_raw_data.py` (no dependencies required).
Use `py verify_raw_data.py --git-ref HEAD` to check the committed bytes, or
`py verify_raw_data.py --git-ref :0` to check the staged bytes before committing.
The preservation rule and restored raw CSVs must be committed together; adding
the rule alone does not repair older Git blobs.

### B. Curated Working Dataset (`data/processed/`)
- **`data/processed/material_candidates.csv`**: **9,245** provisional individual material records isolated from the main corpus. Each record is enriched with derived major item categories (14 industrial domains) and audited for 6 discrete technical detail dimensions (size, material grade, engineering standard, voltage, pressure class, model/part number).

---

## 3. Human Review & Annotation (`reports/`)

- **`reports/classification_review.csv`**: Stratified sample of **400 records** across all 3 CPSEs, 6 predicted classes, major description kinds, and 7 boundary conditions (e.g. `supply and installation`, `AMC of pumps`, engineering standards). Includes blank columns for `human_label`, `reviewer_note`, and `usable_for_matching`.
- **`LABELING_GUIDE.md`**: Comprehensive human labeling guidelines providing clear definitions, decision boundaries, and concrete examples for annotators.

---

## 4. Reports & Audit Deliverables

1. **`reports/data_profile.json`**: Machine-readable JSON profiling all files, missing values, duplicates, and initial breakdowns.
2. **`reports/data_profile.md`**: Master profiling Markdown report.
3. **`reports/curation_report.md`**: Detailed Phase 1B curation and overlap audit report.
4. **`reports/curation_report.json`**: Machine-readable curation statistics and technical attribute distributions.
5. **`reports/sample_records.csv`**: Initial 42-record representative sample from Phase 1A.

---

## 5. Key Metrics Summary

- **Total Raw Records Across 3 Files:** `23,223`
- **Global Unique Descriptions:** `17,459`
- **Material vs. Service Assessment:**
  - **Individual Materials:** **9,245** (42.97%)
  - **Broad Tenders & Services:** **12,268** (57.03%)
- **Technical Attribute Density:** **2,911** material candidates (31.49%) possess explicit technical engineering attributes (dimensions, grades, standards, ratings, pressure classes, or catalog numbers).
- **Cross-File Overlap Audit:**
  - NTPC: 462 descriptions match after whitespace trimming; 24 additional matches after stripping punctuation at both ends; zero unmatched descriptions.
  - IOCL: 1,147 descriptions match after whitespace trimming; 45 additional matches after stripping punctuation at both ends; 32 unmatched descriptions. A length filter is a hypothesis, not a verified cause.
  - NTPC vs. IOCL: zero shared descriptions under the implemented normalization; this does not establish disjoint domains or prove source provenance.

## Phase 1C: Data QA and Human Review

Reports use strict JSON (`null` for missing/non-finite values). Source-field
coverage is measured; overlap is not treated as proof of record identity.
Human validation is pending. Raw CSVs and the original review sheet are preserved.

The existing 400-row sheet is split into six files in `reports/review_batches/`
(67, 67, 67, 67, 66, 66 rows). Assign one file to each reviewer and follow
[LABELING_GUIDE.md](LABELING_GUIDE.md). Edit only the three human-review columns.
All source fields and IDs must remain unchanged. Reviewers should save CSV as UTF-8.

```powershell
# Optional: reproduce blank batches into a NEW directory; never overwrites reviews
py review_classification.py split --output-dir reports/review_batches_new

# Validate all six returned files, combine in original order, and evaluate labels
$reviewFiles = (Get-ChildItem reports/review_batches/review_*.csv).FullName
py review_classification.py combine --output-dir reports/review_results @reviewFiles

# Focused QA tests
py -m unittest discover -s tests -v
py verify_raw_data.py
```

The combine command writes `classification_review_combined.csv` and
`review_metrics.json` into a new directory; it refuses existing output directories.
It rejects invalid labels, invalid usability values, changed source fields,
duplicate/unknown IDs, missing IDs, and changes to existing reference annotations.
With no labels it reports `awaiting_labels` and no metrics. With partial labels,
precision and recall use only labeled rows and are marked partial. Undefined
ratios are `null`. Results describe this stratified sample, not full-corpus
performance. No overall accuracy is reported. `reviewer_note` is optional;
`usable_for_matching` completion is counted separately from classification labels.
