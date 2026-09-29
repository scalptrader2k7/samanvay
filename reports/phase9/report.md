# Phase 9 reviewer-interface implementation report

## Before Phase 9

The repository had the complete Phase 8 FastAPI contract and persistence layer,
but no HTML, CSS, JavaScript, frontend framework or browser test. It also had no
upload endpoint and no persisted server-side pending-review queue.

## Implemented

- A cool-white, midnight-blue and restrained-cobalt laptop-first application shell.
- Workspace status from real health, readiness, dashboard and migration counts.
- Paginated material browse/search and a selected-material candidate queue.
- Side-by-side source IDs, organizations, untouched descriptions, five proposed
  outcomes, separate retrieval rank/score, and field evidence/conflicts/unknowns.
- Owner actions for approve, reject, defer and reconsider, with reasons and fresh
  idempotency keys. Conflict/no-match identity approval is disabled; possible
  functional equivalence remains a separate relationship.
- Persisted decision history, prototype registry cards, readable and structured
  descriptions, source mappings, legacy-code status and bounded CSV/JSON exports.
- Public-read presentation with write controls gated by a token while all real
  authentication, ownership, RBAC and safety enforcement stays on the server.

## APIs consumed

`/health`, `/ready`, workspace `/dashboard`, `/migration-preview`, `/materials`,
`/materials/search`, material `/candidates`, `/pairs/{left}/{right}`, `/decisions`,
decision `/reconsider`, `/registry`, `/mappings`, and `/exports/{dataset}.{format}`.
All list/export calls retain the Phase 8 bounds and pagination behavior.

## Acceptance verification

Local headless Chrome loaded the live service with 9,245 real source records,
searched M000753, opened M000925 at rank 1, and showed the proposed near-duplicate
outcome with both original descriptions, supported size/standard evidence and
unknown material grade, pressure and voltage. Approval was submitted in the page;
the resulting stable code SMV-P-51AEF0D48CE7 and both mappings were visible in the
registry. The criterion that a reviewer can trace and approve or reject one match
without a command line is met.

Checks: `node --check frontend/app.js`; 12 focused Phase 8/9 tests; 47 Phase 5-9
dependency tests; three other dependency groups of 28, 18 and 9 tests; Python
compilation; diff check; and three raw-file SHA-256 checks all passed. The browser
evidence image is `browser_workflow.png` in this directory.

## Limitations and deferred work

Upload remains visibly disabled because no backend upload route exists. The review
queue is scoped to candidates for the selected material because no persisted
pending-queue route exists. Exports are limited to 1,000 rows per request by the
existing safe API bound. Managed deployment and public-URL validation still need
Neon/OIDC/Vercel account setup. These are explicit constraints; no backend feature
is fabricated. Phase 10 has not started.
