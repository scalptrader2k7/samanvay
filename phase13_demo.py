"""Run Samanvay's deterministic local Phase 13 evidence workflow."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import tempfile

from fastapi.testclient import TestClient

from api_service import Settings, create_app
from load_corpus import read_mapping
from integration_adapter import adapt_csv
from seed_service import load_seed_records
from service_storage import LocalWorkspaceStorage

ROOT = Path(__file__).resolve().parent
RAW_FILES = [
    "data/raw/huggingface/material_description_corpus.csv",
    "data/raw/huggingface/ntpc_material_items.csv",
    "data/raw/huggingface/iocl_procurement_plan_items.csv",
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                     allow_nan=False) + "\n", encoding="utf-8")


def run(output_dir):
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    output.mkdir(parents=True)
    before = {name: sha(ROOT / name) for name in RAW_FILES}

    temporary_storage = tempfile.TemporaryDirectory(prefix="samanvay-phase13-")
    storage = LocalWorkspaceStorage(Path(temporary_storage.name) / "storage")
    workspace, owner, token = "phase13-demo", "phase13-local-owner", "phase13-local-token"
    storage.create_workspace(workspace, owner, public_read=True)
    records = load_seed_records()
    with storage.open_workspace(workspace, owner, write=True) as store:
        inserted = store.import_records(records)
        warnings = store.import_phase6_warnings(ROOT / "reports/phase6/review_sample.csv",
                                                ROOT / "reports/phase6/error_log.csv")
    app = create_app(settings=Settings(demo_token=token, demo_subject=owner), storage=storage)
    client = TestClient(app)
    base = f"/api/v1/workspaces/{workspace}"
    auth = {"Authorization": f"Bearer {token}"}

    def get(path, headers=None):
        response = client.get(path, headers=headers or {})
        response.raise_for_status(); return response

    def post(path, payload, key):
        response = client.post(path, json=payload,
                               headers={**auth, "Idempotency-Key": key})
        response.raise_for_status(); return response

    evidence = {}
    evidence["health"] = get("/health").json()
    evidence["readiness"] = get("/ready").json()
    evidence["search"] = get(base + "/materials/search?q=M000753&limit=10").json()
    evidence["candidates"] = get(base + "/materials/M000753/candidates?top_k=5").json()
    evidence["pair"] = get(base + "/pairs/M000753/M000925").json()
    evidence["critical_conflict"] = get(base + "/pairs/M000830/M000834").json()

    approval = post(base + "/decisions", {
        "action": "approve", "relationship_type": "identity",
        "member_ids": ["M000753", "M000925"],
        "reason": "Phase 13 local demo approval using displayed matching pipe evidence",
        "demonstration": True,
    }, "phase13-approve-0001").json()
    evidence["approval"] = approval
    decision_id = approval["decision_id"]
    evidence["registry_after_approval"] = get(base + "/registry?limit=10").json()

    deferred = post(base + f"/decisions/{decision_id}/reconsider", {
        "action": "defer", "reason": "Phase 13 demo of reversible governance history",
        "demonstration": True,
    }, "phase13-defer-0001").json()
    evidence["defer_reconsideration"] = deferred
    restored = post(base + f"/decisions/{deferred['decision_id']}/reconsider", {
        "action": "approve", "reason": "Phase 13 demo restores the supported prototype mapping",
        "demonstration": True,
    }, "phase13-restore-0001").json()
    evidence["restore_reconsideration"] = restored

    evidence["registry_current"] = get(base + "/registry?limit=10").json()
    evidence["mappings_current"] = get(base + "/mappings?limit=10").json()
    evidence["decisions"] = get(base + "/decisions?limit=10").json()
    evidence["audit_events"] = get(base + "/audit-events?limit=20").json()
    evidence["mapping_history"] = get(base + "/mapping-history?limit=20").json()
    evidence["quality_dashboard"] = get(base + "/quality-dashboard").json()

    examples = get(base + "/integration/examples").json()["items"]
    integration = []
    for item in examples:
        response = client.post(base + "/integration/validate-preview", json=item)
        response.raise_for_status(); integration.append(response.json())
    evidence["integration_previews"] = integration

    exports = {
        "registry.json": get(base + "/exports/registry.json?limit=1000").content,
        "source_mappings.csv": get(base + "/exports/source-mappings.csv?limit=1000").content,
        "audit_events.json": get(base + "/exports/audit-events.json?limit=1000").content,
        "quality_pack.xlsx": get(base + "/exports/quality-pack.xlsx").content,
    }
    export_hashes = {}
    for name, payload in exports.items():
        (output / name).write_bytes(payload)
        export_hashes[name] = hashlib.sha256(payload).hexdigest()

    after = {name: sha(ROOT / name) for name in RAW_FILES}
    if before != after:
        raise RuntimeError("A protected raw source changed during the demo")
    pair = evidence["pair"]; conflict = evidence["critical_conflict"]
    current_registry = evidence["registry_current"]
    checks = {
        "all_9245_records_seeded": inserted == 9245,
        "candidate_contains_verified_pair": any(x["candidate_source_record_id"] == "M000925"
            for x in evidence["candidates"]["items"]),
        "pair_outcome_near_duplicate": pair["outcome"]["label"] == "near_duplicate",
        "critical_conflict_blocks_identity": conflict["outcome"]["label"] == "conflict"
            and conflict["outcome"]["identity_merge_blocked"],
        "prototype_code_created": current_registry["total"] == 1
            and current_registry["items"][0]["proposed_code"].startswith("SMV-P-"),
        "both_sources_mapped": evidence["quality_dashboard"]["mapping_coverage"]["mapped"] == 2,
        "governance_history_retained": evidence["audit_events"]["total"] == 3,
        "integration_schemas_same_core": all(x["report"]["matching_core_changed"] is False
            and x["persisted"] is False and x["erp_writes"] is False for x in integration)
            and [x["source_record_id"] for x in integration[0]["matching_records"]]
              == [x["source_record_id"] for x in integration[1]["matching_records"]],
        "raw_sources_unchanged": before == after,
    }
    if not all(checks.values()):
        raise AssertionError({key: value for key, value in checks.items() if not value})
    for name, value in evidence.items(): dump(output / f"{name}.json", value)
    summary = {
        "status": "passed", "workspace": workspace, "records_inserted": inserted,
        "phase6_warnings_inserted": warnings, "source_pair": ["M000753", "M000925"],
        "conflict_pair": ["M000830", "M000834"],
        "prototype_code": current_registry["items"][0]["proposed_code"],
        "checks": checks, "raw_sha256_before_and_after": before,
        "export_sha256": export_hashes, "python": platform.python_version(),
        "scope": "Local SQLite and demo-token workflow; not managed deployment validation.",
    }
    dump(output / "summary.json", summary)
    client.close()
    temporary_storage.cleanup()
    print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(); run(args.output_dir)


if __name__ == "__main__": main()
