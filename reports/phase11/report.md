# Phase 11 quality dashboard and export report

## Existing behavior

Phase 8 already returned persisted source, mapping, registry, relationship,
organization, family and decision counts and provided bounded CSV/JSON datasets.
Phase 10 added current/superseded decisions and separate audit/mapping history.
Phase 11 reuses those storage and access boundaries.

## Dashboard API and calculations

`GET /api/v1/workspaces/{workspace}/quality-dashboard` returns:

- loaded and available eligibility-status counts;
- present/missing/unknown counts for organization, source ID, description, UOM,
  category and structured evidence;
- current approve/reject/defer counts, reconsideration events and unique reviewed
  pairs;
- persisted active registry groups and functional relationships;
- pair-evidence outcome counts and conflict numerator/denominator;
- current mapped/unresolved coverage and historically revoked sources;
- deterministic workspace-state SHA-256 and explicit metric definitions.

Conflict denominator is the set of unique unordered pairs represented by current
persisted decisions. The metric is a rules output, not a labeled quality estimate.
On-demand candidate proposals have no persisted aggregate and are reported as
unavailable. Financial metrics are unsupported because transaction price/quantity
evidence is absent.

## Exports

Current registry and mappings remain available as deterministic, paginated CSV and
JSON. Audit events and mapping history are separate historical datasets. Added
`GET /exports/quality-pack.xlsx`, containing current-state Manifest, Dashboard,
Completeness, Registry and Current Mappings sheets. Its response identifies the
workspace-state hash and `current-state-no-history` scope.

OpenXML cannot store certain control characters found in real source text. Excel
cells preserve them as explicit Unicode escape text such as `\u0000`; raw storage
and CSV/JSON are unchanged. Workbook properties, modified metadata, member ordering
and ZIP timestamps are normalized for deterministic output.

## Frontend and verification

The Quality dashboard shows loaded, mapped, unresolved, pending, registry and
reviewed-pair cards; completeness; review/cluster state; conflict formula and scope;
mapping coverage; current/history export groups; and the financial-data limitation.

On the 9,245-record local workspace, API counts matched direct SQL: 2 mapped, 9,243
unresolved, no deferred current decision, one active registry and 0/2 conflict rule
outputs. Chrome inspected M000753/M000925 registry membership and downloaded an
Excel pack containing all 9,245 current mapping rows. Independent workbook downloads
had identical SHA-256
`4B092BE02BEF6B2C2E423D76976BF3E2F1080E11078F7706D3D720E5D74AB960`.

Sixty Phase 5-11 tests and seven final Phase 11 tests passed. JavaScript syntax,
Python compilation, OpenAPI generation and raw-file hashes passed. Live managed
deployment validation still requires the Phase 8 account setup. Phase 12 has not
started.
