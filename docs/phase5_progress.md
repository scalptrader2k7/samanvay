# Phase 5 progress

Read this log, `PHASE5.md`, the Phase 5 contract, Phase 4 checkpoint/progress and
current code before each iteration. Complete one task per iteration. Do not begin
Phase 6.

## 2026-09-30 Iteration 1

- Re-read the master-plan Phase 5 section, Phase 4 contract/progress/report and
  current retrieval and extraction code. Confirmed that the repository has no
  backend service or comparison-workspace screen; the existing product surface is
  Python module/CLI output.
- Closed Phase 4 in `docs/phase4_checkpoint.md` with its verification evidence and
  limitations. The authoritative pack remains `output/phase4-v0.1/`.
- Added the bounded Phase 5 checklist and contract. It separates retrieval ranking
  from outcomes, defines same-meaning/unit comparison, makes critical conflicts
  precede textual similarity, treats missing values as unknown and defines all five
  requested proposed outcomes. Functional equivalence is reviewer-only.
- Documentation checks: task IDs P5-01..P5-04, five outcome definitions, decision
  order, critical fields, review behavior and prohibited actions are present.
- P5-01 complete; no blocker. Next: P5-02 field comparator and safety gate.

## 2026-09-30 Iteration 2

- Re-read iteration 1 and added `pair_evidence.py`. It validates every attribute
  span against original text and compares values only within explicit semantic
  types. Voltage is canonicalized to volts; bar/PSI share a physical pressure
  type; Class, PN and physical pressure remain separate rating systems.
- Missing evidence is `unknown`. Role/parse ambiguity and different non-pressure
  semantic types are `uncertain`, not agreement. Pressure evidence on incompatible
  bases is a conservative safety conflict without equating the numbers.
- Critical conflicts in size/dimension, grade, standard, pressure or voltage set
  `identity_merge_blocked` before later outcome logic.
- `py -3.13 -m unittest discover -s tests -p test_phase5_comparison.py -v`:
  6 tests passed. Real cases covered 15/25 mm pipe size, 150/240 mm2 cable area,
  matching pipe specifications, Class 300 versus 5000 PSI, and missing pump specs;
  a deliberate case verified 1 kV equals 1000 V while mm is not compared to mm2.
- `py -3.13 verify_raw_data.py`: all three protected raw hashes passed.
  `git diff --check` passed. P5-02 complete; no blocker. Next: P5-03 outcome
  engine and readable module/CLI result.

## 2026-09-30 Iteration 3

- Re-read iteration 2 and added the deterministic outcome layer to
  `pair_evidence.py`. Decision order is critical conflict, explicit family no-match,
  exact duplicate, near duplicate, possible functional equivalent, then no-match.
- Results retain both IDs, organizations and original descriptions; supporting
  text signals; field-level compatible/conflict/missing/uncertain evidence; review
  state and explanations. Retrieval rank/score/reasons live only in `retrieval`
  and changing the score cannot change the outcome.
- Added `phase5_compare.py` as the repository's existing Python/CLI interface.
  There is no backend service or comparison-workspace screen in this repository,
  so no frontend integration was applicable.
- `py -3.13 -m unittest discover -s tests -p 'test_phase5_*.py' -v`: 13 tests
  passed. The suite covers all five proposed outcomes, conflict precedence,
  qualified-review-only functional equivalence, score separation, and readable
  CLI JSON with original IDs/text.
- `py -3.13 verify_raw_data.py`: all three protected raw hashes passed.
  `git diff --check` passed. P5-03 complete; no blocker. Next: P5-04 full evidence
  pack, diagnostics and final verification.

## 2026-09-30 Iteration 4

- Re-read iteration 3 and added `phase5_build.py`, a no-overwrite generator from
  the frozen Phase 3 records and Phase 4 candidate pack. Both input hashes are
  checked before/after generation. Added compact report/examples/review notes in
  `reports/phase5/`; the authoritative reproducible pack is
  `output/phase5-v0.1/`.
- Reconciled all 9,245 Phase 4 queries and 89,381 retrieved directed pairs; 9,155
  queries had candidates. Generation took 12.595633 seconds. Rule outputs were:
  4,476 exact duplicate, 3,352 near duplicate, 10,529 possible functional
  equivalent, 6,804 conflict and 64,220 no match. These are rule counts, not
  accuracy metrics. No merge or common-code assignment occurred.
- All 7 named real/hard checks passed: identical separate rows, matching-spec pipe
  wording variants, 15/25 mm pipes, 150/240 mm2 cables, different valve pressure
  bases, missing pump specifications, and unrelated families. A deliberate test
  also covers unrelated items that share the generic word `industrial`.
- `py -3.13 -m unittest discover -s tests -p 'test_phase5_*.py' -v`: 16 tests
  passed. `py -3.13 -m unittest discover -s tests -v`: 75 tests passed in
  74.018 seconds before the final additional generic-word test; that added focused
  test also passed. The pack manifest, no-overwrite guard and 89,381-line
  reconciliation passed.
- `py -3.13 verify_raw_data.py`: all three protected raw hashes passed.
  `git diff --check` passed apart from Git's informational LF/CRLF warning for
  `.gitignore`. P5-04 complete; no blocker. Phase 5 is ready to close. Phase 6
  has not started.
