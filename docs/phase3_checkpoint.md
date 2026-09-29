# Phase 3 final checkpoint

Status: **Closed on 2026-09-27** within the derivation contract v0.1.

The authoritative full output pack is `output/phase3-v0.1/`. The older ignored
`output/phase3/` pack is superseded and intentionally left alone. Compact retained
evidence is in `reports/phase3/`.

- Verification: 50 automated tests passed; 9,245 input/output records and unique
  source IDs reconciled; zero rows dropped; original decoded descriptions and all
  evidence spans were preserved; all three raw hashes passed.
- Reviewed pipe, valve, cable and pump examples, explicit unknown/ambiguous cases,
  and technical conflicts that later phases must retain rather than collapse.
- Coverage is rule output, not accuracy: size 1,539 records, material/grade 166,
  standard 378, pressure 206, voltage 283, explicit model/part 63.
- Limitations: no human attribute gold set, unit conversion, abbreviation expansion,
  semantic interpretation or pair decision. Derived values are evidence-linked
  proposals and do not alter source master data.

This checkpoint freezes `description-normalization-v0.1` and
`technical-attributes-v0.1` as the Phase 4 input boundary.
