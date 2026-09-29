# Phase 2 Common input format and readiness

Phase 1A-1C is complete; human review remains pending. Phase 2 accepts different
source columns into a common, traceable record format and reports missing data.
The current public files are procurement-text surrogates, not CPSE material masters.

## Bounded Ralph loop

At the start of each iteration, read this file, [progress](docs/phase2_progress.md),
[the input contract](docs/common_input_format.md), repository instructions and the
relevant code. Select one small unfinished task. Implement it, run its checks,
record results and the next task before the next iteration. The current limit is
**one task per iteration**, with up to three iterations authorized for P2-04 through
P2-06; stop at Phase 2 completion and do not begin Phase 3. Split a task further before starting if it cannot fit a bounded iteration.
Stop and record a blocker when missing data or a user decision prevents completion.

Preserve raw bytes, original identifiers, descriptions and reviewer work. Do not
invent material codes, human labels, specifications or accuracy claims. Do not
re-download data or rerun generators into existing reports as part of ingestion.
Frontend work belongs to Phase 9. The user will supply context/frontend plugin or
skill names; read their instructions when supplied and relevant, without guessing
which installed plugin they mean.

## Tasks and acceptance checks

| Task | Status | Small deliverable | Check before marking complete |
|---|---|---|---|
| P2-01 | Complete | Document v0.1 common record contract, current column mappings and missing-field policy. | Inspect all CSV headers; reconcile raw/candidate row counts and field coverage; check candidate IDs against the corpus; verify raw hashes and unchanged tracked data. |
| P2-02 | Complete | Implement a read-only CSV loader for the raw corpus using the contract. | Load 21,513 records; preserve every source cell and ID; distinguish blank/unmapped fields; handle quoted multiline text, literal NA and leading zeros; reject duplicate headers and malformed rows without modifying input. |
| P2-03 | Complete | Add explicit NTPC and IOCL CSV mapping profiles. | Load 486 and 1,224 records respectively; retain original locator components; label organization constants as mapping metadata; report absent legacy codes; never deduplicate across files. |
| P2-04 | Complete | Add a configurable CSV mapping and candidate-file profile. | Renamed columns work through an explicit mapping; invalid/ambiguous mappings fail clearly; 9,245 candidate IDs trace to the corpus; heuristic flags stay separate from source specifications and human labels. |
| P2-05 | Complete | Add a read-only XLSX adapter with explicit sheet/header selection. | CSV/XLSX versions of the same real sample yield equivalent values; text IDs retain leading zeros; formula/numeric-ID ambiguity is reported rather than silently repaired; input bytes stay unchanged. |
| P2-06 | Complete | Emit readiness reports and traceable sample upload files in a new output directory. | Counts reconcile per input; missing codes/specifications/transaction history are explicit; samples link to real source rows; existing output is never overwritten; raw hashes and regression checks pass. |

The Phase 2 exit check is a reproducible CSV/XLSX load with source mappings,
validation report and sample files. A loaded row is not a verified material or a
match. Missing sponsor data limits claims, but does not block surrogate ingestion.
Normalization, attribute extraction, matching, code assignment and UI are later phases.

All Phase 2 tasks and exit checks passed on 2026-09-27. See
[usage and limitations](docs/phase2_usage.md), [per-input evidence](reports/phase2/summary.json)
and the iteration log. XLSX currently accepts text/blank cells and rejects typed
cells explicitly; sponsor codes, human validation and transactions remain absent.
Phase 2 is ready to close within this documented scope. Stop here; no Phase 3 work.
