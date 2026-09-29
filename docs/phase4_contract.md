# Phase 4 retrieval contract v0.1

Input records come from the frozen Phase 3 pack. Each result contains query and
candidate `source_record_id`, source organization, rank, retrieval score and a
list of retrieval reasons. It also retains the candidate's original description.
The output status is always `candidate_only`.

Retrieval layers:

1. Exact normalized description index.
2. Exact nonblank source identifier components, keyed by identifier field and
   value. A source record ID is never treated as a shared material code.
3. Inverted index over useful normalized tokens. Common stopwords and one-character
   alphabetic tokens are excluded; numeric/technical tokens remain.
4. Fuzzy character-trigram Dice score only inside the bounded candidate pool
   built by layers 1-3. Trigrams are precomputed per record; no external model or
   all-pairs fuzzy matrix is built.

The index stores postings, never every possible pair. At query time it selects a
maximum of eight rare useful tokens, caps each posting at 250 records, and trims
the union to at most 500 candidates by exact/shared-token evidence before fuzzy
scoring. The query itself is excluded. `top_k` must be 1-50 and defaults to 10.

Reasons may include exact normalized text, shared identifier, shared useful tokens,
and fuzzy normalized-text similarity. Scores rank proposals only; they are not
probabilities or match confidence. Attribute values are displayed for downstream
review but do not reject candidates in Phase 4. Different sizes/ratings can appear
as useful hard-negative proposals; Phase 5 owns comparison and conflict decisions.

Diagnostics record pool size, postings visited, comparisons performed and elapsed
time. Example coverage names the query/expected candidate pairs in advance and
reports whether the target appeared in top-k. It is not accuracy, recall or a gold
benchmark. Semantic retrieval remains disabled unless a documented difficult-case
suite gains targets that lexical retrieval misses without unacceptable noise/runtime.
