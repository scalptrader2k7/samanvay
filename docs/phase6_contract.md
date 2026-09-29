# Phase 6 evaluation contract v0.1

The evaluation unit is an unordered pair keyed by the sorted pair of distinct
source record IDs. A-to-B and B-to-A proposals collapse only for sampling; both
source IDs, organizations, original descriptions and available evidence remain in
the review row. Source records and prior output packs are read-only.

The sample contains 100 deterministic pairs with quota coverage across all five
automated proposed outcomes. Selection also seeks cross-organization pairs,
explicit pipe/valve/cable/pump families, missing or uncertain attributes and
critical conflicts. This is a review sample, not a random population estimate.

Automated fields use an `automated_` prefix. Human fields use a `human_` prefix and
are blank at generation. Automated outcomes and AI/rule suggestions are never
called human labels or ground truth.

`automated_evidence_disposition` distinguishes:

- `supported_incompatibility`: explicit family or supported critical evidence
  rules out identity for the proposed pair;
- `insufficient_evidence`: available text/attributes do not justify a relationship
  or a confirmed incompatibility; the pair remains reviewable;
- `supported_duplicate_text`, `supported_near_duplicate`, and
  `reviewer_equivalence_candidate`: the corresponding positive proposal bases.

The human reviewer may record a judgment independently, including
`insufficient_evidence`. Blank means unreviewed. Metrics use only rows with valid
human judgments and report the labeled denominator and sample scope. With zero
labels, the utility reports `validation_pending` and emits no accuracy, precision,
recall or confusion counts. Partial labels never use the full sample as a metric
denominator.

The error log records suspected rule/extraction problems and review questions. It
does not silently change human fields. Phase 6 does not merge records, assign
common codes, start a registry, or build the backend/interface.
