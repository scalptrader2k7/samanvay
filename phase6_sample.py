"""Create a deterministic, unordered Phase 6 human-review sample."""
import argparse
import csv
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from pair_evidence import compare_pair


OUTCOMES = ("exact_duplicate", "near_duplicate", "possible_functional_equivalent", "conflict", "no_match")
HUMAN_FIELDS = ("human_judgment", "human_confidence", "human_reason", "human_reviewer_id", "human_reviewed_at")


def load_records(path):
    with Path(path).open(encoding="utf-8") as stream:
        return {record["source_record_id"]: record for record in map(json.loads, stream)}


def load_unordered_retrievals(path):
    pairs = defaultdict(list)
    with Path(path).open(encoding="utf-8") as stream:
        for query in map(json.loads, stream):
            query_id = query["query_source_record_id"]
            for item in query["candidates"]:
                candidate_id = item["candidate_source_record_id"]
                key = tuple(sorted((query_id, candidate_id)))
                pairs[key].append({"query_source_record_id": query_id,
                    "candidate_source_record_id": candidate_id, "rank": item["rank"],
                    "retrieval_score": item["retrieval_score"], "reasons": item["reasons"]})
    for directions in pairs.values():
        directions.sort(key=lambda x: (x["query_source_record_id"], x["candidate_source_record_id"]))
    return pairs


def _stable_hash(key):
    return hashlib.sha256(("phase6-review-v0.1|" + "|".join(key)).encode()).hexdigest()


def _features(result):
    fields = result["field_comparisons"]
    families = tuple(sorted({x for x in (fields["family"]["left_value"],
                                         fields["family"]["right_value"]) if x})) or ("unknown",)
    return {"families": families,
            "cross_organization": result["left"]["source_organization"] != result["right"]["source_organization"],
            "has_missing_or_uncertain": bool(result["missing_or_uncertain_attributes"]),
            "has_critical_conflict": any(fields[name]["conflicts"] for name in
                ("size_dimension", "material_grade", "standard", "pressure", "voltage"))}


def _select(pool, count):
    selected, covered = [], set()
    remaining = list(pool)
    while remaining and len(selected) < count:
        def ordering(item):
            feature_keys = {("family", family) for family in item["features"]["families"]}
            feature_keys |= {("cross_org", item["features"]["cross_organization"]),
                             ("missing", item["features"]["has_missing_or_uncertain"]),
                             ("critical", item["features"]["has_critical_conflict"]),
                             ("basis", item["comparison"]["outcome"]["evidence_disposition"])}
            return (-len(feature_keys - covered), item["hash"])
        chosen = min(remaining, key=ordering)
        selected.append(chosen); remaining.remove(chosen)
        covered |= {("family", family) for family in chosen["features"]["families"]}
        covered |= {("cross_org", chosen["features"]["cross_organization"]),
                    ("missing", chosen["features"]["has_missing_or_uncertain"]),
                    ("critical", chosen["features"]["has_critical_conflict"]),
                    ("basis", chosen["comparison"]["outcome"]["evidence_disposition"])}
    if len(selected) != count:
        raise ValueError(f"Only {len(selected)} eligible pairs for requested quota {count}")
    return selected


