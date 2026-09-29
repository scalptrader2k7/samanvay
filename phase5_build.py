"""Build a no-overwrite Phase 5 evidence pack from frozen Phase 3/4 outputs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time

from pair_evidence import compare_pair


EXAMPLES = (
    ("identical descriptions from separate rows", "M000114", "M008245", "exact_duplicate"),
    ("minor wording/format changes with matching specifications", "M000753", "M000925", "near_duplicate"),
    ("15 mm versus 25 mm pipes", "M000913", "M000927", "conflict"),
    ("150 mm2 versus 240 mm2 cables", "M000830", "M000834", "conflict"),
    ("different valve pressure-rating bases", "M010407", "M003626", "conflict"),
    ("same pump family with missing specifications", "M000041", "M000114", "possible_functional_equivalent"),
    ("unrelated explicit families sharing generic material context", "M000114", "M000165", "no_match"),
)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_records(path):
    with Path(path).open(encoding="utf-8") as stream:
        return {record["source_record_id"]: record for record in map(json.loads, stream)}


def _example_retrievals(candidate_path):
    wanted = {(left, right) for _, left, right, _ in EXAMPLES}
    found = {}
    with Path(candidate_path).open(encoding="utf-8") as stream:
        for query in map(json.loads, stream):
            query_id = query["query_source_record_id"]
            for candidate in query["candidates"]:
                key = (query_id, candidate["candidate_source_record_id"])
                if key in wanted:
                    found[key] = candidate
    return found


def generate(records_path, candidates_path, output_dir):
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    records_path, candidates_path = Path(records_path), Path(candidates_path)
    before = {str(records_path): _sha(records_path), str(candidates_path): _sha(candidates_path)}
    records = load_records(records_path)
    counts, pairs, reviews, blocked = Counter(), 0, 0, 0
    query_count, queries_with_pairs = 0, 0
    started = time.perf_counter()
    output.mkdir(parents=True, exist_ok=False)
    evidence_path = output / "pair_evidence.jsonl"
    with candidates_path.open(encoding="utf-8") as source, evidence_path.open(
            "x", encoding="utf-8", newline="\n") as target:
        for query in map(json.loads, source):
            query_count += 1
            query_id = query["query_source_record_id"]
            if query_id not in records:
                raise ValueError(f"Unknown Phase 4 query ID: {query_id}")
            queries_with_pairs += bool(query["candidates"])
            for candidate in query["candidates"]:
                candidate_id = candidate["candidate_source_record_id"]
                if candidate_id not in records:
                    raise ValueError(f"Unknown Phase 4 candidate ID: {candidate_id}")
                result = compare_pair(records[query_id], records[candidate_id], candidate)
                label = result["outcome"]["label"]
                counts[label] += 1
                reviews += result["outcome"]["review_required"]
                blocked += result["outcome"]["identity_merge_blocked"]
                pairs += 1
                target.write(json.dumps(result, ensure_ascii=False, allow_nan=False) + "\n")
    example_retrievals = _example_retrievals(candidates_path)
    examples = []
    for name, left, right, expected in EXAMPLES:
        result = compare_pair(records[left], records[right], example_retrievals.get((left, right)))
        examples.append({"name": name, "expected_rule_output": expected,
                         "passed": result["outcome"]["label"] == expected,
                         "comparison": result})
    elapsed = time.perf_counter() - started
    report = {
        "phase": "5", "status": "complete", "comparison_version": "pair-evidence-v0.1",
        "inputs": {"phase3_records_sha256": before[str(records_path)],
                   "phase4_candidates_sha256": before[str(candidates_path)]},
        "source_records": len(records), "phase4_query_records": query_count,
        "queries_with_pairs": queries_with_pairs, "pair_results": pairs,
        "outcome_rule_counts": dict(sorted(counts.items())),
        "review_required_rule_count": reviews,
        "identity_merge_blocked_rule_count": blocked,
        "runtime_seconds": round(elapsed, 6),
        "named_example_checks": {"passed": sum(x["passed"] for x in examples),
                                 "total": len(examples),
                                 "scope": "Rule-output checks on named examples; not accuracy metrics."},
        "automatic_merges": 0, "common_codes_assigned": 0,
        "limitations": [
            "Outcomes are deterministic rule outputs, not measured accuracy or engineering validation.",
            "Possible functional equivalent is only a suggestion for a qualified reviewer.",
            "Missing evidence remains unknown and may require review.",
            "Dimension roles can be ambiguous when source text gives unlabelled measurements.",
            "Pressure Class, PN and physical pressure use different bases and are not equated.",
            "The repository has a Python/CLI interface but no backend service or comparison-workspace screen.",
        ],
    }
    for name, value in (("report.json", report), ("examples.json", examples)):
        with (output / name).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
    if {str(records_path): _sha(records_path), str(candidates_path): _sha(candidates_path)} != before:
        raise ValueError("A frozen input changed during Phase 5 generation")
    artifacts = {path.name: _sha(path) for path in output.iterdir()}
    with (output / "manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump({"status": "complete", "artifacts": artifacts}, stream, indent=2)
        stream.write("\n")
    return report, examples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", default="output/phase3-v0.1/material_attributes.jsonl")
    parser.add_argument("--candidates", default="output/phase4-v0.1/candidates.jsonl")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    try:
        report, _ = generate(args.records, args.candidates, args.output_dir)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Phase 5 failed: {exc}\n")
    print(json.dumps({"pairs": report["pair_results"],
                      "runtime_seconds": report["runtime_seconds"],
                      "outcome_rule_counts": report["outcome_rule_counts"]}))


if __name__ == "__main__":
    main()
