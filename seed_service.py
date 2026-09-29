"""Create and seed one owned service workspace from frozen project evidence."""
import argparse
import os
from pathlib import Path

from prototype_registry import load_phase3_records
from integration_adapter import adapt_csv
from load_corpus import read_mapping
from service_storage import LocalWorkspaceStorage, PostgresWorkspaceStorage


DEFAULT_RECORDS = "output/phase3-v0.1/material_attributes.jsonl"


def load_seed_records(path=DEFAULT_RECORDS):
    """Load the frozen pack, or reproducibly rebuild it from committed candidates."""
    requested = Path(path)
    if requested.is_file():
        return load_phase3_records(requested)
    if requested.as_posix() != DEFAULT_RECORDS:
        raise FileNotFoundError(requested)
    root = Path(__file__).resolve().parent
    result = adapt_csv(root / "data/processed/material_candidates.csv",
                       read_mapping(root / "examples/phase2/candidates/mapping.json"),
                       import_root=root)
    return result["matching_records"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--owner-subject", required=True,
                        help="Exact managed-auth sub claim that owns the workspace")
    parser.add_argument("--public-read", action="store_true")
    parser.add_argument("--records", default=DEFAULT_RECORDS)
    parser.add_argument("--review-sample", default="reports/phase6/review_sample.csv")
    parser.add_argument("--error-log", default="reports/phase6/error_log.csv")
    parser.add_argument("--backend", choices=("sqlite", "postgres"),
                        default=os.getenv("SAMANVAY_STORAGE_BACKEND", "sqlite"))
    parser.add_argument("--local-dir", default=os.getenv("SAMANVAY_LOCAL_STORAGE_DIR",
                                                         ".local/samanvay-service"))
    args = parser.parse_args()
    storage = (PostgresWorkspaceStorage(os.environ.get("DATABASE_URL")) if args.backend == "postgres"
               else LocalWorkspaceStorage(args.local_dir))
    storage.create_workspace(args.workspace, args.owner_subject, public_read=args.public_read)
    with storage.open_workspace(args.workspace, args.owner_subject, write=True) as store:
        records = store.import_records(load_seed_records(args.records))
        warnings = store.import_phase6_warnings(args.review_sample, args.error_log)
    print({"workspace": args.workspace, "records_inserted": records,
           "warnings_inserted": warnings, "public_read": args.public_read,
           "owner_subject": args.owner_subject, "backend": storage.backend_name})


if __name__ == "__main__":
    main()
