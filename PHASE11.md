# Phase 11 quality dashboard and export

The master plan is authoritative: show loaded records, data completeness, candidate
clusters, conflict rate, pending reviews and mapping coverage; export registry and
mapping CSV/Excel. Counts must reconcile and no savings figures may be invented.
Do not begin Phase 12.

| Task | Status | Deliverable | Acceptance check |
|---|---|---|---|
| P11-01 | Complete | Existing metric/export audit and bounded calculation contract. | Every planned number has a persisted source and denominator; unpersisted candidate proposals and financial claims are explicitly unavailable. |
| P11-02 | Complete | Authoritative quality calculations and dashboard API. | Counts, completeness, current review states, conflict numerator/denominator, clusters and mapping coverage reconcile with direct database queries. |
| P11-03 | Complete | Deterministic registry/mapping exports and Excel quality pack. | Current-state CSV/JSON and XLSX preserve IDs/status, remain workspace isolated, separate history and reproduce byte-for-byte for unchanged state. |
| P11-04 | Complete | Practical browser quality dashboard and export explanations. | Every displayed number comes from the quality API; reviewer can inspect scope/definitions and download supported current or historical exports. |
| P11-05 | Complete | Full-data browser verification, dependency checks and checkpoint. | 9,245-record metrics reconcile, exported content matches current state, raw hashes pass and Phase 12 remains unstarted. |
