# Phase 6 pair review guide

This 100-pair sheet prepares human evaluation. `automated_*` columns are rule
outputs and suggestions. They are not human judgments or ground truth. Fill only
the blank `human_*` columns; do not edit source or automated fields.

Review both original descriptions, source IDs, organizations, identifiers,
retrieval directions, missing fields and conflict evidence. Missing information is
unknown. Do not count it as agreement or disagreement.

Allowed `human_judgment` values:

- `exact_duplicate`: the records describe the same source item identity.
- `near_duplicate`: the same item is described with minor wording differences.
- `possible_functional_equivalent`: a qualified reviewer considers engineering
  substitution plausible; this is distinct from identity.
- `conflict`: supported comparable specifications make identity unsafe.
- `no_match`: evidence supports that the records refer to different items.
- `insufficient_evidence`: the supplied records do not support either a match or
  a confirmed no-match.

Use `human_confidence` as `high`, `medium`, or `low`. Explain decisive source text
in `human_reason`, enter a reviewer identifier, and use an ISO-8601 timestamp in
`human_reviewed_at`. If engineering competence is required and unavailable, choose
`insufficient_evidence` and explain the escalation need.

Safety checks:

1. Exact duplicate requires equal normalized descriptions. Missing specifications
   remain unknown and may still warrant review.
2. A supported difference in comparable size, pressure, voltage, grade or standard
   takes priority over similar wording.
3. Compare only the same technical meaning and compatible units. Do not equate
   diameter with length/area or pressure Class with PSI.
4. `supported_incompatibility` identifies an explicit family/critical conflict.
   `insufficient_evidence` is reviewable and is not a confirmed no-match.
5. Possible functional equivalence never creates identity, a merge, or a common
   code in this phase.

Metrics remain unavailable until at least one valid human judgment exists. Any
later metric must report its labeled denominator and this sample's limited scope.
