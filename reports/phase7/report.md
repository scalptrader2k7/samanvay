# Phase 7 proposed registry report

Phase 7 is complete as a local prototype. It does not create official CPSE material
codes and Phase 8 has not started.

The registry stores opaque `SMV-P-XXXXXXXXXXXX` proposed codes in SQLite. Codes
survive restart and repeated/reordered approvals. Membership is created only by an
explicit identity approval with actor and reason. Every member pair is checked;
critical conflicts, supported family incompatibility and functional-equivalence-
only evidence block identity grouping transactionally.

Standard descriptions contain only family/attribute values supported identically
by all members. Other fields remain `UNKNOWN`, while every observed value keeps its
source ID and exact text span. Mappings retain organization, internal source row
ID, original description and all source identifiers. Internal `corpus_id` and
tender identifiers are not presented as official material codes.

The demonstration imports 9,245 source records and 10 Phase 6 warnings. Six
demonstration decisions exercise stable repeated identity approval, rejection,
deferral, reconsideration and a separate functional relationship. They create zero
evaluation labels. One two-record prototype is active; 9,243 records remain
unresolved. None of the current records supplies a field explicitly identified as
a genuine CPSE/SAP/legacy material code, so all 9,245 are reported as missing one.

Migration exports include registry entries, original-to-proposed mappings,
unresolved records, warnings/rejections, functional relationships, decisions and a
manifest in CSV/JSON where applicable.

Limitations: human evaluation remains pending; Phase 6 warnings are advisory;
standard-description completeness depends on conservative Phase 3 extraction; and
the demonstration decisions are workflow fixtures rather than production review.
SQLite is suitable for local development and restart tests only. Phase 8 must use
durable mounted storage or a managed transactional database and must not rely on a
deployed server's ephemeral filesystem.
