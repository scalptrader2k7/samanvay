# Phase 6 evaluation-preparation report

Phase 6 preparation is complete; human validation remains pending.

The frozen Phase 5 pack contains 89,381 directed candidate pairs. Sampling
collapsed reverse directions to 63,531 unique unordered pairs and selected 100
deterministically: 20 for each proposed outcome. The sample retains both source
IDs, organizations, source identifiers, original descriptions and all available
retrieval directions. Eight sampled pairs cross organizations; pipe, valve, cable,
pump and unknown-family cases are present. All 100 human-review fields are blank.

The review layer distinguishes `supported_incompatibility` from
`insufficient_evidence`. Eighteen sampled rows have insufficient evidence and
remain reviewable; they are not confirmed no-matches. Twenty-two rows carry a
supported incompatibility disposition, including the 20 critical-conflict cases.

Automated invariant inspection passed: all 20 exact-duplicate proposals have equal
normalized descriptions, with missing specifications still unknown; all 20
conflict proposals contain supported critical-conflict reasons; and critical
conflicts retain priority over similar wording.

Ten suspected rule problems are recorded in `error_log.csv` without assigning
human labels. They include missed fractional sizes/grades, spare-versus-item scope,
grade alias conflicts, malformed pressure numbers, missing family support and a
likely contextual family false positive.

The current sample has zero human labels. `metrics.json` therefore reports
`pending_human_review` and contains no accuracy, precision, recall or confusion
metrics. The metrics utility's clearly marked fixtures verify entirely unlabeled,
partially labeled and invalid-label behavior.

No source data or prior output pack was modified. Phase 7 registry and mapping work
has not started.
