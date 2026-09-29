# Phase 11 progress

Read this log and `PHASE11.md` before each bounded iteration. Do not begin Phase 12.

## 2026-09-30 Iteration 1

- Re-read the master-plan Phase 11 section and audited the Phase 8 dashboard and
  generic exports, Phase 10 current/history state, frontend controls and storage.
- Existing metrics are persisted source, mapping, registry, relationship, warning,
  organization, family, decision and audit counts. Existing current-state registry
  and source-mapping CSV/JSON exports are workspace-scoped and paginated.
- Identified gaps in completeness, current-state review metrics, transparent
  conflict denominator, reconsidered coverage, registry export UI and Excel pack.
- Candidate proposals are not persisted; the contract forbids inventing their
  workspace-wide count. No supported financial metric exists.
- Added the bounded checklist and calculation/export contract. P11-01 complete; no
  blocker. Next: P11-02 authoritative quality calculations and API.

## 2026-09-30 Iteration 2

- Added `RegistryStore.quality_dashboard()` and workspace-scoped
  `GET /quality-dashboard`. It calculates loaded/status counts, persisted-field
  completeness, current approve/reject/defer states, reconsiderations, unique
  current-decision pairs, rule-output outcomes, transparent conflict numerator and
  denominator, active registry clusters/functional relationships, current mapping
  coverage and historically revoked mappings.
- The response includes a deterministic workspace-state SHA-256, metric scope and
  definitions, an explicit `not_persisted` candidate count, and an explicit
  unsupported financial-metrics result.
- Focused check: 10 Phase 8/10/11 API tests passed. Fixtures reconcile 4 loaded,
  2 mapped, 2 unresolved and 1/2 conflict rule outputs; reconsideration separates
  current zero-mapped state from two historically revoked sources.
- P11-02 complete; no blocker. Next: P11-03 deterministic exports and Excel pack.

## 2026-09-30 Iteration 3

- Normalized registry exports to stable current-state rows with prototype code,
  readable/structured descriptions and sorted member source IDs. Existing mapping
  CSV/JSON remains current-state, ordered and paginated.
- Added separate generic audit-event and mapping-history JSON/CSV datasets rather
  than mixing historical changes into current mappings.
- Added `GET /exports/quality-pack.xlsx`. The workbook contains Manifest,
  Dashboard, Completeness, Registry and Current Mappings sheets. Fixed document/ZIP
  metadata makes unchanged workspace state byte-for-byte reproducible; response
  headers identify workspace-state hash and current-state/no-history scope.
- Focused check: 9 Phase 8/11 tests passed, including identical repeated XLSX/CSV
  bytes, IDs/status, pagination, workbook scope and cross-workspace denial.
- P11-03 complete; no blocker. Next: P11-04 frontend dashboard and export UI.

## 2026-09-30 Iteration 4

- Replaced the basic status page with a quality dashboard backed entirely by
  `/quality-dashboard`: loaded/mapped/unresolved/pending cards, persisted-field
  completeness table, current review/cluster state, conflict formula and scope,
  and current versus historically revoked mapping coverage.
- Added clear download groups for current registry CSV/JSON, current mapping
  CSV/JSON, the Excel quality pack, and separate governance-history exports. The UI
  states workspace/state hash and whether data is current or historical.
- Added an explicit financial-metrics limitation from the API; no savings, ROI or
  cost-impact numbers appear.
- Fixed Excel reproducibility across clock seconds by normalizing OpenXML modified
  metadata as well as ZIP timestamps.
- Focused check: 10 Phase 9/11 frontend, metric and export tests passed; JavaScript
  syntax passed. P11-04 complete; no blocker. Next: P11-05 real-data verification.

## 2026-09-30 Iteration 5

- Reconciled the full-data quality API against direct workspace SQL: 9,245 loaded,
  2 mapped, 9,243 unresolved, 0 deferred/pending, 1 active registry entry and a
  conflict rule output of 0/2 current persisted decision pairs.
- Chrome opened the dashboard, inspected the underlying M000753/M000925 registry
  membership, downloaded the Excel pack and verified 9,245 mapping rows plus the
  same loaded/mapped/unresolved summary.
- Full data exposed an OpenXML-illegal NUL in one preserved description. The Excel
  serializer now writes illegal controls as visible Unicode escape text (for
  example `\u0000`); stored data and CSV/JSON remain unchanged. The manifest records
  this policy.
- Two independently downloaded full-data workbooks had identical SHA-256
  `4B092BE02BEF6B2C2E423D76976BF3E2F1080E11078F7706D3D720E5D74AB960`.
- Final dependency run: 60 Phase 5-11 tests passed in 17.815 seconds. A final 7
  Phase 11 tests passed after rate-display refinement. JavaScript syntax, Python
  compilation, OpenAPI generation (24 operations), diff validation and all three
  protected raw hashes passed.
- P11-05 and Phase 11 are complete; no blocker. Phase 12 has not started.
