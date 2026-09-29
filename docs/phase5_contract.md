# Phase 5 pair comparison contract v0.1

## Inputs and output boundary

The source records are the frozen Phase 3 records. Pair proposals come from the
frozen Phase 4 candidate pack. Every comparison retains both
`source_record_id` values, organizations and original descriptions. Attribute
evidence remains an exact span of its original description. Repeated source rows
remain distinct comparisons.

The Phase 4 rank, score and reasons are copied under `retrieval` only. They select
and order candidate pairs; they never set or strengthen the Phase 5 outcome.

Every result contains field-by-field comparisons for family, size/dimension,
material grade, standard, pressure, voltage and model/part. A field reports
compatible values, conflicts, unknown sides and values that cannot safely be
compared. Missing values are `unknown`, never agreement. Ambiguous or
non-comparable evidence sets `review_required`.

## Comparable meanings and units

Values are compared only within the same semantic type. Examples include nominal
bore with nominal bore, cable cross-sectional area with cross-sectional area,
pipe/valve inch diameter with inch diameter, voltage with voltage, and pressure
values with the same pressure basis. Voltage uses volts as a canonical unit. PSI
and bar are physically compatible units and may be compared after a documented
conversion. Pressure Class and PSI, or PN and bar, remain different designation
systems; equal-looking numbers are not equality evidence. A diameter is never
compared with length or area.

If both sides carry pressure evidence but only in incompatible designation systems,
the pair receives a safety conflict that blocks identity. The rule does not claim
the numeric ratings are equal or unequal; it says their equivalence is unsupported.
Unparseable or role-ambiguous values remain uncertain and go to review.

Critical fields are size/dimension, pressure, voltage, material grade and standard.
A supported conflicting value in any critical field sets
`identity_merge_blocked: true` before text similarity is considered.

## Proposed outcomes and decision order

The deterministic order is:

1. **Conflict** — a critical comparable value conflicts, or incompatible pressure
   bases prevent a safe identity comparison. This always blocks an identity merge.
2. **No match** — there is an explicit family conflict, or text evidence is too
   weak to support a material relationship. Generic shared words are insufficient.
3. **Exact duplicate** — normalized descriptions are exactly equal, there is no
   conflict, and all compared evidence is compatible. Missing specifications stay
   unknown and require review; the outcome is a proposal, not an automatic merge.
4. **Near duplicate** — text is a strong wording/format variant, at least one
   technical or family value supports it, and all comparable critical evidence is
   compatible. Missing or uncertain critical evidence requires review.
5. **Possible functional equivalent** — explicit family evidence and some useful
   text support a reviewer considering functional interchangeability, but duplicate
   evidence is insufficient. This always requires a qualified reviewer and never
   establishes engineering equivalence or permits an automatic identity merge.

All outcomes are proposals for review. `identity_merge_blocked` is true for
conflict, no match and possible functional equivalent. Even where it is false,
this phase performs no merge and assigns no common material code.

## Traceability and reporting

Readable explanations cite the two source IDs and original text. Supporting
attribute values include exact source spans. Reason codes describe the rule path.
Outcome totals are rule outputs only; without independently reviewed human labels
they are not accuracy, precision, recall or engineering-validation claims.
