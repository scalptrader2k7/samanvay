# Phase 7 proposed common-material registry and mappings

Phase 6 preparation is closed at `docs/phase6_checkpoint.md` with human validation
still pending. Phase 7 creates a prototype registry only through explicit review
operations. Proposed Samanvay codes are not official CPSE material codes.

Each Ralph iteration completes one task, runs focused checks and updates
`docs/phase7_progress.md`. Stop after exit checks or a decision blocker. Do not
begin Phase 8.

| Task | Status | Deliverable | Acceptance check |
|---|---|---|---|
| P7-01 | Complete | Registry, decision, identifier, warning and storage contract. | Contract defines opaque prototype codes, explicit membership, all-member safety, separate functional relationships, history, evidence descriptions, migration/export fields and Phase 8 storage boundary. |
| P7-02 | Complete | Transactional SQLite repository with stable codes, source snapshots and evidence-built standard descriptions. | Reload/repeat operations retain codes; descriptions contain only supported values or UNKNOWN; source provenance and genuine identifiers remain distinct from internal row IDs. |
| P7-03 | Complete | Approval, rejection, deferral and reconsideration operations with group safety and Phase 6 warnings. | Membership requires explicit identity approval; critical/all-member conflicts block; functional equivalence creates no shared identity; repeated decisions are idempotent; history survives restart. |
| P7-04 | Complete | Reusable CLI plus migration preview and CSV/JSON exports. | Exports reconcile registry members, unresolved records, conflicts, missing material codes and original-to-proposed mappings; local database assumptions are documented. |
| P7-05 | Complete | Demonstration actions, example pack and final verification. | Tests cover stable IDs, repeated approvals, conflicting members, reconsideration, missing codes and exports; raw hashes pass; demo actions are marked non-evaluation; Phase 7 report is complete. |

Phase 7 exit means a persistent local prototype registry and export boundary are
ready for the Phase 8 service. It does not make any Samanvay code official.

All Phase 7 tasks passed on 2026-09-30. The authoritative local demonstration pack
is `output/phase7-v0.1/`; compact evidence is in `reports/phase7/`. Phase 7 is
complete. Phase 8 has not started.
