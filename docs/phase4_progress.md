# Phase 4 progress

Read this log, `PHASE4.md`, the Phase 3 checkpoint/contract and current code before
each iteration. Complete one task per iteration. Do not begin Phase 5.

## 2026-09-27 Iteration 1

- Closed Phase 3 in `docs/phase3_checkpoint.md`; authoritative pack is
  `output/phase3-v0.1/`. The older ignored pack remains untouched as requested.
- Read the supplied master plan, Phase 3 contract/output/report and current code.
  Inspected real exact repeats, including cross-organization `Centrifugal Pump`,
  `Electrical Cables`, and other descriptions.
- Added the Phase 4 checklist and retrieval contract. The design uses postings and
  bounded query pools, not all-pairs comparison; scores are ranking signals only.
- P4-01 acceptance checks pass. No blocker. Next: P4-02 exact/token indexes.

## 2026-09-27 Iteration 2

- Re-read iteration 1 and added `CandidateIndex` with normalized-text, exact
  provenance-identifier and useful-token postings. Source `corpus_id` remains the
  record identity and is not used as a shared material key.
- Query pools use at most eight rare tokens, skip postings above 250 and cap at
  500 candidates. No pair matrix exists; self is excluded and explanations retain
  exact identifier fields/values and shared tokens.
- `py -3.13 -m unittest discover -s tests -p test_phase4_index.py -v`: 5 tests
  passed. Cross-organization exact examples `Centrifugal Pump` and `Electrical
  Cables` were found; pool bounds and no-all-pairs diagnostics passed.
- P4-02 complete; no blocker. Next: P4-03 bounded fuzzy top-k/explanations.

## 2026-09-27 Iteration 3

- Re-read iteration 2 and added bounded `SequenceMatcher` reranking only within
  the indexed pool. Results are deterministic, validate `top_k` 1-50 and retain
  reasons, candidate organization/original text and Phase 3 attribute evidence.
- Scores are capped ranking signals; exact normalized text ranks at 1.0. Every
  output is `candidate_only` and has no decision or common code.
- `py -3.13 -m unittest discover -s tests -p test_phase4_retrieval.py -v`: 4 tests
  passed. Exact cross-organization pump repeat, near pipe formatting variant and
  a different-size cable proposal were retrieved; top-k bounds passed.
- P4-03 complete; no blocker. Next: P4-04 full pack/diagnostics/semantic decision.

## 2026-09-27 Iteration 4

- Re-read iteration 3 and added a no-overwrite all-record retrieval pack. The
  first full test using Python `SequenceMatcher` exceeded two minutes and was
  interrupted; fuzzy scoring was replaced with precomputed character-trigram Dice.
  The same bounded behavior/examples passed in 38.972 seconds including pack I/O.
- Generated authoritative `output/phase4-v0.1/` and retained compact report,
  diagnostic examples and review notes in `reports/phase4/`.
- Reconciled all 9,245 query IDs; 9,155 queries returned at least one candidate.
  Top-k is 10 for the full pack. Index build took 0.490502 s; all queries took
  30.637253 s (301.757 queries/s). Mean measured query latency was 3.049 ms.
- Bounded work: maximum pool/comparisons 500; mean pool 189.111, p95 474;
  1,748,329 fuzzy comparisons versus 85,460,780 possible directed pairs. No
  all-pairs matrix or scan was used.
- Predeclared diagnostic example coverage was 5/5 (not accuracy/recall): exact
  cross-organization pump/cable rank 1, near pipe rank 1, different cable size
  rank 4/30, different valve pressure rank 18/50. All remain `candidate_only`.
- Semantic retrieval was not added: lexical retrieval found every named target,
  so no incremental benefit was demonstrated on this non-gold suite.
- Focused `py -3.13 -m unittest discover -s tests -p 'test_phase4_*.py' -v`:
  10 tests passed. Final regression/hash checks are recorded below.
- P4-04 implementation complete; no blocker. Phase 5 not started.

- Final regression: `py -3.13 -m unittest discover -s tests -v`: **60 tests
  passed** in 61.632 s, including all prior phase tests and the full 9,245-query
  pack check. `python verify_raw_data.py`: all three hashes passed. Protected raw
  data, Phase 1 review files and earlier reports remain unchanged. `git diff
  --check` passed. Phase 4 is ready to close; Phase 5 remains unstarted.
