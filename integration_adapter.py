"""Read-only external-schema adapter into the existing Samanvay record contract."""
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

from load_corpus import load_mapped_csv, map_source_rows, validate_mapping
from phase3_attributes import assert_evidence_integrity, derive_description


def _preview_snapshot(headers, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def validate_for_matching(records):
    """Add integration-readiness issues without dropping or mutating source rows."""
    counts = Counter(record.get("source_record_id") for record in records
                     if record.get("source_record_id"))
    checked = []
    for record in records:
        item = dict(record)
        item["issues"] = [dict(issue) for issue in record["issues"]]
        source_id = item.get("source_record_id")
        if not source_id:
            item["issues"].append({"field": "source_record_id",
                                   "reason": "required_for_matching_workflow",
                                   "severity": "error"})
        elif counts[source_id] > 1:
            item["issues"].append({"field": "source_record_id",
                                   "reason": "duplicate_blocks_workspace_load",
                                   "severity": "error"})
        item["eligible_for_processing"] = not any(
            issue["severity"] == "error" for issue in item["issues"])
        checked.append(item)
    return checked


def _result(records, headers, mapping, source_sha256):
    checked = validate_for_matching(records)
    enriched = []
    for record in checked:
        if not record["eligible_for_processing"]:
            continue
        derived = derive_description(record)
        assert_evidence_integrity(derived)
        enriched.append(derived)
    used = (set(mapping["columns"].values()) | set(mapping.get("identifiers", [])) |
            set(mapping.get("specifications", [])))
    issues = Counter((issue["field"], issue["reason"], issue["severity"])
                     for record in checked for issue in record["issues"])
    report = {
        "contract_version": "samanvay-integration-v0.1",
        "mapping_id": mapping["mapping_id"],
        "source_sha256": source_sha256,
        "input_rows": len(checked),
        "canonical_records": len(checked),
        "matching_ready_records": len(enriched),
        "ineligible_records": len(checked) - len(enriched),
        "mapped_source_columns": sorted(used),
        "unmapped_source_columns": [header for header in headers if header not in used],
        "issue_counts": [{"field": field, "reason": reason, "severity": severity,
                          "count": count}
                         for (field, reason, severity), count in sorted(issues.items())],
        "transformations": ["identity text mapping", "blank-to-null with issue",
                            "existing Phase 3 description derivation for eligible rows"],
        "matching_core_changed": False,
        "erp_writes": False,
    }
    return {"report": report, "canonical_records": checked,
            "matching_records": enriched}


def preview_rows(headers, rows, mapping, *, source_name="integration-preview.csv"):
    validate_mapping(mapping)
    snapshot = _preview_snapshot(headers, rows)
    digest = hashlib.sha256(snapshot).hexdigest()
    records = map_source_rows(rows, headers, mapping, source_file=source_name,
                              source_sha256=digest)
    return _result(records, headers, mapping, digest)


def adapt_csv(path, mapping, *, import_root=None):
    validate_mapping(mapping)
    path = Path(path)
    snapshot = path.read_bytes()
    records = load_mapped_csv(path, mapping, import_root=import_root)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        headers = next(csv.reader(stream))
    if path.read_bytes() != snapshot:
        raise ValueError("Input changed during adaptation")
    return _result(records, headers, mapping, hashlib.sha256(snapshot).hexdigest())


def write_adapter_pack(path, mapping, output_dir, *, import_root=None):
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    result = adapt_csv(path, mapping, import_root=import_root)
    output.mkdir(parents=True, exist_ok=False)
    objects = {"mapping.json": mapping, "validation.json": result["report"]}
    for name, value in objects.items():
        with (output / name).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
    for name, records in (("canonical_records.jsonl", result["canonical_records"]),
                          ("matching_records.jsonl", result["matching_records"])):
        with (output / name).open("x", encoding="utf-8", newline="\n") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
    artifacts = {item.name: hashlib.sha256(item.read_bytes()).hexdigest()
                 for item in sorted(output.iterdir())}
    with (output / "manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump({"status": "complete", "read_only_erp_boundary": True,
                   "artifacts": artifacts}, stream, indent=2)
        stream.write("\n")
    return result["report"]
