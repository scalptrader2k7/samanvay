"""Samanvay Phase 8 FastAPI service."""
from collections import Counter
import csv
import hashlib
import io
import json
from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Path as ApiPath, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints

from candidate_retrieval import CandidateIndex
from pair_evidence import compare_pair
from prototype_registry import RegistrySafetyError
from quality_export import build_quality_workbook, registry_export_rows
from integration_adapter import preview_rows
from load_corpus import validate_mapping
from service_storage import (LocalWorkspaceStorage, PostgresWorkspaceStorage, WorkspaceAccessError,
                             WorkspaceNotFoundError)


class Settings(BaseModel):
    storage_backend: str = "sqlite"
    local_storage_dir: str = ".local/samanvay-service"
    auth_mode: str = "demo"
    demo_token: str = "local-development-token"
    demo_subject: str = "local-demo-owner"
    deployment_mode: bool = False
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    oidc_jwks_url: str | None = None
    database_url: str | None = None

    @classmethod
    def from_environment(cls):
        return cls(storage_backend=os.getenv("SAMANVAY_STORAGE_BACKEND", "sqlite"),
                   local_storage_dir=os.getenv("SAMANVAY_LOCAL_STORAGE_DIR", ".local/samanvay-service"),
                   auth_mode=os.getenv("SAMANVAY_AUTH_MODE", "demo"),
                   demo_token=os.getenv("SAMANVAY_DEMO_TOKEN", "local-development-token"),
                   demo_subject=os.getenv("SAMANVAY_DEMO_SUBJECT", "local-demo-owner"),
                   deployment_mode=os.getenv("VERCEL", "") == "1",
                   oidc_issuer=os.getenv("OIDC_ISSUER"),
                   oidc_audience=os.getenv("OIDC_AUDIENCE"),
                   oidc_jwks_url=os.getenv("OIDC_JWKS_URL"),
                   database_url=os.getenv("DATABASE_URL"))


SourceId = Annotated[str, StringConstraints(min_length=1, max_length=128,
                                             pattern=r"^[A-Za-z0-9._:-]+$")]


class DecisionRequest(BaseModel):
    action: str = Field(pattern=r"^(approve|reject|defer)$")
    relationship_type: str = Field(pattern=r"^(identity|functional_equivalence)$")
    member_ids: list[SourceId] = Field(min_length=2, max_length=50)
    reason: str = Field(min_length=5, max_length=1000)
    demonstration: bool = False


class ReconsiderRequest(BaseModel):
    action: str = Field(pattern=r"^(approve|reject|defer)$")
    reason: str = Field(min_length=5, max_length=1000)
    demonstration: bool = False


class WorkspaceRequest(BaseModel):
    public_read: bool = False


class IntegrationPreviewRequest(BaseModel):
    source_name: str = Field(min_length=1, max_length=128,
                             pattern=r"^[A-Za-z0-9][A-Za-z0-9._ -]*$")
    headers: list[str] = Field(min_length=1, max_length=100)
    rows: list[dict[str, str]] = Field(max_length=100)
    mapping: dict


class Page(BaseModel):
    items: list[dict]
    offset: int
    limit: int
    total: int
    next_offset: int | None


def _page(items, offset, limit):
    total = len(items)
    selected = items[offset:offset + limit]
    return Page(items=selected, offset=offset, limit=limit, total=total,
                next_offset=offset + limit if offset + limit < total else None)


