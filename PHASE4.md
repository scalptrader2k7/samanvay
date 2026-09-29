# Phase 4 candidate retrieval

Phase 3 is closed at `docs/phase3_checkpoint.md`; its authoritative input is
`output/phase3-v0.1/material_attributes.jsonl`. Retrieval proposes a bounded list
of records and explanations. It never declares identity/equivalence, merges rows,
assigns common codes, or applies the Phase 5 conflict gate.

Each Ralph iteration handles one task, runs focused checks and updates
`docs/phase4_progress.md` before continuing. Stop after exit checks or a decision
blocker. Do not begin Phase 5.

| Task | Status | Deliverable | Acceptance check |
|---|---|---|---|
| P4-01 | Complete | Retrieval contract, token policy and bounded index design. | Contract defines top-k, reasons, source-ID preservation, candidate-only semantics, blocking limits, diagnostics and honest evaluation language. |
| P4-02 | Complete | Build exact normalized-text/identifier and useful-token indexes. | Repeated descriptions and cross-organization exact examples are found; self is excluded; no full all-pairs structure or scan is used. |
| P4-03 | Complete | Add bounded fuzzy reranking and deterministic top-k explanations. | Near formatting variants and size/rating-conflict records can be proposed with reasons; results are stable and limited; no decision label appears. |
| P4-04 | Complete | Run all-record retrieval pack and diagnostic example suite; decide whether semantics is justified. | 9,245 query IDs reconcile; runtime/candidate-pool diagnostics are recorded; clearly named example coverage passes; semantic retrieval is added only with demonstrated improvement; raw hashes/full regressions pass. |

Phase 4 exit means practical, traceable lexical retrieval on current surrogate
data. Example coverage is not recall or accuracy without independently reviewed pairs.

All Phase 4 tasks passed on 2026-09-27. The authoritative pack is
`output/phase4-v0.1/`; compact evidence is in `reports/phase4/`. Phase 4 is ready
to close after the final regression recorded in the progress log. Phase 5 has not started.
