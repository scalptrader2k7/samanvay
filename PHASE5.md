# Phase 5 pair evidence and safety checks

Phase 4 is closed at `docs/phase4_checkpoint.md`. Phase 5 compares only retrieved
pairs. It never merges records, assigns common codes, changes raw data, or treats
a retrieval score as a pair decision.

Each Ralph iteration completes one task, runs its focused checks and updates
`docs/phase5_progress.md` before continuing. Stop after the exit checks or at a
decision blocker. Do not begin Phase 6.

| Task | Status | Deliverable | Acceptance check |
|---|---|---|---|
| P5-01 | Complete | Phase 4 checkpoint and Phase 5 comparison/outcome contract. | Contract defines evidence traceability, comparable meanings/units, critical conflict precedence, five outcomes, review handling, score separation and prohibited actions. |
| P5-02 | Complete | Evidence-preserving field comparator and critical safety gate. | Focused tests cover compatible, missing, uncertain, non-comparable and conflicting values; 15/25 mm, 150/240 mm2 and pressure-basis cases block identity proposals; all evidence spans reproduce source text. |
| P5-03 | Complete | Deterministic pair outcome engine plus readable CLI/API result. | Real/synthetic cases cover all five outcomes; every result retains both IDs/descriptions, evidence, field comparisons, review state and a retrieval section separate from the outcome. |
| P5-04 | Complete | Phase 5 evidence pack, diagnostic report and final verification. | All Phase 4 retrieved pairs are reconciled; named real/hard cases are documented; outputs are rule counts, not accuracy; focused/full tests, raw hashes, manifest and no-overwrite/input-integrity checks pass. |

Phase 5 exit means the rule system produces traceable proposed outcomes and blocks
unsafe identity proposals on supported critical conflicts. It does not establish
engineering equivalence or measured predictive accuracy.

All Phase 5 tasks passed on 2026-09-30. The authoritative reproducible pack is
`output/phase5-v0.1/`; compact evidence is in `reports/phase5/`. Phase 5 is closed
at `docs/phase5_checkpoint.md`. The frozen pack retains its five proposed outcome
labels; Phase 6 records an explicit evidence basis for review.
