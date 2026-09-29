"""Compute scoped metrics only from actual, valid Phase 6 human judgments."""
import argparse
import csv
from collections import Counter, defaultdict
import json
from pathlib import Path


LABELS = ("exact_duplicate", "near_duplicate", "possible_functional_equivalent",
          "conflict", "no_match", "insufficient_evidence")


def automated_category(row):
    if (row["automated_outcome"] == "no_match" and
            row["automated_evidence_disposition"] == "insufficient_evidence"):
        return "insufficient_evidence"
    return row["automated_outcome"]


def evaluate_rows(rows):
    rows = list(rows)
    labeled = []
    for row in rows:
        human = row.get("human_judgment", "").strip()
        if not human:
            continue
        if human not in LABELS:
            raise ValueError(f"Invalid human_judgment {human!r} for {row.get('review_pair_id', 'unknown pair')}")
        labeled.append((automated_category(row), human))
    result = {"sample_rows": len(rows), "human_labeled_rows": len(labeled),
              "unlabeled_rows": len(rows) - len(labeled),
              "sample_scope": "Phase 6 deterministic review sample; metrics use human-labeled rows only."}
    if not labeled:
        result["validation_status"] = "pending_human_review"
        result["performance_metrics_reported"] = False
        return result
    confusion = defaultdict(Counter)
    for predicted, actual in labeled:
        confusion[actual][predicted] += 1
    correct = sum(predicted == actual for predicted, actual in labeled)
    per_label = {}
    for label in LABELS:
        true_positive = confusion[label][label]
        predicted_total = sum(confusion[actual][label] for actual in LABELS)
        actual_total = sum(confusion[label].values())
        per_label[label] = {
            "labeled_support": actual_total,
            "precision": (true_positive / predicted_total) if predicted_total else None,
            "recall": (true_positive / actual_total) if actual_total else None,
        }
    result.update({"validation_status": "partial_human_review" if len(labeled) < len(rows) else "human_review_complete",
                   "performance_metrics_reported": True,
                   "metric_denominator": len(labeled),
                   "accuracy": correct / len(labeled),
                   "per_label": per_label,
                   "confusion": {actual: dict(counts) for actual, counts in sorted(confusion.items())}})
    return result


def evaluate_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return evaluate_rows(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = evaluate_csv(args.sample)
        rendered = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            with Path(args.output).open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(rendered)
        else:
            print(rendered, end="")
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Phase 6 metrics failed: {exc}\n")


if __name__ == "__main__":
    main()
