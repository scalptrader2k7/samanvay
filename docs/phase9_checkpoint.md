# Phase 9 checkpoint

Phase 9 is complete. The existing FastAPI service now serves a practical browser
reviewer interface at `/`. A reviewer can browse or search real source materials,
open bounded lexical candidates, trace a pair through original IDs/text and
field-level evidence, record an owner-authorized decision, and see the resulting
decision, prototype registry entry and source mappings without using the command
line.

The verified full-data path used M000753 and rank-1 candidate M000925. The page
displayed `near_duplicate`, kept retrieval rank/score separate, showed missing
critical specifications as `UNKNOWN`, and submitted an approval with a reason and
idempotency key. The server returned stable prototype code SMV-P-51AEF0D48CE7;
the registry then showed its readable description, structured evidence and both
source IDs. This local demonstration decision is not a human evaluation label.

Public visitors can read the configured demo workspace but the UI does not enable
writes without a token. The service still verifies token identity, ownership,
request limits, idempotency and registry safety. Conflict/no-match pairs cannot be
approved as identities in the UI; possible functional equivalence uses the
separate relationship operation.

The Phase 8 contract has no upload endpoint or persisted global pending-review
queue. Upload is therefore visibly unavailable, and the working queue contains
candidates for the selected source material. Managed Neon/OIDC/Vercel verification
remains pending the account setup already recorded for Phase 8. No public URL is
claimed.

Verification: the Phase 9/Phase 8 focused run passed 12 tests; the final Phase 5-9
dependency group passed 47 tests; three additional dependency groups passed 28,
18 and 9 tests. JavaScript syntax, Python compilation and diff checks passed. All
three protected raw-file hashes passed. Phase 10 has not started.
