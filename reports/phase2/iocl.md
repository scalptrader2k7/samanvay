# Input readiness

Source: `data/raw/huggingface/iocl_procurement_plan_items.csv`
Mapping: `raw-iocl-v0.1`

Loaded 1224 rows; retained 1224 records; dropped 0.
Eligible: 1224; ineligible: 0.

| Field | Origin | Populated rows | Missing rows |
|---|---|---:|---:|
| source_organization | constant | 1224 | 0 |
| source_record_id | unmapped | 0 | 1224 |
| description_original | column | 1224 | 0 |
| uom_original | column | 928 | 296 |
| category_original | unmapped | 0 | 1224 |
| source_system | unmapped | 0 | 1224 |
| source_section | column | 74 | 1150 |
| source_url | unmapped | 0 | 1224 |
| document_reference | column | 1224 | 0 |
| quantity_original | column | 1123 | 101 |
| legacy_material_code | unmapped | 0 | 1224 |
| source_identifiers | columns | 1224 | 0 |
| specifications_original | unmapped | 0 | 1224 |

No transaction adapter is present; transaction modules are disabled.

Counts describe input rows, not unique materials or verified matches.
Overlapping sources and candidate subsets must not be summed as distinct materials.
No PR/PO/stock/issue history is mapped. Current public inputs do not provide it.
Planned quantities and estimated values do not establish consumption, prices paid or savings.
Human review and sponsor material-master validation remain separate from ingestion.

The sample contains original cells from the first input rows, not invented examples.
Use sample_provenance.json to trace each sample back to the original snapshot.
records.jsonl includes each retained row and its validation issues.
