# Phase 12 integration boundary contract

Phase 12 reuses the Phase 2 common input record as the canonical source schema and
the Phase 3 `derive_description` function as the unchanged entry into matching.
Source-provided data and derived evidence remain separate.

## Boundary

Supported: UTF-8 CSV and the existing conservative text-cell XLSX loader, explicit
source-column mapping, validation, preview, no-overwrite adapter packs, Phase 3
enrichment and administrator-controlled workspace seeding.

Unsupported: SAP/ERP writes, database writes to source systems, live synchronization,
automatic material-master updates, change transactions, or credential exchange with
an ERP. Any live integration requires sponsor access, approval, authentication,
field semantics and interface specifications.

## Canonical layers

Source layer fields are `source_organization`, `source_record_id`,
`legacy_material_code`, `description_original`, `uom_original`,
`category_original`, `specifications_original`, `source_system`, `source_section`,
`source_url`, `document_reference`, `quantity_original`, `source_identifiers`,
`raw_fields`, source snapshot/row provenance, mapping version and validation issues.
The integration boundary requires organization, source record ID and description
before a row may be loaded into the existing registry-backed workflow. Other source
fields are optional and remain null/empty when absent.

Derived fields are added only by the existing Phase 3 rules:
`description_normalized`, `family`, evidence-bearing `attributes`, normalization and
parser versions, and derivation issues. External structured specification columns
remain in `specifications_original`; their names and values are preserved but never
silently promoted to diameter, grade, pressure, voltage or model meanings.

Every mapping is explicit identity transformation from an exact source header to a
canonical field. Blank values become null plus an issue while the exact cell remains
in `raw_fields`. Unmapped fields remain null/empty plus an issue. No case folding,
unit conversion, type coercion or inference occurs during adaptation.

The machine-readable field contract and mapping examples are under
`contracts/integration/`; import templates and source examples are under
`examples/phase12/`.
