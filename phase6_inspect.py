"""Validate Phase 6 sample invariants without assigning human judgments."""
import csv
import json
from pathlib import Path

from phase3_attributes import normalize_description
from phase6_sample import HUMAN_FIELDS


def inspect_sample(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    failures = []
    for row in rows:
        pair_id = row["review_pair_id"]
        if any(row[field].strip() for field in HUMAN_FIELDS):
            failures.append(f"{pair_id}: human fields must remain blank")
        if row["automated_outcome"] == "exact_duplicate":
            left = normalize_description(row["left_description_original"]).casefold()
            right = normalize_description(row["right_description_original"]).casefold()
            if left != right:
                failures.append(f"{pair_id}: exact duplicate lacks equal normalized text")
        if row["automated_outcome"] == "conflict" and not json.loads(
                row["automated_critical_conflicts_json"]):
            failures.append(f"{pair_id}: conflict lacks a critical conflict reason")
        disposition = row["automated_evidence_disposition"]
        if disposition == "insufficient_evidence" and row["automated_review_required"] != "true":
            failures.append(f"{pair_id}: insufficient evidence is not reviewable")
        if disposition == "supported_incompatibility" and row["automated_outcome"] == "no_match":
            reasons = json.loads(row["automated_reason_codes_json"])
            if "family.different_explicit_family" not in reasons:
                failures.append(f"{pair_id}: supported no-match lacks explicit incompatibility")
    return {"rows": len(rows), "failures": failures,
            "exact_rows": sum(r["automated_outcome"] == "exact_duplicate" for r in rows),
            "conflict_rows": sum(r["automated_outcome"] == "conflict" for r in rows),
            "insufficient_evidence_rows": sum(r["automated_evidence_disposition"] == "insufficient_evidence" for r in rows)}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample")
    args = parser.parse_args()
    report = inspect_sample(args.sample)
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(report["failures"]))
