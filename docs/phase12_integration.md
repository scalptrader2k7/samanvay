# Phase 12 CPSE/SAP integration boundary

Phase 12 is a read-only prototype. It accepts explicitly mapped CSV rows, validates them, and produces the existing Phase 2 canonical records plus the existing Phase 3 matching records. It has no live SAP connector, ERP write, sync scheduler, or automatic workspace update.

## Contracts and templates

- `contracts/integration/canonical_schema_v0.1.json`: canonical source/derived field contract.
- `contracts/integration/mapping_contract_v0.1.json`: mapping grammar, validation and missing-value policy.
- `contracts/integration/public_mapping_v0.1.json`: current public candidate schema.
- `contracts/integration/cpse-sap_mapping_v0.1.json`: demonstrative sponsor/SAP-shaped schema.
- `examples/phase12/*_import_template.csv`: header-only import templates.
- `examples/phase12/*_example.csv`: the same two real records under different headers.

`External Row ID` is a stable source row locator and is never presented as an official material code. `Material Code` maps to `legacy_material_code` only when genuinely supplied. It is blank in the example because the inspected source supplies no confirmed CPSE code.

## Field mapping

| CPSE/SAP-shaped field | Canonical field | Transformation | Validation | Missing behavior |
|---|---|---|---|---|
| Company | source_organization | exact text | required for processing | error; row retained |
| External Row ID | source_record_id and source_identifiers | exact text | required and unique for workspace loading | error; row retained |
| Material Code | legacy_material_code | exact text | source meaning evidence required in mapping | unknown with warning |
| Short Text | description_original | exact text | required for processing | error; row retained |
| Base UOM | uom_original | exact text | optional | unknown with warning |
| Material Group | category_original | exact text | optional | unknown with warning |
| Standard/Grade/Size/Pressure/Voltage/Model Supplied | specifications_original | exact key/value evidence | optional; no interpretation | unknown with warning |
| Source System | source_system | exact text | optional | unknown with warning |
| Plant | source_section | exact text | optional; no geographic inference | unknown with warning |
| Document Reference | document_reference | exact text | optional | unknown with warning |
| every source column | raw_fields | exact text | every row has exactly the header set | always retained |

After validation, eligible rows pass unchanged into `phase3_attributes.derive_description`. No integration rule duplicates normalization, extraction, retrieval, pair comparison, or registry logic.

## File and API use

```powershell
py -3.13 phase12_adapter.py sponsor.csv --mapping sponsor_mapping.json --output-dir output/new_adapter_pack --import-root .
```

The CLI refuses to overwrite an existing directory. Its pack contains the mapping, validation report, all canonical rows, eligible matching rows, and hashes.

Workspace-scoped service endpoints:

- `GET /api/v1/workspaces/{workspace}/integration/contract`
- `GET /api/v1/workspaces/{workspace}/integration/examples`
- `GET /api/v1/workspaces/{workspace}/integration/templates/{public|cpse-sap}.csv`
- `POST /api/v1/workspaces/{workspace}/integration/validate-preview`

Preview requests permit at most 100 rows and 100 columns, require text values, enforce normal workspace read access, and return `persisted: false` and `erp_writes: false`. The browser Integration view displays mapping, missing/unmapped fields, source IDs, descriptions, code presence, and preview hash. Production ingestion remains an authenticated administrator operation through a validated adapter pack and the existing offline seeding utility.

## Acceptance evidence

`reports/phase12/acceptance.json` records the 9,245-row current-candidate validation and the two-schema test. Both example schemas produce byte-equivalent logical matching inputs for the compared core fields, retrieve M000925 for M000753, and yield the existing `near_duplicate` rule outcome. These are deterministic rule outputs, not accuracy claims.
