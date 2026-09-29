# Phase 12 progress

Read this log and `PHASE12.md` before each bounded iteration. Do not begin Phase 13.

## 2026-09-30 Iteration 1 — P12-01

Audited the Phase 2 mapping, Phase 3 enrichment, matching/registry consumers, seeding and frontend. Recorded source/derived boundaries and the read-only integration contract.

## Iteration 2 — P12-02

Added `map_source_rows`, `integration_adapter.py`, and `phase12_adapter.py`. Focused tests passed for row/provenance retention, missing and duplicate IDs, invalid values, deterministic preview, no-overwrite packs, and unchanged retrieval/pair logic.

## Iteration 3 — P12-03

Added canonical and mapping machine contracts, public and CPSE/SAP mapping profiles, header-only templates, and two examples carrying the same real source IDs/descriptions. Blank CPSE codes/specifications remain unknown. Both schemas produced the same core inputs.

## Iteration 4 — P12-04

Added four workspace-scoped integration endpoints and the browser Integration view. Preview limits are enforced by request validation; private-workspace isolation and zero persistence were tested. The UI exposes mapping, issues, source evidence, code presence and the read-only boundary.

## Iteration 5 — P12-05

Validated all 9,245 current candidates: all rows were retained and matching-ready with unique source IDs. Existing retrieval and pair evidence accepted both example schemas unchanged. Focused Phase 12 tests and dependency tests passed; source hashes passed. Phase 12 closed with limitations in `docs/phase12_checkpoint.md`. Next phase, when authorized: Phase 13 delivery packaging and final documentation.

Final verification: 126 repository tests passed in 110.8 seconds;
ode --check frontend/app.js passed. A headless Edge walkthrough loaded the public workspace, opened Integration, selected the CPSE/SAP-shaped example, validated two rows, displayed both original source IDs/descriptions, reported one unmapped raw column, and showed persisted=false, matching_core_changed=false, and erp_writes=false. Screenshot:
eports/phase12/integration_preview.png.
