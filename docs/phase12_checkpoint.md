# Phase 12 checkpoint

Status: **complete** on 2026-09-30. Phase 13 has not started.

The integration boundary maps configurable CSV schemas into the existing canonical contract, retains all source rows/raw fields/provenance, and calls the unchanged Phase 3 and matching modules. A no-overwrite CLI pack, machine contracts, header-only templates, two real-data examples, workspace-scoped preview API, and browser preview are complete.

Acceptance evidence:

- Current candidate snapshot: 9,245 input/canonical/matching-ready records; 9,245 unique source IDs; zero ineligible.
- Different public and CPSE/SAP-shaped headers produced the same core records for M000753 and M000925.
- Existing retrieval returned M000925 for M000753; existing pair evidence returned `near_duplicate`.
- Missing material codes and technical fields remained unknown; no code or attribute was invented.
- API preview was non-persistent, workspace access-controlled, bounded to 100 rows/columns, and made no ERP writes.
- Raw hash verification passed for all three source CSVs.

Limitations: CSV text input only at this Phase 12 service boundary; XLSX remains available through the conservative Phase 2 offline loader. There is no live SAP protocol, ERP writeback, scheduled sync, schema discovery, deployed account validation, or automatic loading of previewed records. Sponsor-specific mappings require source-owner review, especially the meaning of material codes, dimensions, plant fields, and null tokens. The public examples contain no genuine CPSE material codes.

Authoritative evidence is in `reports/phase12/`, `contracts/integration/`, and `examples/phase12/`.
