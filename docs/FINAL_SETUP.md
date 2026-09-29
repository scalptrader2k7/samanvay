# Samanvay final setup guide

## Prerequisites

- Windows, Linux or macOS with Python 3.13.
- Git for a repository checkout.
- A modern browser. Microsoft Edge was used for final local replay.
- Approximately 1 GB of free space for the environment, local database and evidence.

The repository includes the protected source CSVs, processed candidate data, Phase 3 output pack and review/error artifacts needed by the demo. Verify their presence after checkout.

## Install

```powershell
git clone <repository-url> samanvay
cd samanvay
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python verify_raw_data.py
```

On POSIX shells, activate with `source .venv/bin/activate` and use `python3.13` when creating the environment.

## Local demonstration configuration

Local demonstration uses SQLite and a fixed local token. These values are for a local machine only.

```powershell
$env:SAMANVAY_STORAGE_BACKEND='sqlite'
$env:SAMANVAY_LOCAL_STORAGE_DIR='.local/samanvay-service'
$env:SAMANVAY_AUTH_MODE='demo'
$env:SAMANVAY_DEMO_TOKEN='choose-a-local-demo-token'
$env:SAMANVAY_DEMO_SUBJECT='local-demo-owner'
```

Create and seed the workspace once:

```powershell
python seed_service.py --workspace public-demo --owner-subject local-demo-owner --public-read --local-dir .local/samanvay-service
```

Repeated seeding is safe for the same source snapshot; the service storage rejects changed source content for an existing ID.

## Start and open

```powershell
python -m uvicorn api_service:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. Use workspace `public-demo`. Public browsing needs no token. To record decisions, enter the exact value of `SAMANVAY_DEMO_TOKEN`; the server resolves the actor from that token and enforces workspace ownership.

Check `http://127.0.0.1:8000/health`, `/ready`, and `/docs` if startup fails. A missing workspace returns 404; seed it using the command above. A 403 means the token subject does not own the workspace. Delete or move a disposable local workspace directory only when intentionally resetting that local demonstration; raw and output packs are separate.

## Verification and deterministic evidence run

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
node --check frontend/app.js
python verify_raw_data.py
python phase13_demo.py --output-dir reports/phase13-run
```

The evidence runner refuses an existing output directory. Use a new path for each run. It makes no source-file changes.

## Managed deployment configuration

Managed deployment uses PostgreSQL and OIDC. Never use demo authentication on Vercel; the application rejects it when `VERCEL=1`.

```text
SAMANVAY_STORAGE_BACKEND=postgres
DATABASE_URL=postgresql://...
SAMANVAY_AUTH_MODE=oidc
OIDC_ISSUER=https://...
OIDC_AUDIENCE=...
OIDC_JWKS_URL=https://.../.well-known/jwks.json
```

The schema and Vercel configuration are prepared, but managed Neon/OIDC/Vercel deployment was not validated because account credentials were unavailable. Follow `docs/phase8_deployment.md` after provisioning those services.

If `output/phase3-v0.1/material_attributes.jsonl` is absent in a fresh checkout, `seed_service.py` rebuilds the enriched records from `data/processed/material_candidates.csv` with the committed Phase 2 mapping and existing Phase 3 derivation before seeding.
