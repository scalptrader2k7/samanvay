# Phase 8 progress

Read this log, `PHASE8.md`, the Phase 7 storage contract/checkpoint, current modules
and deployment notes before each iteration. Complete one task per iteration. Do not
begin Phase 9.

## 2026-09-30 Iteration 1

- Read the master-plan Phase 8 section, Phase 7 storage/registry contract, current
  modules and repository delivery references. Closed Phase 7 at its checkpoint.
- Added the bounded Phase 8 checklist, versioned API/auth/storage contract, Phase 9
  visual handoff and ten-feature implementation matrix.
- Selected FastAPI, local per-workspace SQLite, verified OIDC deployment identity,
  and a Neon-compatible PostgreSQL workspace-image adapter. PostgreSQL remains the
  durable transactional copy; no deployed filesystem persistence is assumed.
- Defined server-derived actors, owner checks, public-read-only demo behavior,
  idempotency, limits, errors and lexical-retrieval terminology.
- Added `build_readable_description`: it names supported family, grade, standard,
  pressure, voltage and model values; untyped size evidence is explicitly called
  `dimensions/specification values`; missing/non-common fields are listed unknown.
  The structured technical listing and full evidence remain unchanged.
- `py -3.13 -m unittest tests.test_phase7_registry tests.test_phase7_cli -v`:
  11 compatibility tests passed. P8-01 complete; no blocker. Next: P8-02 read API.

## 2026-09-30 Iteration 2

- Re-read iteration 1, added FastAPI dependencies and implemented workspace-scoped
  health/readiness, material listing/search, bounded lexical candidates, pair
  evidence, registry, mappings, decision history, functional relationships and
  dashboard endpoints.
- List/search outputs enforce 1-100 page limits and non-negative offsets. Candidate
  top-k is 1-50. Missing workspaces/materials and validation errors return useful
  status/detail responses.
- Dashboard counts come from persisted source records, mappings, decisions and
  relationships. Candidate retrieval is explicitly `bounded_lexical`; no BM25,
  semantic or identity claim is made.
- Added local workspace storage with hashed file paths, owner metadata and a
  public-read flag. `py -3.13 -m unittest tests.test_phase8_read_api -v`: 4 tests
  passed after closing catalog connections explicitly on Windows.
- P8-02 complete; no blocker. Next: P8-03 authenticated/idempotent writes and exports.

## 2026-09-30 Iteration 3

- Re-read iteration 2 and implemented local demo-token plus deployment OIDC JWT
  authentication. Deployment mode refuses demo authentication. Decision actors
  come only from the verified identity subject; request bodies contain no actor.
- Added owner-only approve/reject/defer/reconsider endpoints, idempotency records
  committed with registry transactions, functional-relationship writes, migration
  preview and safe CSV/JSON mapping exports. Public-read workspaces remain write-
  protected. Safety/idempotency conflicts return 409.
- Tests cover approval-to-registry-to-export, exact retry replay, changed-payload
  rejection, unauthenticated writes, cross-owner denial, critical conflict,
  reconsideration, functional separation and fresh-app restart persistence.
- `py -3.13 -m unittest tests.test_phase8_write_api -v`: 3 tests passed. P8-03
  complete; no blocker. Next: P8-04 managed durable storage and Vercel preparation.

## 2026-09-30 Iteration 4

- Re-read iteration 3 and implemented `PostgresWorkspaceStorage`. A Neon-compatible
  PostgreSQL transaction locks the owned workspace row, restores its SQLite image
  into memory, runs the tested registry logic, and atomically stores the new image
  and revision. No deployed filesystem contains the durable copy.
- Added managed schema SQL, owner-controlled workspace creation, seed utility,
  environment placeholders, Python 3.13 selection, Vercel ASGI entrypoint/config
  and exact free Neon/OIDC/Vercel setup steps. Local SQLite remains supported.
- Added tests proving database-image roundtrip preserves code, readable description,
  history and idempotency. Deployment mode refuses demo auth. All 9 Phase 8 service
  tests passed across read/write/storage groups (the framework emits a harmless
  TestClient deprecation warning).
- Official Vercel documentation confirms FastAPI ASGI apps, Python 3.13,
  requirements files, environment variables and function file exclusions are
  supported. P8-04 implementation complete; live managed integration remains an
  external-account check. Next: P8-05 final contract/check report.

## 2026-09-30 Iteration 5

- Verified a real local workspace seeded with all 9,245 records and 10 warnings.
  Health, readiness, paginated materials, lexical candidates and dashboard calls
  returned HTTP 200. Added bounded/paginated JSON and CSV exports for mappings,
  unresolved records, conflicts, registry, decisions and functional relationships.
- Maintained the ten-feature matrix. Generated an OpenAPI contract and deployment
  report. The Vercel CLI is installed (`59.11.7`), but the checkout is unlinked and
  `DATABASE_URL`, OIDC settings and `VERCEL_TOKEN` are absent. No live deployment
  or public URL can be truthfully verified.
- Final focused checks are recorded in the Phase 8 report/checkpoint. P8-05 is
  complete with the external account setup blocker documented. Phase 9 has not
  started.
- Final compilation/OpenAPI generation passed with 23 FastAPI routes. The focused
  dependency suite passed 36 tests in 12.440 seconds; all three protected raw-file
  hashes passed. `git diff --check` passed apart from informational Windows
  line-ending warnings.
