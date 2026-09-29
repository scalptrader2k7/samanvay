# Phase 8 backend and deployment-preparation report

Phase 8 implementation is complete; managed deployment verification is pending
external account configuration. Phase 9 has not started.

The FastAPI service exposes health/readiness, paginated materials/search, bounded
lexical candidates, pair evidence, proposed registries/mappings, authenticated
decisions/reconsideration, functional relationships, migration preview, bounded
CSV/JSON exports and dashboard counts from persisted data.

Writes derive the actor from a verified identity, enforce workspace ownership and
require idempotency keys. Public demonstration workspaces are read-only to visitors.
Critical/all-member registry safety, stable codes, rollback and history reuse the
Phase 7 implementation.

Registry entries retain the technical field listing and add a readable description.
Untyped dimensions are called `dimensions/specification values`; the service does
not guess diameter, length or thickness. Missing fields remain unknown.

Local development uses per-workspace SQLite. Deployment uses a Neon-compatible
PostgreSQL row as the durable transactional workspace image. Requests lock the row,
operate on an in-memory SQLite database and atomically update the image/revision.
No Vercel filesystem persistence is assumed. This is a bounded demo architecture;
high-concurrency production should migrate active tables to native PostgreSQL rows.

Local full-data checks seeded 9,245 source records and 10 warnings. Health,
readiness, material listing, candidate retrieval and dashboard returned HTTP 200.
Focused tests cover approval-to-registry-to-export, reconsideration, local restart,
idempotency, conflict rollback, readable descriptions, access isolation and image
roundtrip.

Deployment blocker: Vercel CLI 59.11.7 is installed, but the checkout is not linked
and no `DATABASE_URL`, `OIDC_ISSUER`, `OIDC_AUDIENCE`, `OIDC_JWKS_URL` or
`VERCEL_TOKEN` is available. The owner must create/link the free Neon, managed OIDC
and Vercel projects using `docs/phase8_deployment.md`. No public URL is claimed.