def _csv_row(index, item, records):
    result, directions = item["comparison"], item["retrieval_directions"]
    left_id, right_id = result["left"]["source_record_id"], result["right"]["source_record_id"]
    fields, outcome = result["field_comparisons"], result["outcome"]
    conflicts = [reason["reason_code"] for name in
                 ("size_dimension", "material_grade", "standard", "pressure", "voltage")
                 for reason in fields[name]["conflicts"]]
    row = {"review_pair_id": f"P6-{index:03d}", "left_source_record_id": left_id,
           "right_source_record_id": right_id,
           "left_source_organization": result["left"]["source_organization"],
           "right_source_organization": result["right"]["source_organization"],
           "left_source_identifiers_json": json.dumps(records[left_id].get("source_identifiers", {}), ensure_ascii=False),
           "right_source_identifiers_json": json.dumps(records[right_id].get("source_identifiers", {}), ensure_ascii=False),
           "left_description_original": result["left"]["description_original"],
           "right_description_original": result["right"]["description_original"],
           "automated_outcome": outcome["label"],
           "automated_evidence_disposition": outcome["evidence_disposition"],
           "automated_explanation": outcome["explanation"],
           "automated_reason_codes_json": json.dumps(outcome["reason_codes"]),
           "automated_missing_or_uncertain_json": json.dumps(result["missing_or_uncertain_attributes"]),
           "automated_critical_conflicts_json": json.dumps(conflicts),
           "automated_review_required": str(outcome["review_required"]).lower(),
           "retrieval_directions_json": json.dumps(directions, ensure_ascii=False)}
    row.update({field: "" for field in HUMAN_FIELDS})
    return row


def generate(records_path, candidates_path, output_dir, *, total=100):
    if total % len(OUTCOMES):
        raise ValueError("Sample total must divide evenly across the five outcomes")
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    records = load_records(records_path)
    retrievals = load_unordered_retrievals(candidates_path)
    pools = defaultdict(list)
    for key, directions in retrievals.items():
        left, right = records[key[0]], records[key[1]]
        comparison = compare_pair(left, right)
        item = {"key": key, "hash": _stable_hash(key), "comparison": comparison,
                "features": _features(comparison), "retrieval_directions": directions}
        pools[comparison["outcome"]["label"]].append(item)
    quota = total // len(OUTCOMES)
    selected = []
    for outcome in OUTCOMES:
        selected.extend(_select(pools[outcome], quota))
    selected.sort(key=lambda x: (OUTCOMES.index(x["comparison"]["outcome"]["label"]), x["hash"]))
    output.mkdir(parents=True, exist_ok=False)
    rows = [_csv_row(index, item, records) for index, item in enumerate(selected, 1)]
    with (output / "review_sample.csv").open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    with (output / "review_evidence.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
        for row, item in zip(rows, selected):
            stream.write(json.dumps({"review_pair_id": row["review_pair_id"],
                "comparison": item["comparison"],
                "retrieval_directions": item["retrieval_directions"],
                "human_review": {field: "" for field in HUMAN_FIELDS}},
                ensure_ascii=False, allow_nan=False) + "\n")
    outcome_counts = Counter(row["automated_outcome"] for row in rows)
    disposition_counts = Counter(row["automated_evidence_disposition"] for row in rows)
    report = {"phase": "6", "status": "review_preparation",
              "sample_scope": "Deterministic stratified review sample; not a population estimate.",
              "directed_phase4_pairs": sum(len(x) for x in retrievals.values()),
              "unique_unordered_pairs": len(retrievals), "sample_pairs": len(rows),
              "outcome_quotas": dict(outcome_counts), "evidence_dispositions": dict(disposition_counts),
              "cross_organization_pairs": sum(r["left_source_organization"] != r["right_source_organization"] for r in rows),
              "pairs_with_missing_or_uncertain": sum(r["automated_missing_or_uncertain_json"] != "[]" for r in rows),
              "pairs_with_critical_conflicts": sum(r["automated_critical_conflicts_json"] != "[]" for r in rows),
              "family_mentions": dict(Counter(family for item in selected for family in item["features"]["families"])),
              "human_labeled_pairs": 0, "validation_status": "pending_human_review",
              "accuracy_metrics_reported": False}
    with (output / "sample_report.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2); stream.write("\n")
    artifacts = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
    with (output / "manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump({"status": "review_preparation", "artifacts": artifacts}, stream, indent=2); stream.write("\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", default="output/phase3-v0.1/material_attributes.jsonl")
    parser.add_argument("--candidates", default="output/phase4-v0.1/candidates.jsonl")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--total", type=int, default=100)
    args = parser.parse_args()
    try:
        report = generate(args.records, args.candidates, args.output_dir, total=args.total)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Phase 6 sampling failed: {exc}\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
