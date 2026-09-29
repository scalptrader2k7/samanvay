# Phase 8 backend service, persistent storage and deployment preparation

Phase 7 is closed at `docs/phase7_checkpoint.md`. Phase 8 exposes the existing
ingestion, retrieval, comparison, registry, decision and export logic through an
authenticated API. Frontend implementation remains Phase 9.

Each Ralph iteration completes one task, runs focused checks and updates
`docs/phase8_progress.md`. Stop after exit checks or an external account blocker.
Do not begin Phase 9.

| Task | Status | Deliverable | Acceptance check |
|---|---|---|---|
| P8-01 | Complete | Service/storage/API contract, ten-feature status and readable description refinement. | Contract defines pagination/limits, authentication, workspace ownership, idempotency, SQLite/local and managed/durable boundaries; readable descriptions preserve attribute meaning and mark ambiguous dimensions. |
| P8-02 | Complete | FastAPI read service: health/readiness, materials/search, lexical candidates, pair evidence, registry/mappings/history/relationships and dashboard. | Responses are validated, paginated, workspace-scoped and calculated from actual persisted records; BM25 is described only as lexical retrieval if used. |
| P8-03 | Complete | Authenticated write service: approve/reject/defer/reconsider and safe exports. | Server-derived actor, owner enforcement, public-read-only demo, idempotent repeated writes, useful errors and approval-to-registry-to-export flow pass. |
| P8-04 | Complete | Durable managed storage adapter, schema, environment documentation and Vercel configuration. | Neon-compatible PostgreSQL transactions persist/reload workspace state without relying on server filesystem; credentials are env-only; local SQLite remains supported. |
| P8-05 | Complete | Deployment/check pack, focused regression, API contract report and Phase 8 checkpoint. | Restart/access-isolation tests pass; deployment is verified only with available account access; exact external setup blockers and local commands are recorded; Phase 9 is not started. |

Phase 8 implementation and deployment preparation completed on 2026-09-30.
Managed deployment verification remains blocked on the project owner's Neon,
OIDC and Vercel account configuration. No public URL is claimed. Phase 9 has not
started.
