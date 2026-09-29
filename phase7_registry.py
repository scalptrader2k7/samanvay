"""CLI for the Phase 7 local prototype registry."""
import argparse
import json

from prototype_registry import RegistrySafetyError, RegistryStore, load_phase3_records


def open_store(path):
    return RegistryStore(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="Local SQLite development database")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--records", default="output/phase3-v0.1/material_attributes.jsonl")
    init.add_argument("--review-sample", default="reports/phase6/review_sample.csv")
    init.add_argument("--error-log", default="reports/phase6/error_log.csv")
    decide = sub.add_parser("decide")
    decide.add_argument("action", choices=("approve", "reject", "defer"))
    decide.add_argument("relationship", choices=("identity", "functional_equivalence"))
    decide.add_argument("members", nargs="+")
    decide.add_argument("--reason", required=True); decide.add_argument("--actor", required=True)
    decide.add_argument("--demonstration", action="store_true")
    reconsider = sub.add_parser("reconsider")
    reconsider.add_argument("decision_id", type=int)
    reconsider.add_argument("action", choices=("approve", "reject", "defer"))
    reconsider.add_argument("--reason", required=True); reconsider.add_argument("--actor", required=True)
    reconsider.add_argument("--demonstration", action="store_true")
    show = sub.add_parser("show"); show.add_argument("proposed_code")
    sub.add_parser("history")
    preview = sub.add_parser("preview"); preview.add_argument("--include-rows", action="store_true")
    export = sub.add_parser("export"); export.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    try:
        with open_store(args.db) as store:
            if args.command == "init":
                inserted = store.import_records(load_phase3_records(args.records))
                warnings = store.import_phase6_warnings(args.review_sample, args.error_log)
                result = {"records_inserted": inserted, "warnings_inserted": warnings,
                          "storage": "SQLite local development; durable storage required for Phase 8 deployment."}
            elif args.command == "decide":
                result = store.decide(args.action, args.relationship, args.members,
                                      args.reason, args.actor, demonstration=args.demonstration)
            elif args.command == "reconsider":
                result = store.reconsider(args.decision_id, args.action, args.reason,
                                          args.actor, demonstration=args.demonstration)
            elif args.command == "show":
                result = store.get_registry(args.proposed_code)
            elif args.command == "history":
                result = store.decision_history()
            elif args.command == "preview":
                result = store.migration_preview()
                if not args.include_rows:
                    result.pop("rows")
            else:
                result = store.export(args.output_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except RegistrySafetyError as exc:
        parser.exit(2, json.dumps({"error": str(exc), "pair_checks": exc.checks}, indent=2) + "\n")
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f"Phase 7 registry failed: {exc}\n")


if __name__ == "__main__":
    main()
