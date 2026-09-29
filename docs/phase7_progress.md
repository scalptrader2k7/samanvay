# Phase 7 progress

Read this log, `PHASE7.md`, the Phase 5 contract, Phase 6 checkpoint/error log and
current code before each iteration. Complete one task per iteration. Do not begin
Phase 8.

## 2026-09-30 Iteration 1

- Read the master-plan Phase 7 section, Phase 5 comparison contract, Phase 6 error
  log/checkpoint and current comparison/sampling code. Closed Phase 6 preparation
  with human validation explicitly pending; demonstration actions are separate.
- Added the bounded Phase 7 checklist and registry contract. Proposed codes are
  opaque stored prototype IDs, not official CPSE codes. Internal row locators and
  tender references remain provenance, not material codes.
- Defined explicit transactional decisions, all-member pair checking, separate
  functional relationships, evidence-only standard descriptions, warning carryover,
  migration/export fields and the durable-storage requirement for Phase 8.
- P7-01 documentation checks pass; no blocker. Next: P7-02 transactional SQLite
  repository, stable codes and evidence-built descriptions.

## 2026-09-30 Iteration 2

- Re-read iteration 1 and added `prototype_registry.py` with a transactional,
  foreign-keyed SQLite schema for immutable source snapshots, registry entries,
  memberships, decisions, functional relationships and review warnings.
- Opaque `SMV-P-` prototype codes are randomly allocated once and stored. A
  canonical member fingerprint makes repeated/reordered creation idempotent and
  stable after database restart.
- Standard descriptions emit only a family/attribute value supported identically
  by every member; other fields are explicitly `UNKNOWN`. All observed evidence,
  including unknown/non-common fields, retains source ID, exact substring, offsets
  and rule ID.
- Source identifier dictionaries remain complete. Only explicitly named upstream
  material-code fields qualify as genuine codes; current Phase 3 records have none,
  while `corpus_id` and tender identifiers remain provenance.
- `py -3.13 -m unittest tests.test_phase7_registry -v`: 3 tests passed, covering
  evidence descriptions, stable reload/repeat codes and atomic snapshot rejection.
  Raw hashes passed. P7-02 complete; no blocker. Next: P7-03 decisions, group
  safety, functional separation and warning carryover.

## 2026-09-30 Iteration 3

- Re-read iteration 2 and added transactional `approve`, `reject`, `defer` and
  `reconsider` operations with required actor/reason and immutable decision history.
- Identity approval evaluates every unordered member pair. Critical conflicts,
  supported family incompatibility and functional-equivalence-only evidence block
  the entire transaction. No transitive closure is used. Repeated approvals reuse
  the persisted code; reconsidered approvals revoke membership while preserving
  the original decision and code for audit/reapproval.
- Functional-equivalence approval creates only a separate relationship record and
  no registry entry. Reject/defer actions create history but no membership.
- Phase 6 warning import resolves error-log pair IDs through the frozen review
  sample and attaches warnings to later actions involving either source record.
- `py -3.13 -m unittest tests.test_phase7_registry -v`: 7 tests passed, including
  all-pair conflict rollback, repeat approval, reconsideration history, separate
  functional relationships and membership-free reject/defer. P7-03 complete; no
  blocker. Next: P7-04 CLI, migration preview and exports.

## 2026-09-30 Iteration 4

- Re-read iteration 3 and added `phase7_registry.py` with `init`, `decide`,
  `reconsider`, `show`, `history`, `preview` and `export` commands.
- Migration preview and no-overwrite CSV/JSON exports distinguish active mappings,
  unresolved records, Phase 6 warnings/explicit rejections, functional
  relationships and missing genuine material codes. Original organization, source
  ID, description and identifier dictionaries are retained. Source IDs are
  explicitly marked internal row locators, not official material codes.
- Export manifests hash every artifact. The preview states that SQLite is local
  development storage and Phase 8 requires a durable mounted volume or managed
  transactional database.
- `py -3.13 -m unittest tests.test_phase7_registry -v`: 8 tests passed, including
  migration counts, missing-code handling, CSV/JSON content and overwrite refusal.
  P7-04 complete; no blocker. Next: P7-05 demonstration pack and final verification.

## 2026-09-30 Iteration 5

- Re-read iteration 4 and added a no-overwrite demonstration generator. It imports
  all 9,245 immutable source snapshots and 10 Phase 6 warnings, then exercises
  identity approval/repeat, rejection, deferral, reconsideration and a separate
  functional relationship. Every demonstration decision is marked non-evaluation.
- Generated `output/phase7-v0.1/` and compact reports in `reports/phase7/`.
  The active example has two reviewed pipe records and stable proposed code
  `SMV-P-3AC6BF90CBF0`; 9,243 records remain unresolved. All 9,245 current records
  correctly report a missing genuine material-code field rather than fabricating one.
- Added protection against a source joining two active identity registries. Export
  and demonstration manifests passed, including stable repeat-code and zero
  evaluation-label checks.
- Focused final suite spanning Phase 5 safety semantics, Phase 6 evaluation
  preparation and all Phase 7 code: 33 tests passed in 5.994 seconds. All three
  raw-file hashes passed. `git diff --check` passed apart from Git's informational
  `.gitignore` line-ending warning. No full regression was repeated because the
  focused suite covers every changed dependency and registry path.
- P7-05 complete; no blocker. Phase 7 is complete. Phase 8 has not started.
