"""Build a no-overwrite Phase 7 demonstration registry and export pack."""
import argparse
import hashlib
import json
from pathlib import Path

from prototype_registry import RegistryStore, load_phase3_records


def generate(output_dir, records_path, review_sample, error_log):
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    input_paths = [Path(records_path), Path(review_sample), Path(error_log)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in input_paths}
    output.mkdir(parents=True, exist_ok=False)
    database = output / "prototype_registry.sqlite3"
    with RegistryStore(database) as store:
        imported = store.import_records(load_phase3_records(records_path))
        warnings = store.import_phase6_warnings(review_sample, error_log)
        approved = store.decide("approve", "identity", ["M000753", "M000925"],
            "Demonstration: matching normalized pipe specifications reviewed for prototype identity.",
            "phase7-demo", demonstration=True)
        repeated = store.decide("approve", "identity", ["M000925", "M000753"],
            "Demonstration repeat: verify stable proposed code.", "phase7-demo", demonstration=True)
        rejected = store.decide("reject", "identity", ["M000830", "M000834"],
            "Demonstration: different supported cable cross-sectional areas.",
            "phase7-demo", demonstration=True)
        deferred = store.decide("defer", "identity", ["M000114", "M000165"],
            "Demonstration: defer unrelated-family proposal for review workflow.",
            "phase7-demo", demonstration=True)
        reconsidered = store.reconsider(deferred["decision_id"], "reject",
            "Demonstration reconsideration: explicit family mismatch supports rejection.",
            "phase7-demo", demonstration=True)
        functional = store.decide("approve", "functional_equivalence", ["M000041", "M000114"],
            "Demonstration only: qualified-review relationship; not shared identity.",
            "phase7-demo", demonstration=True)
        preview = store.export(output / "exports")
        example = store.get_registry(approved["proposed_code"])
        history = store.decision_history()
    if approved["proposed_code"] != repeated["proposed_code"]:
        raise ValueError("Repeated approval changed the proposed code")
    after = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in input_paths}
    if after != before:
        raise ValueError("A Phase 7 input changed during demonstration generation")
    report = {
        "phase": "7", "status": "complete", "registry_version": "prototype-registry-v0.1",
        "demonstration_only": True, "evaluation_labels_created": 0,
        "source_records_imported": imported, "phase6_warnings_imported": warnings,
        "stable_repeat_code_check": True, "example_proposed_code": approved["proposed_code"],
        "prototype_status": example["prototype_status"], "example_members": len(example["members"]),
        "decisions": len(history), "identity_rejections": 2, "identity_deferrals": 1,
        "functional_relationships": preview["functional_relationships"],
        "mapped_records": preview["mapped_records"], "unresolved_records": preview["unresolved_records"],
        "records_missing_genuine_material_code": preview["records_missing_genuine_material_code"],
        "storage_requirement": "Phase 8 must use durable mounted storage or a managed transactional database; do not rely on an ephemeral server filesystem.",
    }
    for name, value in (("report.json", report), ("example_registry_entry.json", example),
                        ("demonstration_decisions.json", history)):
        with (output / name).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write("\n")
    artifacts = {}
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            artifacts[path.relative_to(output).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    with (output / "manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump({"status": "complete_demonstration", "artifacts": artifacts}, stream, indent=2); stream.write("\n")
    return report, example


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--records", default="output/phase3-v0.1/material_attributes.jsonl")
    parser.add_argument("--review-sample", default="reports/phase6/review_sample.csv")
    parser.add_argument("--error-log", default="reports/phase6/error_log.csv")
    args = parser.parse_args()
    try:
        report, _ = generate(args.output_dir, args.records, args.review_sample, args.error_log)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Phase 7 demonstration failed: {exc}\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
