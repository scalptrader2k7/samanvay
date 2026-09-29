# Phase 4 retrieval examples

These five cases were declared before the full retrieval run. “Found” means the
named target appeared within the stated top-k, not that it is an identity match.
No pair has a human label.

| Case | Query | Target | Rank | Limit | Purpose |
|---|---|---|---:|---:|---|
| Exact cross-organization pump | M000114 | M008245 | 1 | 10 | Same normalized `Centrifugal Pump` text across IOCL and Oil India. |
| Exact cross-organization cable | M000165 | M017540 | 1 | 10 | Same normalized `Electrical Cables` text across IOCL and Oil India. |
| Near-format pipe | M000753 | M000925 | 1 | 20 | Punctuation/case variant with ASTM A312 and the same explicit dimensions. |
| Different cable size proposal | M000830 | M000834 | 4 | 30 | Similar 11KV cable wording but `150MM2` versus `240MM2`; retrieval must propose, not merge. |
| Different valve pressure proposal | M010407 | M003626 | 18 | 50 | Both gate valves, but `300 Class`/API 6D versus `5000 PSI`/API 6A; intended downstream conflict case. |

Lexical retrieval found 5/5 named targets. This small, purpose-built suite checks
mechanics and safety cases; it is not recall, accuracy or evidence of CPSE matching
quality. Semantic retrieval was not added because it showed no demonstrated
incremental need on this suite. A human-reviewed retrieval set in Phase 6 is needed
before comparing lexical and semantic methods quantitatively.
