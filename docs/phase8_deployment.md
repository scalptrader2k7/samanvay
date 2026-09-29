# Phase 8 deployment preparation

## Local start

```powershell
py -3.13 -m pip install -r requirements.txt
$env:SAMANVAY_AUTH_MODE = "demo"
$env:SAMANVAY_DEMO_TOKEN = "choose-a-long-local-token"
$env:SAMANVAY_DEMO_SUBJECT = "local-owner"
py -3.13 seed_service.py --workspace local-demo --owner-subject local-owner --public-read
py -3.13 -m uvicorn api_service:app --reload --port 8000
```

Check `http://127.0.0.1:8000/health`, `/ready`, and `/docs`. Writes require
`Authorization: Bearer <local token>` and an `Idempotency-Key` header.

## Free managed setup required from the project owner

1. Create a free Neon PostgreSQL project. Copy its pooled connection string into
   Vercel as `DATABASE_URL`. Do not commit it.
2. Create a free managed OIDC application (for example Clerk or Auth0). Configure
   an API audience, then add `OIDC_ISSUER`, `OIDC_AUDIENCE`, and `OIDC_JWKS_URL` to
   Vercel. The token's verified `sub` claim becomes the workspace owner/actor.
3. In Vercel Hobby, import this repository with the project root set to `samanvay`.
   Add `SAMANVAY_STORAGE_BACKEND=postgres` and `SAMANVAY_AUTH_MODE=oidc`. Never set
   demo-token variables in Vercel.
4. Deploy once so the PostgreSQL workspace schema is created. From a trusted local
   shell with the same `DATABASE_URL`, seed the isolated demonstration workspace:

```powershell
$env:SAMANVAY_STORAGE_BACKEND = "postgres"
$env:DATABASE_URL = "<Neon pooled URL>"
py -3.13 seed_service.py --backend postgres --workspace public-demo `
  --owner-subject "<exact managed-auth sub>" --public-read
```

5. Redeploy or call `/ready`. Verify public reads, authenticated owner writes,
   cross-owner 403 responses, decision persistence after another deployment, and
   CSV/JSON export.

The PostgreSQL `bytea` workspace image is the durable copy. Vercel's filesystem is
never used to retain decisions. This bounded design reuses tested SQLite
transactions; a later scale phase should move frequently updated tables to native
PostgreSQL rows.

Current verification status (2026-09-30): Vercel CLI is installed, but this checkout
is not linked to a Vercel project and no `DATABASE_URL`, OIDC configuration or
Vercel token is available. Therefore no deployment or public URL is claimed yet.
The account owner must complete steps 1-3 before steps 4-5 can be tested.
