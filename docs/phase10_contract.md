# Phase 10 governance contract

Phase 10 extends the existing workspace database and transaction boundary. It does
not add another persistence system. PostgreSQL deployment continues to persist the
whole transactional workspace image; local development continues to use SQLite.

Existing `decisions` rows remain immutable history. A reconsideration appends a
new decision linked by `supersedes_decision_id`; it never edits the prior decision.
The latest non-superseded row is the current pair decision. Registry membership and
functional relationships continue to be changed only by the tested registry logic.

Each decision transaction appends one governance event containing its workspace,
event/action/relationship types, affected source IDs, server-derived actor, time,
reason, input snapshots available on those records, rule versions, and before/after
governance state. Each changed source mapping also appends a mapping-change row
with previous/new status and prototype code. Database triggers reject update or
delete against both audit tables.

Roles remain deliberately small. A public visitor has `view_review`; the verified
workspace owner has `view_review`, `review_decide`, and `governance_reconsider`.
These reported capabilities describe the existing access checks; write enforcement
continues to use authenticated server identity and storage ownership.

No source record is updated by a decision or reconsideration. Input versions come
from stored source records (`source_sha256`, `mapping_id`, `schema_version`), and
rule versions use the recorded normalization/parser versions plus the implemented
pair-evidence and registry versions. Missing version metadata is represented as
unknown/null, never invented.
