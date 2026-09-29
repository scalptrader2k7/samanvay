"""Compare one Phase 4 candidate pair and print its Phase 5 evidence as JSON."""
import argparse
import json
from pathlib import Path

from pair_evidence import compare_pair


def load_records(path):
    with Path(path).open(encoding="utf-8") as stream:
        return {record["source_record_id"]: record for record in map(json.loads, stream)}


def find_retrieval(path, query_id, candidate_id):
    if not path:
        return None
    with Path(path).open(encoding="utf-8") as stream:
        for line in stream:
            query = json.loads(line)
            if query["query_source_record_id"] != query_id:
                continue
            return next((item for item in query["candidates"]
                         if item["candidate_source_record_id"] == candidate_id), None)
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left_source_record_id")
    parser.add_argument("right_source_record_id")
    parser.add_argument("--records", default="output/phase3-v0.1/material_attributes.jsonl")
    parser.add_argument("--candidates", default="output/phase4-v0.1/candidates.jsonl")
    args = parser.parse_args()
    records = load_records(args.records)
    try:
        left, right = records[args.left_source_record_id], records[args.right_source_record_id]
    except KeyError as exc:
        parser.exit(1, f"Unknown source_record_id: {exc.args[0]}\n")
    retrieval = find_retrieval(args.candidates, args.left_source_record_id,
                               args.right_source_record_id)
    print(json.dumps(compare_pair(left, right, retrieval), ensure_ascii=False,
                     indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
