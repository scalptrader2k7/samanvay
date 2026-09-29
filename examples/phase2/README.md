# Real sample uploads

Each subdirectory contains the first five records of its source file, an explicit
mapping and a sidecar linking every sample row to the original snapshot hash and
row number. Values and source identifiers were copied unchanged.

| Profile | Original file |
|---|---|
| corpus | data/raw/huggingface/material_description_corpus.csv |
| ntpc | data/raw/huggingface/ntpc_material_items.csv |
| iocl | data/raw/huggingface/iocl_procurement_plan_items.csv |
| candidates | data/processed/material_candidates.csv |

These are transport/ingestion examples, not verified materials, labeled matches
or representative evaluation samples. Candidates remain provisional and overlap
the corpus. See `SOURCES.md` for source attribution and the stated CC-BY-4.0
license, and `docs/phase2_usage.md` for replay commands. Preserve text identifiers
when opening or saving these CSVs in spreadsheet software.