def create_app(*, settings=None, storage=None):
    settings = settings or Settings.from_environment()
    if settings.deployment_mode and settings.auth_mode == "demo":
        raise RuntimeError("Demo authentication is forbidden in deployment mode")
    if storage is None:
        if settings.storage_backend == "postgres":
            storage = PostgresWorkspaceStorage(settings.database_url or os.getenv("DATABASE_URL"))
        elif settings.storage_backend == "sqlite":
            storage = LocalWorkspaceStorage(settings.local_storage_dir)
        else:
            raise RuntimeError("SAMANVAY_STORAGE_BACKEND must be sqlite or postgres")

    app = FastAPI(title="Samanvay API", version="0.2.0",
                  description="Prototype material harmonization service; no automatic merges.")
    app.state.settings = settings
    app.state.storage = storage

    def subject(request: Request):
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        if not authorization.startswith("Bearer "):
            raise HTTPException(401, "Authorization must use Bearer token")
        token = authorization[7:]
        if settings.auth_mode == "demo":
            if token != settings.demo_token:
                raise HTTPException(401, "Invalid local demo token")
            return settings.demo_subject
        if settings.auth_mode != "oidc" or not all(
                (settings.oidc_issuer, settings.oidc_audience, settings.oidc_jwks_url)):
            raise HTTPException(503, "OIDC authentication is not configured")
        import jwt
        try:
            key = jwt.PyJWKClient(settings.oidc_jwks_url).get_signing_key_from_jwt(token).key
            claims = jwt.decode(token, key, algorithms=["RS256", "ES256"],
                                audience=settings.oidc_audience, issuer=settings.oidc_issuer)
        except Exception as exc:
            raise HTTPException(401, "Invalid managed identity token") from exc
        identity = claims.get("sub")
        if not identity:
            raise HTTPException(401, "Managed identity token has no subject")
        return identity

    def require_subject(auth_subject=Depends(subject)):
        if not auth_subject:
            raise HTTPException(401, "Authentication required")
        return auth_subject

    def open_read(workspace_id, auth_subject):
        try:
            return storage.open_workspace(workspace_id, auth_subject, write=False)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.exception_handler(WorkspaceNotFoundError)
    async def missing_workspace(_request, exc):
        return __import__("fastapi").responses.JSONResponse(
            status_code=404, content={"detail": f"Workspace not found: {exc.args[0]}"})

    @app.exception_handler(WorkspaceAccessError)
    async def denied_workspace(_request, exc):
        return __import__("fastapi").responses.JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(RegistrySafetyError)
    async def registry_conflict(_request, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc), "pair_checks": exc.checks})

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "samanvay", "version": "0.2.0"}

    @app.get("/ready")
    def ready():
        try:
            result = storage.readiness()
            return {"status": "ready", "storage": result}
        except Exception as exc:
            raise HTTPException(503, f"Storage unavailable: {type(exc).__name__}") from exc

    @app.get("/api/v1/workspaces/{workspace_id}/materials", response_model=Page)
    def materials(workspace_id: str, offset: int = Query(0, ge=0),
                  limit: int = Query(25, ge=1, le=100), auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            rows = [dict(row) for row in store.connection.execute("""
                SELECT source_record_id, organization AS source_organization,
                       original_description AS description_original,
                       normalized_description AS description_normalized, family,
                       source_identifiers_json, genuine_material_codes_json
                FROM source_records ORDER BY source_record_id
            """)]
        import json
        for row in rows:
            row["source_identifiers"] = json.loads(row.pop("source_identifiers_json"))
            row["genuine_material_codes"] = json.loads(row.pop("genuine_material_codes_json"))
        return _page(rows, offset, limit)

    @app.post("/api/v1/workspaces/{workspace_id}")
    def create_workspace(workspace_id: str, payload: WorkspaceRequest,
                         auth_subject=Depends(require_subject)):
        try:
            created = storage.create_workspace(workspace_id, auth_subject,
                                               public_read=payload.public_read)
            return {"workspace_id": workspace_id, "owner_subject": auth_subject,
                    "public_read": payload.public_read, "created": created}
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/api/v1/workspaces/{workspace_id}/materials/search", response_model=Page)
    def search_materials(workspace_id: str, q: str = Query(min_length=2, max_length=200),
                         offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100),
                         auth_subject=Depends(subject)):
        needle = q.casefold()
        with open_read(workspace_id, auth_subject) as store:
            records = [store.get_source_record(row[0]) for row in store.connection.execute(
                "SELECT source_record_id FROM source_records ORDER BY source_record_id")]
        matched = [record for record in records if needle in record["source_record_id"].casefold()
                   or needle in record["description_normalized"].casefold()
                   or needle in record["source_organization"].casefold()]
        return _page(matched, offset, limit)

    @app.get("/api/v1/workspaces/{workspace_id}/materials/{source_id}/candidates")
    def candidates(workspace_id: str, source_id: str, top_k: int = Query(10, ge=1, le=50),
                   auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            records = [store.get_source_record(row[0]) for row in store.connection.execute(
                "SELECT source_record_id FROM source_records ORDER BY source_record_id")]
        try:
            results, diagnostics = CandidateIndex(records).retrieve(source_id, top_k=top_k)
        except KeyError as exc:
            raise HTTPException(404, f"Material not found: {source_id}") from exc
        return {"retrieval_type": "bounded_lexical", "identity_decision": False,
                "items": results, "diagnostics": diagnostics}

    @app.get("/api/v1/workspaces/{workspace_id}/pairs/{left_id}/{right_id}")
    def pair(workspace_id: str, left_id: str, right_id: str, auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            try:
                left, right = store.get_source_record(left_id), store.get_source_record(right_id)
            except KeyError as exc:
                raise HTTPException(404, f"Material not found: {exc.args[0]}") from exc
        try:
            return compare_pair(left, right)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/api/v1/workspaces/{workspace_id}/registry", response_model=Page)
    def registry(workspace_id: str, offset: int = Query(0, ge=0),
                 limit: int = Query(25, ge=1, le=100), auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            codes = [row[0] for row in store.connection.execute(
                "SELECT proposed_code FROM registry_entries ORDER BY proposed_code")]
            items = [store.get_registry(code) for code in codes]
        return _page(items, offset, limit)

    @app.get("/api/v1/workspaces/{workspace_id}/registry/{proposed_code}")
    def registry_entry(workspace_id: str, proposed_code: str = ApiPath(
            pattern=r"^SMV-P-[0-9A-F]{12}$"), auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            try:
                return store.get_registry(proposed_code)
            except KeyError as exc:
                raise HTTPException(404, f"Registry entry not found: {proposed_code}") from exc

    @app.get("/api/v1/workspaces/{workspace_id}/mappings", response_model=Page)
    def mappings(workspace_id: str, offset: int = Query(0, ge=0),
                 limit: int = Query(25, ge=1, le=100), auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            rows = store.migration_rows()
        return _page(rows, offset, limit)

    @app.get("/api/v1/workspaces/{workspace_id}/decisions", response_model=Page)
    def decisions(workspace_id: str, offset: int = Query(0, ge=0),
                  limit: int = Query(25, ge=1, le=100), source_id: SourceId | None = None,
                  auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            rows = store.decision_history()
        if source_id:
            rows = [row for row in rows if source_id in row["member_ids"]]
        return _page(rows, offset, limit)

    @app.get("/api/v1/workspaces/{workspace_id}/governance/access")
    def governance_access(workspace_id: str, auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject):
            metadata = storage.metadata(workspace_id)
        owner = bool(auth_subject and auth_subject == metadata["owner_subject"])
        return {"workspace_id": workspace_id,
                "role": "governance_owner" if owner else "public_viewer",
                "authenticated": bool(auth_subject),
                "permissions": {
                    "view_review": True,
                    "review_decide": owner,
                    "governance_reconsider": owner,
                    "view_audit": True,
                }}

    @app.get("/api/v1/workspaces/{workspace_id}/audit-events", response_model=Page)
    def audit_events(workspace_id: str, offset: int = Query(0, ge=0),
                     limit: int = Query(25, ge=1, le=100),
                     source_id: SourceId | None = None,
                     event_type: str | None = Query(None, max_length=64),
                     auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            rows = store.audit_history(source_id=source_id, event_type=event_type)
        return _page(rows, offset, limit)

    @app.get("/api/v1/workspaces/{workspace_id}/mapping-history", response_model=Page)
    def mapping_history(workspace_id: str, offset: int = Query(0, ge=0),
                        limit: int = Query(25, ge=1, le=100),
                        source_id: SourceId | None = None,
                        proposed_code: str | None = Query(None, pattern=r"^SMV-P-[0-9A-F]{12}$"),
                        auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            rows = store.mapping_history(source_id=source_id, proposed_code=proposed_code)
        return _page(rows, offset, limit)

    @app.get("/api/v1/workspaces/{workspace_id}/functional-relationships", response_model=Page)
    def relationships(workspace_id: str, offset: int = Query(0, ge=0),
                      limit: int = Query(25, ge=1, le=100), auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            rows = [dict(row) for row in store.connection.execute(
                "SELECT * FROM functional_relationships ORDER BY relationship_id")]
        return _page(rows, offset, limit)

    @app.get("/api/v1/workspaces/{workspace_id}/dashboard")
    def dashboard(workspace_id: str, auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            sources = [dict(row) for row in store.connection.execute(
                "SELECT organization, family FROM source_records")]
            decisions_rows = store.decision_history()
            audit_count = len(store.audit_history())
            mapping_change_count = len(store.mapping_history())
            preview = store.migration_preview(); preview.pop("rows")
        return {**preview,
                "organizations": dict(Counter(row["organization"] for row in sources)),
                "families": dict(Counter(row["family"] or "unknown" for row in sources)),
                "decision_actions": dict(Counter(row["action"] for row in decisions_rows)),
                "audit_events": audit_count,
                "mapping_changes": mapping_change_count,
                "counts_source": "persisted workspace records and decisions"}

    @app.get("/api/v1/workspaces/{workspace_id}/quality-dashboard")
    def quality_dashboard(workspace_id: str, auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            return store.quality_dashboard()

    integration_dir = Path(__file__).resolve().parent / "contracts" / "integration"
    integration_examples_dir = Path(__file__).resolve().parent / "examples" / "phase12"

    def read_json(path):
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)

    def integration_example(name):
        if name not in {"public", "cpse-sap"}:
            raise HTTPException(404, "Unknown integration example")
        csv_path = integration_examples_dir / f"{name}_example.csv"
        mapping = read_json(integration_dir / f"{name}_mapping_v0.1.json")
        with csv_path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return {"name": name, "source_name": csv_path.name,
                    "headers": reader.fieldnames, "rows": list(reader), "mapping": mapping}

    @app.get("/api/v1/workspaces/{workspace_id}/integration/contract")
    def integration_contract(workspace_id: str, auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject):
            pass
        return {"boundary": "read-only-preview", "erp_writes": False,
                "persistence": False,
                "canonical_schema": read_json(integration_dir / "canonical_schema_v0.1.json"),
                "mapping_contract": read_json(integration_dir / "mapping_contract_v0.1.json")}

    @app.get("/api/v1/workspaces/{workspace_id}/integration/examples")
    def integration_examples(workspace_id: str, auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject):
            pass
        return {"items": [integration_example("public"), integration_example("cpse-sap")],
                "erp_writes": False, "persistence": False}

    @app.get("/api/v1/workspaces/{workspace_id}/integration/templates/{name}.csv")
    def integration_template(workspace_id: str, name: str, auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject):
            pass
        if name not in {"public", "cpse-sap"}:
            raise HTTPException(404, "Unknown integration template")
        return FileResponse(integration_examples_dir / f"{name}_import_template.csv",
                            media_type="text/csv; charset=utf-8",
                            filename=f"samanvay_{name}_import_template.csv")

    @app.post("/api/v1/workspaces/{workspace_id}/integration/validate-preview")
    def integration_preview(workspace_id: str, payload: IntegrationPreviewRequest,
                            auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject):
            pass
        try:
            validate_mapping(payload.mapping)
            result = preview_rows(payload.headers, payload.rows, payload.mapping,
                                  source_name=payload.source_name)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        return {**result, "persisted": False, "erp_writes": False,
                "next_step": "An authenticated administrator may load a validated adapter pack with the offline seeding utility."}

    def request_hash(value):
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    @app.post("/api/v1/workspaces/{workspace_id}/decisions")
    def create_decision(workspace_id: str, payload: DecisionRequest,
                        idempotency_key: str = Header(min_length=8, max_length=128,
                                                      alias="Idempotency-Key"),
                        auth_subject=Depends(require_subject)):
        data = payload.model_dump()
        try:
            with storage.open_workspace(workspace_id, auth_subject, write=True) as store:
                return store.decide_idempotent(idempotency_key, request_hash(data),
                    payload.action, payload.relationship_type, payload.member_ids,
                    payload.reason, auth_subject, demonstration=payload.demonstration)
        except RegistrySafetyError:
            raise
        except KeyError as exc:
            raise HTTPException(404, f"Material not found: {exc.args[0]}") from exc
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.post("/api/v1/workspaces/{workspace_id}/decisions/{decision_id}/reconsider")
    def reconsider_decision(workspace_id: str, decision_id: int, payload: ReconsiderRequest,
                            idempotency_key: str = Header(min_length=8, max_length=128,
                                                          alias="Idempotency-Key"),
                            auth_subject=Depends(require_subject)):
        data = {"decision_id": decision_id, **payload.model_dump()}
        try:
            with storage.open_workspace(workspace_id, auth_subject, write=True) as store:
                return store.reconsider_idempotent(idempotency_key, request_hash(data),
                    decision_id, payload.action, payload.reason, auth_subject,
                    demonstration=payload.demonstration)
        except RegistrySafetyError:
            raise
        except KeyError as exc:
            raise HTTPException(404, f"Decision not found: {exc.args[0]}") from exc
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/api/v1/workspaces/{workspace_id}/migration-preview")
    def migration_preview(workspace_id: str, auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            result = store.migration_preview(); result.pop("rows")
            return result

    @app.get("/api/v1/workspaces/{workspace_id}/exports/source-mappings.json")
    def mappings_json(workspace_id: str, offset: int = Query(0, ge=0),
                      limit: int = Query(100, ge=1, le=1000), auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            return _page(store.migration_rows(), offset, limit)

    @app.get("/api/v1/workspaces/{workspace_id}/exports/source-mappings.csv")
    def mappings_csv(workspace_id: str, offset: int = Query(0, ge=0),
                     limit: int = Query(100, ge=1, le=1000), auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            all_rows = store.migration_rows(); rows = all_rows[offset:offset + limit]
        fields = list(rows[0]) if rows else []
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        for row in rows:
            rendered = {}
            for key, value in row.items():
                value = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
                    value = "'" + value
                rendered[key] = value
            writer.writerow(rendered)
        return Response(stream.getvalue(), media_type="text/csv; charset=utf-8",
                        headers={"Content-Disposition": "attachment; filename=source_mappings.csv",
                                 "X-Total-Count": str(len(all_rows)), "X-Offset": str(offset),
                                 "X-Limit": str(limit)})

    @app.get("/api/v1/workspaces/{workspace_id}/exports/quality-pack.xlsx")
    def quality_pack_xlsx(workspace_id: str, auth_subject=Depends(subject)):
        with open_read(workspace_id, auth_subject) as store:
            payload = build_quality_workbook(store)
            state_hash = store.quality_dashboard()["workspace_state_sha256"]
        return Response(payload,
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=samanvay_quality_pack.xlsx",
                                 "X-Workspace-State-SHA256": state_hash,
                                 "X-Export-Scope": "current-state-no-history"})

    def export_dataset(store, dataset):
        if dataset == "source-mappings":
            return store.migration_rows()
        if dataset == "unresolved-records":
            return [row for row in store.migration_rows() if row["mapping_status"] == "unresolved"]
        if dataset == "conflicts":
            return store.conflict_rows()
        if dataset == "registry":
            return registry_export_rows(store)
        if dataset == "decisions":
            return store.decision_history()
        if dataset == "audit-events":
            return store.audit_history()
        if dataset == "mapping-history":
            return store.mapping_history()
        if dataset == "functional-relationships":
            return [dict(row) for row in store.connection.execute(
                "SELECT * FROM functional_relationships ORDER BY relationship_id")]
        raise HTTPException(404, f"Unknown export dataset: {dataset}")

    @app.get("/api/v1/workspaces/{workspace_id}/exports/{dataset}.{format}")
    def generic_export(workspace_id: str, dataset: str, format: str,
                       offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000),
                       auth_subject=Depends(subject)):
        if format not in {"json", "csv"}:
            raise HTTPException(404, "Export format must be json or csv")
        with open_read(workspace_id, auth_subject) as store:
            all_rows = export_dataset(store, dataset)
        rows = all_rows[offset:offset + limit]
        if format == "json":
            return _page(rows, offset, limit)
        fields = list(rows[0]) if rows else []
        stream = io.StringIO(newline=""); writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            rendered = {}
            for key, value in row.items():
                value = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
                    value = "'" + value
                rendered[key] = value
            writer.writerow(rendered)
        return Response(stream.getvalue(), media_type="text/csv; charset=utf-8",
                        headers={"Content-Disposition": f"attachment; filename={dataset}.csv",
                                 "X-Total-Count": str(len(all_rows)), "X-Offset": str(offset),
                                 "X-Limit": str(limit)})

    frontend_dir = Path(__file__).resolve().parent / "frontend"
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def reviewer_interface():
        return FileResponse(frontend_dir / "index.html")

    return app


app = create_app()
