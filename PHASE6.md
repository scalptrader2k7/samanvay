# Phase 6 evaluation preparation and error review

Phase 5 is closed at `docs/phase5_checkpoint.md`; its authoritative pack remains
`output/phase5-v0.1/`. Phase 6 prepares honest human review without creating human
labels or reporting accuracy metrics before review.

Each Ralph iteration completes one task, runs focused checks and updates
`docs/phase6_progress.md`. Stop when the exit checks pass or a decision blocker is
reached. Do not begin Phase 7.

| Task | Status | Deliverable | Acceptance check |
|---|---|---|---|
| P6-01 | Complete | Phase 5 closure plus Phase 6 checklist and evaluation contract. | Contract defines unordered-pair deduplication, sampling coverage, label separation, evidence-basis distinction, partial-label metrics and prohibited claims. |
| P6-02 | Complete | Explicit evidence disposition in current pair results. | Supported incompatibility and insufficient evidence are distinct; insufficient evidence is reviewable; exact text and critical-conflict precedence remain unchanged. |
| P6-03 | Complete | Deterministic review pack of approximately 100 unique unordered pairs. | Exactly 100 unique unordered pairs cover five automated outcomes, organizations/families, missing evidence and critical conflicts; both IDs/provenance remain intact; human fields are blank. |
| P6-04 | Complete | Review guide, sample inspection and error log. | Guide separates automation from judgment; obvious rule risks are logged without invented labels; named safety invariants and evidence traceability checks pass. |
| P6-05 | Complete | Partial-label metrics utility and concise Phase 6 report. | Unlabeled input reports validation pending and no performance metrics; test fixtures verify partial-label denominators; focused tests, raw hashes and pack manifest pass. |

Phase 6 exit means the review process is prepared and reproducible. Validation
remains pending until qualified reviewers supply judgments.

All Phase 6 preparation tasks passed on 2026-09-30. The authoritative review pack
is `output/phase6-v0.1/`; compact tracked materials are in `reports/phase6/`.
Phase 6 is ready to close with validation pending. Phase 7 has not started.
