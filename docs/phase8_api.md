# Phase 8 API handoff for Phase 9

Base paths use `/api/v1/workspaces/{workspace_id}`. Public reads work only for a
workspace explicitly created with `public_read=true`. Every write requires a
verified owner Bearer token and `Idempotency-Key`; the actor is the verified token
subject.

Core endpoints:

- `GET /health`, `GET /ready`
- `POST /api/v1/workspaces/{workspace_id}`
- `GET /materials`, `GET /materials/search`
- `GET /materials/{source_id}/candidates`
- `GET /pairs/{left_id}/{right_id}`
- `GET /registry`, `GET /registry/{proposed_code}`
- `GET /mappings`, `GET /decisions`, `GET /functional-relationships`
- `POST /decisions`
- `POST /decisions/{decision_id}/reconsider`
- `GET /migration-preview`, `GET /dashboard`
- `GET /exports/{dataset}.{format}` for source mappings, unresolved records,
  conflicts, registry, decisions and functional relationships.

All list and export endpoints are paginated. Candidate results explicitly identify
bounded lexical retrieval and never declare identity. Pair evidence keeps retrieval
ranking separate from proposed outcomes. Registry entries return structured
evidence plus `readable_description`.

The generated machine-readable contract is `reports/phase8/openapi.json`.
