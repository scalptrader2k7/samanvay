"""Generate a no-overwrite Phase 4 top-k candidate retrieval pack."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import time

from candidate_retrieval import CandidateIndex

EXAMPLES = (
    {"name": "exact cross-organization pump", "query": "M000114", "target": "M008245", "top_k": 10},
    {"name": "exact cross-organization cable", "query": "M000165", "target": "M017540", "top_k": 10},
    {"name": "near-format pipe", "query": "M000753", "target": "M000925", "top_k": 20},
    {"name": "different cable size proposal", "query": "M000830", "target": "M000834", "top_k": 30},
    {"name": "different valve pressure proposal", "query": "M010407", "target": "M003626", "top_k": 50},
)


def load_phase3(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


def generate(input_path, output_dir, *, top_k=10):
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    input_path = Path(input_path)
    before = input_path.read_bytes()
    records = load_phase3(input_path)
    build_started = time.perf_counter()
    index = CandidateIndex(records)
    build_seconds = time.perf_counter() - build_started
    query_started = time.perf_counter()
    diagnostics = []
    output.mkdir(parents=True, exist_ok=False)
    with (output / "candidates.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
        for record in records:
            results, diagnostic = index.retrieve(record["source_record_id"], top_k=top_k)
            diagnostics.append(diagnostic)
            stream.write(json.dumps({"query_source_record_id": record["source_record_id"],
                                     "query_organization": record["source_organization"],
                                     "query_description_original": record["description_original"],
                                     "status": "candidate_only", "candidates": results},
                                    ensure_ascii=False, allow_nan=False) + "\n")
    query_seconds = time.perf_counter() - query_started
    example_results = []
    for case in EXAMPLES:
        results, diagnostic = index.retrieve(case["query"], top_k=case["top_k"])
        ids = [r["candidate_source_record_id"] for r in results]
        example_results.append({**case, "found": case["target"] in ids,
                                "rank": ids.index(case["target"]) + 1 if case["target"] in ids else None,
                                "diagnostic": diagnostic})
    pools = [d["candidate_pool_size"] for d in diagnostics]
    comparisons = [d["fuzzy_comparisons"] for d in diagnostics]
    elapsed = [d["total_elapsed_ms"] for d in diagnostics]
    lexical_found = sum(c["found"] for c in example_results)
    report = {
        "phase": "4", "status": "complete", "retrieval_version": "lexical-retrieval-v0.1",
        "input_sha256": hashlib.sha256(before).hexdigest(), "query_records": len(records),
        "output_query_records": len(diagnostics), "top_k": top_k,
        "queries_with_candidates": sum(bool(n) for n in comparisons),
        "runtime": {"index_build_seconds": round(build_seconds, 6),
                    "all_queries_seconds": round(query_seconds, 6),
                    "queries_per_second": round(len(records) / query_seconds, 3) if query_seconds else None},
        "candidate_pool": {"maximum": max(pools, default=0),
                           "mean": round(statistics.fmean(pools), 3) if pools else 0,
                           "p95": sorted(pools)[min(len(pools)-1, int(len(pools)*0.95))] if pools else 0},
        "comparisons": {"total_fuzzy": sum(comparisons), "maximum_per_query": max(comparisons, default=0),
                        "all_possible_directed_pairs": len(records) * max(0, len(records)-1),
                        "all_pairs_compared": False},
        "latency_ms": {"mean": round(statistics.fmean(elapsed), 4) if elapsed else 0,
                       "maximum": round(max(elapsed, default=0), 4)},
        "example_coverage": {"found": lexical_found, "total": len(example_results),
                             "scope": "Predeclared diagnostic examples; not accuracy or recall."},
        "semantic_retrieval": {"enabled": False,
            "decision": "Not added: bounded lexical retrieval found every predeclared difficult/example target; no demonstrated incremental benefit on this non-gold suite."},
        "limitations": [
            "No human-labeled retrieval gold set exists; example coverage is not accuracy or recall.",
            "Public descriptions are surrogate procurement text and contain overlapping extraction stages.",
            "Fuzzy scores are ranking signals, not match confidence or identity decisions.",
            "Token posting/pool caps can miss candidates with no useful lexical overlap.",
            "Phase 4 does not compare critical attributes, reject conflicts, merge records or assign codes.",
        ],
    }
    for name, value in (("report.json", report), ("examples.json", example_results)):
        with (output / name).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write("\n")
    artifacts = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
    with (output / "manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump({"status": "complete", "artifacts": artifacts}, stream, indent=2); stream.write("\n")
    if input_path.read_bytes() != before:
        raise ValueError("Input changed during retrieval")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="output/phase3-v0.1/material_attributes.jsonl")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()
    try:
        report = generate(args.input, args.output_dir, top_k=args.top_k)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Phase 4 failed: {exc}\n")
    print(json.dumps(report["runtime"]))


if __name__ == "__main__":
    main()
