# Phase 11 metric and export contract

All authoritative counts come from the opened workspace database. The frontend
renders returned values and definitions; it does not recompute core metrics.

- Loaded records are rows in `source_records`.
- Mapped/unresolved are current active registry membership states, one per source.
- Pending reviews are current, non-superseded decisions whose action is `defer`.
- Approved/rejected/deferred counts are current decisions, not model accuracy.
- Reconsidered count is the number of appended decisions with a supersession link.
- Candidate retrieval results are generated on demand and are not persisted. No
  workspace-wide candidate count or retrieval coverage is claimed.
- Candidate-cluster equivalents are persisted active registry groups and active
  functional-equivalence relationships, reported separately.
- Conflict rate evaluates the unique unordered source pairs represented by current
  decisions using the existing pair-evidence rules. Numerator is outcome `conflict`;
  denominator is every evaluated current-decision pair. It is a rule-output rate,
  not accuracy, precision, recall or engineering validation.
- Completeness examines persisted record fields only. Present means a nonblank
  stored scalar or at least one supported structured family/attribute. Missing means
  the scalar/key is absent or blank. Unknown applies when the structured attribute
  container exists but contains no supported family or attribute value.
- Mapping coverage is current mapped sources divided by loaded sources. Historical
  mapped-to-unresolved transitions are reported separately and never mixed into the
  current mapped count.

Current registry and mapping exports remain separate from audit/decision/mapping
history exports. Output ordering is stable. The Excel quality pack contains current
registry, current mappings, dashboard summary, completeness and a scope manifest;
its ZIP metadata is normalized so unchanged workspace state produces identical
bytes. No source record is modified during calculation or export.

No savings, ROI, cost reduction, obsolete-stock value or financial impact metric is
defined because persisted transaction, price and quantity evidence is insufficient.
