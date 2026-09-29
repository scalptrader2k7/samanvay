# Input readiness

Source: `data/raw/huggingface/material_description_corpus.csv`
Mapping: `raw-corpus-v0.1`

Loaded 21513 rows; retained 21513 records; dropped 0.
Eligible: 21513; ineligible: 0.

| Field | Origin | Populated rows | Missing rows |
|---|---|---:|---:|
| source_organization | column | 21513 | 0 |
| source_record_id | column | 21513 | 0 |
| description_original | column | 21513 | 0 |
| uom_original | column | 397 | 21116 |
| category_original | column | 12758 | 8755 |
| source_system | column | 21513 | 0 |
| source_section | column | 21513 | 0 |
| source_url | column | 20534 | 979 |
| document_reference | column | 4375 | 17138 |
| quantity_original | column | 484 | 21029 |
| legacy_material_code | unmapped | 0 | 21513 |
| source_identifiers | columns | 21513 | 0 |
| specifications_original | unmapped | 0 | 21513 |

No transaction adapter is present; transaction modules are disabled.

Counts describe input rows, not unique materials or verified matches.
Overlapping sources and candidate subsets must not be summed as distinct materials.
No PR/PO/stock/issue history is mapped. Current public inputs do not provide it.
Planned quantities and estimated values do not establish consumption, prices paid or savings.
Human review and sponsor material-master validation remain separate from ingestion.

The sample contains original cells from the first input rows, not invented examples.
Use sample_provenance.json to trace each sample back to the original snapshot.
records.jsonl includes each retained row and its validation issues.
