# Phase 3 progress

Read this file, `PHASE3.md`, the Phase 2 checkpoint/input contract and current code
before each iteration. One task per iteration. Do not begin Phase 4.

## 2026-09-27 Iteration 1

- Selected P3-01 after closing Phase 2 in `docs/phase2_checkpoint.md`, retaining
  the prior 38-test/hash verification as Codex-reported evidence pending independent inspection.
- Inspected Phase 2 records/loaders, Phase 1 Boolean extractors, candidate headers,
  and real pipe/valve/cable/pump descriptions. Phase 1 rules are retained as
  historical flags and will not be treated as extracted values or ground truth.
- Added the Phase 3 checklist and derivation contract. Exact source spans are
  mandatory; uncertain/missing values stay absent; multi-family text is ambiguous;
  power/current/frequency are not mislabeled as voltage; Phase 3 makes no matches.
- Acceptance check: contract covers preservation, normalization, evidence,
  uncertainty, requested attributes and exclusions. P3-01 complete; no blocker.
- Next: P3-02 normalization and family evidence. Phase 4 not started.

## 2026-09-27 Iteration 2

- Re-read iteration 1 and implemented only normalization/family derivation in
  `phase3_attributes.py`; source records are copied, never mutated.
- Normalization is NFKC/whitespace/punctuation-spacing only and idempotent. An
  initial test caught `A2 X 3` being treated like a numeric dimension; the rule
  was narrowed so only standalone numeric dimensions change spacing.
- Explicit whole-word family evidence supports pipe, valve, cable and pump.
  Multi-family M000342/M000093 stay unknown with exact evidence for ambiguity.
- `py -3.13 -m unittest discover -s tests -p test_phase3_normalization.py -v`:
  4 tests passed, including all 9,245 candidates for original description/ID and
  evidence-span integrity. P3-02 complete; no blocker. Next: P3-03 attributes.

## 2026-09-27 Iteration 3

- Re-read iteration 2 and implemented conservative extraction for size/dimension,
  material/grade, standard, pressure, voltage and explicit model/part labels.
- Every result has exact raw text, normalized display value, source offsets and
  rule ID. All 9,245 records passed span and identity preservation checks.
- Focused real checks cover ASTM A312 pipe dimensions, A312-TP304L/80S, API 6D
  valve at 300 Class versus API 6A valve at 5000 PSI, 11KV/150MM2 cable, API 610
  pump and an explicitly labeled pump model. Plain pump text remains empty.
- A first focused run exposed reversed `300 Class`; a narrow evidence rule was
  added. `py -3.13 -m unittest discover -s tests -p test_phase3_attributes.py -v`:
  6 tests passed. No match decision was made; distinct conflicts stay distinct.
- P3-03 complete; no blocker. Next: P3-04 full enrichment/report/exit checks.

## 2026-09-27 Iteration 4

- Re-read iteration 3 and added `phase3_enrich.py`, a no-overwrite full-candidate
  enrichment pack with manifest, report and real example records.
- Generated final `output/phase3-v0.1/` (Git-ignored reproducible full output) and retained
  compact `reports/phase3/report.json`, `examples.json`, and human-readable review.
  All 9,245 input/output rows, unique source IDs and original descriptions reconcile;
  no rows were dropped. The input candidate SHA-256 is recorded.
- Derived coverage (not accuracy): family pipe 1,172; valve 396; cable 266; pump
  505; unknown/ambiguous 6,906. Records with evidence: size 1,539; grade/material
  166; standard 378; pressure 206; voltage 283; explicit model/part 63.
- Reviewed real evidence for all requested families. Critical-difference checks
  preserve 300 Class/API 6D versus 5000 PSI/API 6A valves, 15MM versus 25MM pipes,
  and 150MM2 versus 240MM2 11KV cables. These should not be exact-identity merges
  without qualified review; Phase 3 does not assign pair labels or scores.
- `py -3.13 -m unittest discover -s tests -p test_phase3_enrich.py -v`: 1 focused
  pack test passed. Final `py -3.13 -m unittest discover -s tests -v`: 49 tests
  passed before the final model/conflict test refinement; a final rerun follows.
- `python verify_raw_data.py`: all three raw hashes passed. Protected Phase 1/2
  data and reports remained unchanged. P3-04 complete pending the recorded final
  rerun below; no decision blocker. Phase 4 not started.

- Output note: an earlier pre-refinement pack remains at ignored `output/phase3/`.
  Automatic policy rejected its recursive removal. It is superseded by
  `output/phase3-v0.1/`; only the latter is the final Phase 3 pack.

- Final refinement retained the complete explicit model `MODEL NAT 12 P 160` and
  added real pipe/cable conflict assertions. Regenerated the final pack and compact
  reports. Final full regression: `py -3.13 -m unittest discover -s tests -v`:
  **50 tests passed**. Phase 3 exit checks pass and the phase is ready to close.
