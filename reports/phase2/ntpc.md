# Input readiness

Source: `data/raw/huggingface/ntpc_material_items.csv`
Mapping: `raw-ntpc-v0.1`

Loaded 486 rows; retained 486 records; dropped 0.
Eligible: 486; ineligible: 0.

| Field | Origin | Populated rows | Missing rows |
|---|---|---:|---:|
| source_organization | constant | 486 | 0 |
| source_record_id | unmapped | 0 | 486 |
| description_original | column | 486 | 0 |
| uom_original | column | 0 | 486 |
| category_original | unmapped | 0 | 486 |
| source_system | unmapped | 0 | 486 |
| source_section | unmapped | 0 | 486 |
| source_url | unmapped | 0 | 486 |
| document_reference | column | 486 | 0 |
| quantity_original | column | 0 | 486 |
| legacy_material_code | unmapped | 0 | 486 |
| source_identifiers | columns | 486 | 0 |
| specifications_original | unmapped | 0 | 486 |

No transaction adapter is present; transaction modules are disabled.

Counts describe input rows, not unique materials or verified matches.
Overlapping sources and candidate subsets must not be summed as distinct materials.
No PR/PO/stock/issue history is mapped. Current public inputs do not provide it.
Planned quantities and estimated values do not establish consumption, prices paid or savings.
Human review and sponsor material-master validation remain separate from ingestion.

The sample contains original cells from the first input rows, not invented examples.
Use sample_provenance.json to trace each sample back to the original snapshot.
records.jsonl includes each retained row and its validation issues.
