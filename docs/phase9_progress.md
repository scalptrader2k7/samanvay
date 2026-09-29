# Phase 9 progress

Read this log, `PHASE9.md`, the Phase 8 API/checkpoint and current frontend files
before each iteration. Complete one task per iteration. Do not begin Phase 10.

## 2026-09-30 Iteration 1

- Re-read the master-plan Phase 9 section and audited the repository. No frontend,
  HTML, CSS, JavaScript framework or browser tests existed.
- Audited the 23-route OpenAPI contract: reads are paginated; candidate retrieval
  is bounded lexical; pair evidence is separate; writes require Bearer identity,
  ownership and `Idempotency-Key`; exports are paginated.
- Identified two missing backend resources and documented honest UI behavior:
  ingestion is admin-seeded because no upload endpoint exists, and the working
  review queue is built from selected-material candidates plus persisted decisions
  because no pending-queue endpoint exists.
- Added the bounded checklist and thin-client contract. P9-01 complete; no blocker.
  Next: P9-02 application shell, status and search.

## 2026-09-30 Iteration 2

- Added a laptop-first reviewer application served at `/` by the existing FastAPI
  service, with static assets under `/static`.
- Added workspace connection state, health/readiness and real dashboard counts,
  paginated browse/search, and an explicit disabled ingestion control explaining
  that Phase 8 exposes no upload endpoint.
- Kept public reads separate from token-gated owner actions; the browser stores the
  optional demo token in session storage and the server remains the authority.
- Focused check: `python -m pytest tests/test_phase9_frontend.py
  tests/test_phase8_read_api.py tests/test_phase8_write_api.py
  tests/test_phase8_storage.py -q` -> 12 passed.
- P9-02 complete; no blocker. Next: P9-03 candidate queue and comparison evidence.

## 2026-09-30 Iteration 3

- Re-read iteration 2 and connected selected materials to the existing bounded
  lexical candidate endpoint and pair-evidence endpoint. The working queue is
  deliberately described as selected-material candidates because Phase 8 has no
  persisted pending-queue resource.
- Added a side-by-side view of source IDs, organizations and untouched original
  descriptions, plus field-level compatible/conflict/not-comparable/missing
  evidence. Unknown values render as `UNKNOWN`; retrieval rank/score stays outside
  the proposed pair outcome.
- Added a visible legend for exact duplicate, near duplicate, possible equivalent,
  conflict and no match. Identity approval is disabled for conflict/no-match, and
  possible equivalence maps only to the separate functional relationship.
- Focused checks: `node --check frontend/app.js` passed. Live full-data calls found
  M000925 at rank 1 for M000753; the comparison returned `near_duplicate`, preserved
  both IDs and exposed material-grade, pressure and voltage as unknown.
- P9-03 complete; no blocker. Next: P9-04 decisions, registry and mappings.

## 2026-09-30 Iteration 4

- Re-read iteration 3 and connected owner actions to the existing decision and
  reconsideration endpoints. Every write supplies a reason and UUID idempotency
  key; identity or functional relationship semantics come from the pair outcome,
  and the server remains responsible for ownership and all-member safety checks.
- Added persisted decision history, reconsideration controls, prototype registry
  cards, readable descriptions, structured evidence, source mapping rows and safe
  paginated CSV/JSON export controls.
- A headless Chrome run used the real 9,245-record local workspace: it searched
  M000753, opened rank-1 M000925, displayed the near-duplicate evidence and unknown
  values, approved through the page, received stable code SMV-P-51AEF0D48CE7, and
  then displayed both source IDs in the registry. The action is isolated to the
  ignored local demonstration workspace and is not an evaluation label.
- Existing Phase 8 write tests continue to cover reject, defer, reconsider,
  idempotent replay, public write denial and cross-owner denial.
- P9-04 complete; no blocker. Next: P9-05 final browser/regression/raw-hash report.

## 2026-09-30 Iteration 5

- Re-read iteration 4 and completed the live browser acceptance path using local
  headless Chrome and the full-data FastAPI service. The registry view was reloaded
  and visibly showed code SMV-P-51AEF0D48CE7, its readable/structured descriptions
  and members M000753/M000925. A screenshot is retained under `reports/phase9/`.
- Focused Phase 5-9 dependency suite: 47 tests passed in 11.272 seconds. Earlier
  dependency groups added 28, 18 and 9 passing tests; the Phase 9 plus Phase 8
  focused run passed 12 tests. `node --check`, Python compilation and `git diff
  --check` passed (line-ending notices only).
- `python verify_raw_data.py` passed all three protected raw snapshot hashes.
- Recorded the implementation report and checkpoint. P9-05 and Phase 9 are
  complete; no product blocker. File ingestion, a persisted global pending queue
  and managed deployment verification remain explicitly deferred because their
  Phase 8 APIs/accounts do not exist. Phase 10 has not started.
