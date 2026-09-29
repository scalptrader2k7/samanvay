# Phase 3 derivation contract v0.1

Each output retains the complete Phase 2 record plus:

- `normalization_version`: `description-normalization-v0.1`.
- `description_normalized`: Unicode NFKC; normalized line breaks; collapsed
  whitespace; spacing standardized around commas/colons and `x` between numeric
  dimensions; case preserved. No abbreviation expansion, spelling repair, unit
  conversion, punctuation deletion or inferred wording.
- `family`: one of `pipe`, `valve`, `cable`, `pump`, or null. A family is emitted
  only for an explicit whole-word term or documented abbreviation. Multiple
  distinct family signals yield null plus `ambiguous_family`; plural/spelling
  variants map to the same family but retain their exact evidence.
- `attributes`: keys `size_dimension`, `material_grade`, `standard`, `pressure`,
  `voltage`, `model_part`. Each is an ordered list; no key is filled with a guessed
  value. Multiple supported values remain separate rather than being reconciled.
- `derivation_issues`: conservative warnings such as ambiguous family.

Every family/attribute evidence object records `value_raw` (the exact substring),
`value_normalized` (a display/search form, never source truth), zero-based
`start`/`end` offsets into `description_original`, and `rule_id`. The invariant is
`description_original[start:end] == value_raw`. Attribute evidence may overlap
(for example `API 6D` is a standard inside a valve description). Exact duplicate
evidence from multiple rules is deduplicated; source records never are.

Rules are deliberately narrow:

- size/dimension: explicit number plus `mm`, `mm2`, `sq mm`, inch mark/word,
  `NB`, `DN`, or explicit numeric `x` dimensions. Quantities in metres are not
  treated as item size.
- material/grade: explicit controlled tokens seen in the corpus such as `SS304`,
  `TP304L`, `FE410`, `A312-TP304L`, `CS`, `GLV`, or explicit `grade ...`.
- standard: designation plus identifier, such as `API 610`, `API 6D`, `ASTM A312`,
  `IS1239-1`, `ASME B16.5`, `IEC 60502`. Bare `API`, `IS`, or manufacturer names
  are not values.
- pressure: explicit `class`, `PN`, `bar`, `psi`, or pressure-rating expression.
  Pipe schedule is a dimension/specification and is captured under size/dimension,
  not pressure.
- voltage: explicit numeric `V`/`kV`. `kW`, `kVA`, `HP`, amperes and Hz are not
  voltage and remain unextracted in v0.1.
- model/part: a value following an explicit `model`, `part no`, `p/n` or `PN`
  label. `PN` followed only by a small pressure-class number is treated as pressure,
  not a part number. Manufacturer names alone are not model values.

No attribute is called correct or complete without human validation. Conflicting
values are evidence for later comparison; Phase 3 makes no match/no-match decision.
