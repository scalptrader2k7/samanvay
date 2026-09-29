# Phase 3 description normalization and technical attributes

Phase 2 is closed at `docs/phase2_checkpoint.md`. Phase 3 operates on common input
records and preserves `source_record_id`, all source identifiers and
`description_original` verbatim. It produces transparent derived fields only.

Each Ralph iteration selects one task, runs its checks, records the result in
`docs/phase3_progress.md`, then re-reads that log before continuing. Stop at a
decision blocker or after the Phase 3 exit checks. Do not begin candidate matching.

| Task | Status | Deliverable | Acceptance check |
|---|---|---|---|
| P3-01 | Complete | Lock normalization, evidence, uncertainty and output contracts from real descriptions. | Contract distinguishes original/normalized text, exact spans, supported values, unknowns and exclusions; Phase 2 checkpoint is recorded. |
| P3-02 | Complete | Implement conservative description normalization and family extraction. | Original text/IDs unchanged; normalization is deterministic/idempotent; family has exact evidence or is unknown; pipe, valve, cable and pump examples plus ambiguous multi-family text pass. |
| P3-03 | Complete | Extract size/dimension, grade/material, standard, pressure, voltage and model/part values with evidence spans. | Every value reproduces its exact source substring; missing/uncertain values remain absent; duplicates are retained; conflict examples keep different technical values distinct. |
| P3-04 | Complete | Enrich all provisional candidates and emit a versioned report/example review set. | 9,245 input/output rows and IDs reconcile; original descriptions match byte-for-byte decoded cells; family examples and no-match/conflict cases pass; raw hashes and full regressions pass; reports make coverage and limitations explicit. |

Exit does not measure extraction accuracy because no human gold labels exist. It
requires deterministic processing, evidence integrity, conservative unknowns and
reviewed real examples across the four requested families. Phase 4 remains out of scope.

All Phase 3 checks passed on 2026-09-27. See `reports/phase3/report.json`,
`reports/phase3/review_examples.md` and the progress log. Phase 3 is ready to close;
the coverage counts are not accuracy. Stop here. Phase 4 has not started.
