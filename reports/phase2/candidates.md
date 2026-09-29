# Input readiness

Source: `data/processed/material_candidates.csv`
Mapping: `material-candidates-v0.1`

Loaded 9245 rows; retained 9245 records; dropped 0.
Eligible: 9245; ineligible: 0.

| Field | Origin | Populated rows | Missing rows |
|---|---|---:|---:|
| source_organization | column | 9245 | 0 |
| source_record_id | column | 9245 | 0 |
| description_original | column | 9245 | 0 |
| uom_original | column | 391 | 8854 |
| category_original | column | 5082 | 4163 |
| source_system | unmapped | 0 | 9245 |
| source_section | unmapped | 0 | 9245 |
| source_url | column | 8338 | 907 |
| document_reference | column | 2131 | 7114 |
| quantity_original | column | 474 | 8771 |
| legacy_material_code | unmapped | 0 | 9245 |
| source_identifiers | columns | 9245 | 0 |
| specifications_original | unmapped | 0 | 9245 |

No transaction adapter is present; transaction modules are disabled.

Counts describe input rows, not unique materials or verified matches.
Overlapping sources and candidate subsets must not be summed as distinct materials.
No PR/PO/stock/issue history is mapped. Current public inputs do not provide it.
Planned quantities and estimated values do not establish consumption, prices paid or savings.
Human review and sponsor material-master validation remain separate from ingestion.

The sample contains original cells from the first input rows, not invented examples.
Use sample_provenance.json to trace each sample back to the original snapshot.
records.jsonl includes each retained row and its validation issues.
