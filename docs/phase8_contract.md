# Phase 8 service and storage contract v0.1

## API and validation

The FastAPI service exposes versioned `/api/v1` resources. List endpoints accept
`limit` from 1-100 and a non-negative cursor/offset. Search text is 2-200 characters;
candidate `top_k` is 1-50. Source IDs, proposed codes, reasons and idempotency keys
have explicit length/pattern limits. Validation failures return structured 422
responses; missing resources return 404; safety conflicts return 409; ownership
failures return 403; repeated idempotency keys with different payloads return 409.

Health reports process availability. Readiness additionally verifies storage and
workspace access. Large exports are generated from persisted rows with safe CSV
content handling and bounded service responses; full artifacts use downloadable
CSV/JSON responses.

## Identity and workspaces

Deployment authentication verifies managed OIDC JWT signatures, issuer and
audience. The authenticated `sub` claim is the decision actor; clients cannot send
or override it. Local development has an explicit demo-token mode controlled by
environment variables. It is rejected when deployment mode is enabled.

Every workspace has one owner subject. All writes require that owner. A designated
demonstration workspace may allow public reads but never public writes. Workspace
ownership is checked in storage on every request; a client-provided workspace ID
does not grant access.

Write endpoints require an `Idempotency-Key`. The key, request digest and stored
response are committed with the workspace state. Exact retries return the stored
response; changed payloads are rejected.

## Persistence

Local development uses one SQLite registry file per workspace plus a local owner
catalog. Deployment uses free managed PostgreSQL where feasible (Neon-compatible
`DATABASE_URL`). Each workspace's tested SQLite database image is stored as a
PostgreSQL `bytea` value. A transaction selects the workspace row `FOR UPDATE`,
deserializes into memory, runs the unchanged registry transaction, serializes the
result and updates the row/revision before commit. The server filesystem is never
the durable copy. This whole-image adapter is appropriate for the bounded demo;
Phase 10+ should migrate hot tables to native relational rows for higher concurrency.

## Retrieval and descriptions

Candidate retrieval remains the bounded Phase 4 lexical index (exact identifiers,
normalized text, useful tokens and fuzzy character trigrams). It is not semantic
search or engineering identity. If BM25 is introduced later it must be described
as lexical retrieval only.

Registry entries expose both structured evidence and a readable description. The
readable form names supported family, grade, standard, pressure, voltage and model
values. Size evidence without a supported role is called
`dimensions/specification values`; it is never guessed to mean diameter, length or
thickness. Missing/non-common fields remain explicitly unknown.

## Phase 9 design handoff

The interface brief is cool white, midnight blue and restrained cobalt, with
minimal rounding and a laptop-first review workspace. Phase 8 establishes API
schemas only and does not implement or redesign the frontend.
