# Phase 4 checkpoint

Phase 4 is closed. Its authoritative output is `output/phase4-v0.1/` and its
authoritative input is `output/phase3-v0.1/material_attributes.jsonl`.

Verification recorded at closure:

- 9,245 query records reconciled; 9,155 returned at least one bounded candidate.
- Top-k was 10. Candidate pools were capped at 500 and no all-pairs matrix or
  scan was used.
- 1,748,329 fuzzy comparisons were made versus 85,460,780 possible directed
  pairs. All queries completed in 30.637253 seconds (301.757 queries/second).
- The five predeclared diagnostic examples were retrieved. This is example
  coverage, not accuracy or recall; no human-labeled retrieval benchmark exists.
- The final repository regression passed 60 tests and all three raw-file hashes.

Limitations remain: lexical caps can miss candidates without useful shared text;
scores are ranking signals rather than probabilities; public descriptions are
surrogate procurement text; and Phase 4 neither decides identity/equivalence nor
rejects technical conflicts. Semantic retrieval was not added because it showed
no benefit on the predeclared non-gold examples.
