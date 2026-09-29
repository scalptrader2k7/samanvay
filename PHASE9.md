# Phase 9 reviewer interface

Phase 8 is closed at `docs/phase8_checkpoint.md`; managed deployment verification
remains pending account setup. Phase 9 builds a browser reviewer interface using
the existing API only. Do not begin Phase 10.

Each Ralph iteration completes one coherent task, runs focused checks and updates
`docs/phase9_progress.md`.

| Task | Status | Deliverable | Acceptance check |
|---|---|---|---|
| P9-01 | Complete | Frontend/API audit, reviewer journey and bounded interface contract. | Exact endpoints/auth/pagination are mapped; missing upload and persisted queue APIs are represented honestly; no business logic is duplicated. |
| P9-02 | Complete | Laptop-first application shell, connection/status and material search. | Browser loads from FastAPI; public reads work; status/counts and paginated search are clear; upload availability is truthful. |
| P9-03 | Complete | Candidate queue and side-by-side evidence workspace. | Reviewer can open a real candidate, distinguish all five outcomes, inspect source IDs/original text/attributes/evidence/conflicts/unknowns, and see retrieval score separately. |
| P9-04 | Complete | Authenticated decisions, reconsideration, registry/mappings and exports. | Owner can approve/reject/defer and reconsider with reason/idempotency; public visitor cannot edit; updated decision/registry/mapping state is visible. |
| P9-05 | Complete | End-to-end browser verification, focused regression and report. | Real local-data browser journey proves a reviewer can trace and approve or reject without CLI; raw hashes pass; Phase 10 remains unstarted. |
