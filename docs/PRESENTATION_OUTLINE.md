# Samanvay SIH presentation outline

Every number below links to local evidence. Avoid adding accuracy, savings, adoption or deployed-scale claims.

## Slide 1 â€” Problem

Material descriptions vary across organizations and source systems. Duplicate-looking wording can conceal critical size, pressure, voltage, grade or standard differences. Teams need traceability and qualified review before shared identity.

Evidence: master plan; `docs/common_input_format.md`.

## Slide 2 â€” Data and provenance

- 23,223 preserved rows across three public source snapshots.
- 9,245 provisional material candidates used for the working demonstration.
- Original IDs, descriptions, raw fields, source hashes and provenance remain intact.
- Public surrogate procurement text is not a genuine cross-CPSE material master.

Evidence: `SOURCES.md`, Phase 1 reports, Phase 13 raw hashes.

## Slide 3 â€” Samanvay approach

Show the end-to-end architecture diagram. Explain source adaptation, conservative extraction, bounded lexical retrieval, pair evidence, reviewer action, prototype registry, governance and exports.

Evidence: `docs/phase13_architecture.md`.

## Slide 4 â€” Matching and safety

Use M000753 â†” M000925 for the near-duplicate pipe example. Use M000830 â†” M000834 for the cable cross-section conflict. Explain unknown values, compatible units and critical-conflict priority.

Evidence: `reports/phase13/pair.json`, `critical_conflict.json`, pair screenshot.

## Slide 5 â€” Human decision and prototype registry

Show approval, stable workspace prototype ID, source mappings and readable/structured evidence. Emphasize that `SMV-P-*` is proposed and workspace-scoped, not official.

Evidence: registry and mapping export; registry screenshot.

## Slide 6 â€” Governance

Show approve â†’ defer â†’ approve history, server-derived actor, reasons, versions and before/after mapping states. Source records remain immutable.

Evidence: audit and mapping history artifacts; governance screenshot.

## Slide 7 â€” Quality dashboard and exports

Show 9,245 loaded, 2 mapped and 9,243 unresolved in the demonstrated current state, plus completeness and explicit unavailable financial metrics. Show CSV, JSON and XLSX export.

Evidence: Phase 13 dashboard JSON and downloaded workbook.

## Slide 8 â€” Integration boundary

Show two different input schemas producing the same matching-core inputs. Explain CSV templates, explicit mapping, missing-value handling, validation and read-only preview. No live SAP or ERP writes.

Evidence: Phase 12 acceptance and integration screenshot.

## Slide 9 â€” Validation

- 128 repository tests in the final run.
- Python compilation, JavaScript syntax and OpenAPI checks passed.
- All protected raw hashes passed.
- Clean filesystem copy installed dependencies and replayed the workflow.
- Full local Edge workflow and export passed.

Evidence: `reports/phase13/final_test_report.md`, reproduction and browser reports.

## Slide 10 â€” Limitations and next deployment step

Human labels and genuine CPSE material-master data are pending. No measured matching accuracy, savings, live ERP integration or public managed deployment is claimed. Next deployment work requires managed PostgreSQL, OIDC and Vercel credentials, followed by access-isolation and persistence validation.

Evidence: claim/evidence matrix and Phase 8 deployment guide.

Fresh-checkout reproducibility also verifies rebuilding the ignored Phase 3 pack from committed candidate data.
