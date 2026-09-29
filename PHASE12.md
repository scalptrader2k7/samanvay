# Phase 12 integration boundary

The master plan is authoritative: document a CPSE/SAP-ready file and API contract without live ERP writes, and map future sponsor fields into the existing schema. Acceptance requires a new schema to map without changing the matching core. Do not begin Phase 13.

| Task | Status | Deliverable | Acceptance check |
|---|---|---|---|
| P12-01 | Complete | Existing schema/loader/core audit and bounded adapter contract. | Canonical source versus derived fields, required/optional/unknown policy, provenance and read-only ERP boundary are explicit. |
| P12-02 | Complete | Reusable in-memory/file adapter and no-overwrite CLI pack. | Exact configurable columns map to canonical records; required load IDs are validated; raw values/provenance/issues survive; eligible records enter existing Phase 3 enrichment unchanged. |
| P12-03 | Complete | CSV templates, two mapping profiles and machine/human contracts. | Public and CPSE/SAP-shaped examples with different headers produce the same canonical/core inputs without guessed technical meanings. |
| P12-04 | Complete | Workspace-scoped validation/preview API and small browser demo. | Reviewer can inspect templates/mapping, preview example rows and see missing/unmapped fields; API performs no persistence or ERP writes. |
| P12-05 | Complete | Two-schema acceptance, dependency checks and checkpoint. | Both schemas feed unchanged retrieval/pair evidence, identifiers/descriptions remain traceable, raw hashes pass and Phase 13 remains unstarted. |
