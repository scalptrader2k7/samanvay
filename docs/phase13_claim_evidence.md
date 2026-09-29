# Samanvay claim and evidence matrix

Status terms: **verified locally** means reproduced in this checkout with local SQLite and demo authentication. **Implemented, externally pending** means code and contracts exist but managed credentials were unavailable. **Unsupported** means the project deliberately makes no such claim.

| Claim | Evidence | Status | Scope and limitation |
|---|---|---|---|
| Raw public source bytes are preserved and traceable. | `SOURCES.md`; `verify_raw_data.py`; `reports/phase13/summary.json` | Verified locally | Three checked source CSVs; public surrogate data, not genuine CPSE material masters. |
| 9,245 provisional candidate records load without dropped source IDs. | `reports/phase13/summary.json`; loader tests | Verified locally | Candidate selection is rule-derived, not a human label. |
| Different source schemas feed the same matching core. | `tests/test_phase12_adapter.py`; `reports/phase12/acceptance.json`; Phase 13 integration previews | Verified locally | Two demonstrated CSV schemas; sponsor mappings still require source-owner review. |
| Original descriptions and source IDs remain intact while derived fields are separate. | Phase 2/3 contracts; `pair.json`; source loader and Phase 3 tests | Verified locally | Extraction coverage is a rule output, not accuracy. |
| Candidate retrieval is bounded lexical retrieval rather than an all-pairs scan. | `candidate_retrieval.py`; Phase 4 tests/report; `candidates.json` | Verified locally | No labeled retrieval benchmark; no recall or accuracy claim. |
| Pair evidence separates retrieval rank from proposed outcome and blocks supported critical conflicts. | `pair_evidence.py`; Phase 5 tests; `critical_conflict.json` | Verified locally | Engineering equivalence is never established automatically. |
| Missing evidence stays unknown. | Phase 3/5 tests and contracts; browser pair screenshot | Verified locally | Unknown does not mean compatible. |
| Reviewer approval creates a stable opaque prototype code and mappings. | Phase 7 tests; `registry_current.json`; `source_mappings.csv` | Verified locally | `SMV-P-*` is a proposed workspace prototype ID, never an official national code. Codes are stable in their workspace; separate workspaces may issue different opaque IDs. |
| Functional equivalence is separate from identity membership. | Phase 7/8 tests and storage contract | Verified locally | It remains a qualified-review suggestion. |
| Decisions and reconsiderations preserve append-only audit and mapping history. | Phase 10 tests; `audit_events.json`; `mapping_history.json`; governance screenshot | Verified locally | Two-role prototype: public viewer and workspace owner; enterprise delegated IAM is pending. |
| Dashboard and exports reconcile with persisted current state. | Phase 11 tests; `quality_dashboard.json`; generated CSV/JSON/XLSX exports | Verified locally | Candidate proposals are not globally persisted, so that count remains unavailable. |
| CPSE/SAP integration is ready at a read-only contract boundary. | `contracts/integration/`; Phase 12 API/tests; integration screenshot | Verified locally | No live SAP connection, synchronization, schema discovery, or ERP writeback. |
| Local restart-persistent storage and managed PostgreSQL/OIDC paths exist. | `service_storage.py`; `db/postgres_schema.sql`; Phase 8 tests/docs | Local SQLite verified; managed path externally pending | Neon/OIDC/Vercel accounts and credentials were unavailable. No tested public URL. |
| The system provides measured cross-CPSE matching accuracy. | Phase 6 unlabeled sample and metrics report | Unsupported | Human validation is pending; no accuracy, precision, recall, or false-merge rate is claimed. |
| Samanvay proves savings, ROI, obsolescence, or procurement impact. | Dashboard financial limitation; Phase 2 reports | Unsupported | Transaction, stock, issue, lifecycle, price and audited savings data are absent. |
| The application automatically merges or writes back to ERP. | API description, decision flow and Phase 12 boundary | Unsupported | Every identity membership requires an explicit review action; ERP writes do not exist. |
| A clean filesystem copy installs and replays the demo. | `reports/phase13/reproducibility.md`; copied-run `summary.json` result | Verified locally | Current working-tree copy passed. A fresh Git checkout remains conditional on committing currently untracked Phase 5–13 files. |
| Complete browser workflow works without CLI interaction after startup. | `reports/phase13/browser_replay.json`; five screenshots | Verified locally | Local Edge, SQLite and demo auth; server setup still uses terminal commands. |

Fresh-checkout seeding is verified through a fallback test that rebuilds the ignored Phase 3 pack from committed candidate data.
