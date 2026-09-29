# Phase 10 governance and audit implementation report

## Existing behavior retained

Phase 7-9 already stored immutable decision inserts with actor, reason, time and a
supersession link; reconsideration revoked registry membership consistently; Phase
8 added owner-only writes, server-derived OIDC/demo subjects, idempotency, rollback,
workspace isolation and restart persistence. Phase 10 reuses those transactions.

## Storage and governance workflow

The existing RegistryStore schema now includes append-only `audit_events` and
`mapping_change_history`. Approval, rejection and deferral append a decision and
audit event. Reconsideration captures the prior state, applies the existing registry
or functional-relationship consequence, appends a superseding decision, then
records the resulting state and any per-source mapping transitions. One transaction
commits or rolls back the full operation.

Audit records include workspace, event/action/relationship type, affected source
IDs, authenticated actor, timestamp, reason, input SHA/mapping/schema versions,
normalization/parser/pair/registry versions, decision link and before/after state.
No model version is claimed; it is explicitly null. Source records, decisions and
audit rows are protected against update/delete.

## APIs and roles

Added:

- `GET /api/v1/workspaces/{workspace}/governance/access`
- `GET /api/v1/workspaces/{workspace}/audit-events`
- `GET /api/v1/workspaces/{workspace}/mapping-history`
- Exact `source_id` filtering on decision history
- Real audit and mapping-change counts on the dashboard

All history endpoints are paginated and workspace isolated. Public visitors receive
view-only capability; the verified owner receives review and governance capability.
Decision/reconsideration writes still derive actor identity server-side and require
ownership and idempotency. Stale superseded decisions cannot be reconsidered.

## Frontend

The Reviewer Interface adds a Governance view with role/capability status, source
filtering, decision/audit timeline, reviewer identity, timestamp, reason, transition
display, mapping history and expandable input/rule evidence. Decision history only
offers reconsideration for the current row and an authorized owner.

## Verification

Headless Chrome completed material M004773 → candidate M004774 → exact-duplicate
evidence → approval → visible audit event → reconsideration to reject → visible
two-event history and unresolved mappings. The evidence image is
`governance_workflow.png` in this directory. Restart verification confirmed the
current reject state and persistent history while the source snapshot digest stayed
unchanged.

The Phase 5-10 dependency suite passed 53 tests. A final 21-test Phase 7-10 focused
run passed after adding the stale-override guard. JavaScript syntax, Python
compilation, OpenAPI generation and all three protected raw-file hashes passed.

## Deferred

No audit records were fabricated for actions predating Phase 10. Delegated reviewer
administration is deferred; the existing owner/public model is sufficient for the
current architecture. Live managed-storage and OIDC verification still require the
external account setup recorded in Phase 8. Phase 11 has not started.
