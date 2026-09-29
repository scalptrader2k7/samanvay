# Phase 9 reviewer interface contract v0.1

The interface is a thin client of the Phase 8 `/api/v1` contract. It does not
normalize descriptions, retrieve candidates, compare attributes, decide identity,
create codes or calculate dashboard counts locally.

The connection bar accepts a workspace ID and optional Bearer token. The token is
kept in browser session memory only. Reads omit the token when viewing a public
demonstration workspace. Approve/reject/defer/reconsider buttons remain disabled
without a token; the server still enforces ownership and derives the actor.

Views:

1. **Workspace status** uses `/health`, `/ready`, `/dashboard` and
   `/migration-preview`. Phase 8 has no upload endpoint, so the interface states
   that ingestion is administrator-seeded and never pretends a selected file was
   uploaded.
2. **Material search** uses paginated `/materials` and `/materials/search`.
3. **Review queue** consists of candidate proposals returned for an explicitly
   selected source material plus persisted decisions. There is no backend pending-
   queue resource, so the UI labels this as a working candidate queue.
4. **Comparison** uses `/pairs/{left}/{right}` and displays retrieval rank/score
   separately. Original text, IDs, organizations, compatible values, conflicts,
   missing/uncertain fields and exact evidence spans remain visible.
5. **Decisions** post to `/decisions` and `/decisions/{id}/reconsider` with a fresh
   idempotency key. Exact/near identity proposals may be approved as identity;
   possible functional equivalence uses the separate relationship type; conflicts
   cannot be approved from the UI. Reject and defer remain available.
6. **Registry/mappings** use `/registry`, `/registry/{code}`, `/mappings` and
   paginated exports. Both readable and structured descriptions are shown.

Outcome language remains: exact duplicate, near duplicate, possible functional
equivalent, conflict and no match. `insufficient_evidence` is displayed as
reviewable rather than confirmed no-match. Unknown values stay unknown. Untyped
size values are never relabeled as diameter, length or thickness.

Visual direction: cool white background, midnight-blue type/navigation, restrained
cobalt actions, minimal 4-8 px rounding, dense but readable laptop-first layout.
