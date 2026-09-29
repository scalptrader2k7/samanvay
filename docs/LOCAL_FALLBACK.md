# Samanvay local fallback run guide

Use this path when managed Neon, OIDC or Vercel access is unavailable. It demonstrates the complete core workflow honestly with local SQLite and demo authentication.

1. Follow `docs/FINAL_SETUP.md` to install dependencies and seed `public-demo`.
2. Start FastAPI with Uvicorn and open `http://127.0.0.1:8000`.
3. Connect to `public-demo` using the locally configured demo token.
4. Open Materials, search `M000753`, and open its candidates.
5. Select `M000925`. Show the original descriptions, source IDs, `near duplicate` proposal, missing values and field evidence. Explain that the retrieval score is separate from the proposed pair outcome.
6. Enter a reason and approve identity. Explain that this is a demonstration review action, not an evaluation label.
7. Open Registry. Show the newly assigned `SMV-P-*` prototype ID and both source mappings. Never call it an official material code.
8. Open Review and reconsider the current decision to defer, then approve it again with reasons. Open Governance to show the append-only history and current state.
9. Return to Quality dashboard. Show 9,245 loaded records, current mapping state, missing fields and the explicit lack of financial metrics. Download the quality workbook.
10. Open Integration, select the CPSE/SAP-shaped example and validate it. Show that blank codes/specifications remain unknown, the source rows remain visible, and the preview reports no persistence or ERP writes.

If the browser is unavailable, run:

```powershell
python phase13_demo.py --output-dir reports/fallback-run
```

Inspect `summary.json`, `pair.json`, `critical_conflict.json`, `registry_current.json`, `audit_events.json`, `quality_dashboard.json`, the exports, and the integration preview files. This fallback proves the local workflow. It does not prove managed deployment, live SAP access, ERP writeback, cross-CPSE accuracy or financial impact.

The local fallback does not require the ignored Phase 3 output pack; seeding reproduces enriched records from committed candidate data when needed.
