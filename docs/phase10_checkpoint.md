# Phase 10 checkpoint

Phase 10 is complete. The master-plan acceptance criterion passed: a browser-made
override persisted across service restart, and no source record was overwritten.

Decisions and reconsiderations now append workspace-scoped governance events in the
same transaction as registry and mapping changes. Each event records affected
source IDs, server-derived actor, timestamp, reason, available input versions,
normalization/parser/pair/registry rule versions, and complete before/after mapping
and functional-relationship state. Changed mappings append individual previous/new
rows. Database triggers reject update/delete of audit events, mapping history,
decisions and source records.

Decision history exposes current versus superseded rows. Reconsideration appends a
new linked decision; only the current row can be reconsidered, so history cannot
branch through a stale override. Existing idempotency, all-member safety, rollback,
workspace ownership and managed workspace-image transactions remain intact.

The browser Governance screen shows owner/public capabilities, actor, timestamp,
reason, affected IDs, state transitions, mapping changes and expandable version
evidence. Public visitors have view-only capability. The authenticated workspace
owner has review-decision and governance-reconsider capability; server storage
checks remain authoritative.

Real-data evidence used M004773/M004774 from the 9,245-record workspace. Browser
approval created prototype SMV-P-4E5553D44FB6; reconsideration rejected the pair and
returned both mappings to unresolved. After restart, two immutable decisions, two
audit events and four pair-level mapping changes remained. The current action was
reject. The complete stored source snapshot digest remained
`c6eafe5ffcf8389347cf469e14d89f34b5a797aa3524f81f1618a54a55a2ac2a`.

Final validation: 53 Phase 5-10 dependency tests passed, followed by 21 focused
tests after the final stale-override guard. JavaScript syntax, Python compilation,
OpenAPI generation and all three protected raw hashes passed. Phase 11 has not
started.

Limitations: governance events begin with Phase 10 actions; older Phase 7-9 decision
rows remain visible but are not assigned fabricated audit/version snapshots. The
role model intentionally remains public viewer versus authenticated workspace
owner rather than adding delegated enterprise IAM. Managed Neon/OIDC/Vercel
verification is still pending the account setup documented in Phase 8.
