# Phase 3 real description review

These are deterministic rule checks on public surrogate text. They are not human
ground truth or an accuracy sample. Values below retain exact source spans in
`examples.json` and the full records under ignored `output/phase3/`.

| ID | Family | Original evidence | Derived fields |
|---|---|---|---|
| M000753 | pipe | `PIPE ASTM A312,9.53MM,141.3MM,125NB` | standard `ASTM A312`; sizes `9.53MM`, `141.3MM`, `125NB` |
| M000913 | pipe | `PIPE SEAMLESS,SS,A312-TP304L,80S,15MM` | grade `A312-TP304L`/`TP304L`; schedule `80S`; size `15MM` |
| M010407 | valve | `Gate Valve, 2" x 300 Class, API 6D` | size `2"`; pressure `300 Class`; standard `API 6D` |
| M003626 | valve | `Gate Valve, 2.1/16 inch x 5000 PSI, API 6A` | source spelling retained; size `2.1/16 inch`; pressure `5000 PSI`; standard `API 6A` |
| M000830 | cable | `CABLE, PWR, 150MM2, 1C, STRANDED, AL, 11KV` | size `150MM2`; voltage `11KV` |
| M000921 | pump | `PUMP/ FAN/ COMPRESSOR UPTO 6.6KV 750KW` | voltage `6.6KV`; `750KW` intentionally not called voltage |
| M000041 | pump | `API 610 Centrifugal Pump` | standard `API 610`; no unsupported model |
| M015553 | pump | `... PUMP MODEL NAT 12 P 160` | explicit model evidence `MODEL NAT 12 P 160` |
| M000114 | pump | `Centrifugal Pump` | family only; all technical values unknown |
| M000342 | unknown | contains pumps, valves and tubing | ambiguous family; no forced family or attributes |

## Critical differences for later matching

Phase 3 does not score or match records. These checks ensure a later exact-identity
matcher has preserved evidence that should block a merge unless qualified review
says otherwise:

- M010407 (`300 Class`, API 6D) and M003626 (`5000 PSI`, API 6A) are both gate
  valves but carry different pressure/standard evidence.
- M000913 (`15MM`) and M000927 (`25mm`) are similar pipe descriptions with a size
  conflict.
- M000830 (`150MM2`) and M000834 (`240MM2`) are otherwise similar 11KV cables with
  a conductor-size conflict.

These are engineering conflict examples from source text, not human-labeled pair
decisions. Phase 4 must use them as candidate-retrieval safeguards; Phase 5 owns
formal conflict decisions under the master plan.
