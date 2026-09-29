# Phase 5 checkpoint

Phase 5 is closed. Its authoritative reproducible pack is
`output/phase5-v0.1/`; compact tracked evidence is in `reports/phase5/`. Inputs
remain the frozen Phase 3 records and Phase 4 candidates.

The pack reconciles 9,245 query records and all 89,381 retrieved directed pairs.
Generation took 12.595633 seconds. The deterministic rule outputs are 4,476 exact
duplicate, 3,352 near duplicate, 10,529 possible functional equivalent, 6,804
conflict and 64,220 no match. These counts are not accuracy metrics. The system
performed zero automatic merges and assigned zero common codes.

Verification at checkpoint:

- 16 focused Phase 5 tests passed, including all five outcomes, critical conflict
  precedence, compatible units, incompatible meanings/rating bases, missing
  values, source-span traceability, retrieval-score separation and CLI output.
- The full regression passed 75 tests in 74.018 seconds; the final added
  generic-shared-word focused test also passed afterward.
- All seven named real/hard rule checks passed. The manifest, no-overwrite guard,
  frozen-input hash checks and pair-count reconciliation passed.
- All three protected raw-file SHA-256 checks passed. Source IDs, original text and
  repeated records remain intact.

Limitations: rules have not been validated against human labels; extracted roles
can remain ambiguous; missing evidence remains unknown; pressure Class, PN and
physical pressure are not equated; and possible functional equivalence remains a
qualified-review suggestion only. The repository contains a Python/CLI interface,
not a backend service or comparison-workspace screen, so no UI integration was
available in this phase.

Closure note: the 89,381 count is directed and may include both A-to-B and B-to-A.
Phase 6 deduplicates those directions for review sampling and distinguishes a
supported no-match incompatibility from insufficient evidence. The Phase 5 pack
itself remains frozen.
