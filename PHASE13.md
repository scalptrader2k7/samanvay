# Phase 13 end-to-end validation and submission

The master plan is authoritative. This phase packages and proves the completed system; it does not add product behavior or begin another phase.

| Task | Status | Deliverable | Acceptance check |
|---|---|---|---|
| P13-01 | Complete | Master-plan, checkpoint, repository-state and claim audit. | Claims and known external/repository limitations are identified before packaging. |
| P13-02 | Complete | Deterministic local demo runner and focused test. | Real input reaches adaptation, retrieval, evidence, review, registry, audit, dashboard and export without changing source data. |
| P13-03 | Complete | Claim/evidence matrix and factual documentation review. | Every major claim has a repository artifact or an explicit pending/unsupported status. |
| P13-04 | Complete | Setup, local fallback and judge-facing demo guides. | A teammate has exact install, seed, start, authentication, browser and fallback commands. |
| P13-05 | Complete | Presentation outline and actual-component diagrams. | All numbers and components link to verified evidence; no nonexistent integrations appear. |
| P13-06 | Complete | Fresh-copy reproduction and final browser replay. | A clean copied working tree completes setup and core workflow; managed credentials remain explicitly pending. |
| P13-07 | Complete | Full validation, evidence pack, checkpoint and cleanup. | Tests, compilation, JS, OpenAPI, hashes and diff checks pass; final claims reconcile with evidence. |

## Known acceptance constraint

The current working tree contains substantial untracked Phase 5â€“12 implementation and evidence. A fresh Git checkout cannot contain those files until the completed work is committed. Phase 13 will verify a clean filesystem copy of the current implementation and record the Git-checkout condition separately.

Final acceptance discovered and fixed one checkout-only dependency: missing ignored Phase 3 output is now rebuilt from committed candidate data. The added test brings the final suite to 128 passing tests.
