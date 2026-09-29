# Phase 5 named rule-output examples

These are traceable rule checks, not accuracy or engineering-validation claims.

## identical descriptions from separate rows

- Left: `M000114` ? Centrifugal Pump
- Right: `M008245` ? Centrifugal Pump
- Proposed outcome: `exact_duplicate` (expected `exact_duplicate`; check passed)
- Explanation: The normalized descriptions are identical and no supported critical conflict was found.
- Review required: `true`; identity merge blocked: `false`
- Reason codes: `text.exact_normalized_description`

## minor wording/format changes with matching specifications

- Left: `M000753` ? , PIPE ASTM A312,9.53MM,141.3MM,125NB ,
- Right: `M000925` ? Pipe Astm A312,9.53mm,141.3mm,125nb
- Proposed outcome: `near_duplicate` (expected `near_duplicate`; check passed)
- Explanation: The wording is a strong variant and supported specifications do not conflict.
- Review required: `true`; identity merge blocked: `false`
- Reason codes: `text.strong_variant`, `family.compatible`, `size_dimension.compatible`, `standard.compatible`

## 15 mm versus 25 mm pipes

- Left: `M000913` ? PIPE SEAMLESS,SS,A312-TP304L,80S,15MM
- Right: `M000927` ? Pipe Seamless,ss,a312-tp304l,80s,25mm
- Proposed outcome: `conflict` (expected `conflict`; check passed)
- Explanation: Supported critical specifications conflict, so an identity merge is blocked.
- Review required: `true`; identity merge blocked: `true`
- Reason codes: `size_dimension.different_linear_dimension_mm`

## 150 mm2 versus 240 mm2 cables

- Left: `M000830` ? CABLE, PWR, 150MM2, 1C, STRANDED, AL, 11KV
- Right: `M000834` ? CABLE,PWR,240MM2,1C,STRANDED,AL,11KV
- Proposed outcome: `conflict` (expected `conflict`; check passed)
- Explanation: Supported critical specifications conflict, so an identity merge is blocked.
- Review required: `true`; identity merge blocked: `true`
- Reason codes: `size_dimension.different_cross_section_area_mm2`

## different valve pressure-rating bases

- Left: `M010407` ? Gate Valve, 2" x 300 Class, API 6D
- Right: `M003626` ? Gate Valve, 2.1/16 inch x 5000 PSI, API 6A
- Proposed outcome: `conflict` (expected `conflict`; check passed)
- Explanation: Supported critical specifications conflict, so an identity merge is blocked.
- Review required: `true`; identity merge blocked: `true`
- Reason codes: `pressure.incompatible_rating_bases`, `standard.different_standard_api`

## same pump family with missing specifications

- Left: `M000041` ? API 610 Centrifugal Pump
- Right: `M000114` ? Centrifugal Pump
- Proposed outcome: `possible_functional_equivalent` (expected `possible_functional_equivalent`; check passed)
- Explanation: The same item family and partial wording support justify qualified review only; engineering equivalence is not established.
- Review required: `true`; identity merge blocked: `true`
- Reason codes: `family.compatible`, `text.partial_support`, `review.qualified_engineer_required`

## unrelated explicit families sharing generic material context

- Left: `M000114` ? Centrifugal Pump
- Right: `M000165` ? Electrical Cables
- Proposed outcome: `no_match` (expected `no_match`; check passed)
- Explanation: The descriptions identify different item families; shared wording cannot support a match.
- Review required: `false`; identity merge blocked: `true`
- Reason codes: `family.different_explicit_family`
