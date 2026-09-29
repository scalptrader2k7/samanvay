# Phase 8 checkpoint

Phase 8 backend implementation and deployment preparation are complete. Live
managed deployment validation is pending external account setup. No public URL is
claimed. Phase 9 has not started.

The service contract, local SQLite storage, PostgreSQL durable adapter, managed
OIDC authentication path, workspace ownership, idempotent decisions, exports,
dashboard, Vercel entrypoint and setup documentation are implemented. Existing
stable-code, all-member conflict, rollback and audit-history semantics are retained.

Local API verification used all 9,245 source records. The managed PostgreSQL path
could not be exercised because no database URL is present. Vercel deployment could
not be exercised because the checkout is unlinked and no Vercel/OIDC credentials
are present. Exact owner actions are in `docs/phase8_deployment.md`.

The next phase is Phase 9's laptop-first reviewer interface using cool white,
midnight blue and restrained cobalt with minimal rounding.

Final verification: 23 routes were emitted in OpenAPI; 36 focused safety,
registry, CLI, read API, write API and storage tests passed in 12.440 seconds;
Python compilation and all three raw-file hashes passed.
