# Phase 7 registry contract v0.1

## Identity and codes

Every registry code is a stored opaque identifier shaped like `SMV-P-XXXXXXXXXXXX`.
`P` means prototype/proposed. The random suffix has no material semantics and is
never derived from organization, family or source codes. Once persisted, a code is
stable across reloads and repeat operations. It is not an official CPSE, SAP or
legacy material code.

Registry membership requires an explicit `approve` action for the `identity`
relationship. Automated pair outcomes only supply review evidence. `reject` and
`defer` create decision history without membership. `reconsider` supersedes a
prior decision while retaining both records and reasons.

Possible functional equivalence uses a separate relationship record. Approving it
does not create or combine registry membership. It always remains a qualified
review relationship rather than established identity.

## Group safety and descriptions

Before identity approval, every unordered pair of proposed members is compared.
Any supported critical conflict blocks the transaction. Pairwise links are never
closed transitively: A-B and B-C evidence does not establish A-C. A functional-
equivalence-only pair cannot create a shared identity group. Ambiguous or
insufficient evidence stays reviewable and cannot act automatically.

A standard description is derived from explicit family and attribute evidence
shared compatibly by every active member. It includes `UNKNOWN` for missing or
non-common fields. Each emitted value retains the contributing source IDs, exact
source substrings, offsets and rule IDs. No inferred label or specification is
inserted.

## Source mappings and identifiers

Mappings preserve organization, internal `source_record_id`, original description,
the complete source identifier dictionary and active proposed code. The
`source_record_id`/`corpus_id` is an internal row locator and is never exported as
an official material code. Only explicitly named upstream fields such as
`material_code`, `cpse_material_code`, `legacy_material_code` or
`sap_material_code` qualify as genuine material codes. Tender references remain
provenance identifiers, not material codes. Missing genuine material codes are
reported as missing, never fabricated.

## Decisions, warnings and storage

Every action records actor, UTC timestamp, reason, relationship type, requested
members, resulting code/relationship and any superseded decision. Transactions
roll back completely on safety or validation failure. Phase 6 error findings are
attached as review warnings when their source IDs can be resolved from the Phase 6
sample; reusable warning patterns remain available for later service review.

SQLite is the local development implementation and restart-persistence test
boundary. Phase 8 must place the database on durable storage or replace it with a
managed transactional database. A deployed server's ephemeral local filesystem is
not an acceptable persistence layer.

Migration preview and exports are read-only. They distinguish mapped records,
unresolved records, supported conflicts, missing genuine material codes and
functional relationships. CSV and JSON exports preserve originals and clearly
mark prototype status.
