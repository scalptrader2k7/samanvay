"""Build a no-overwrite external-schema adapter pack; performs no ERP writes."""
import argparse

from integration_adapter import write_adapter_pack
from load_corpus import read_mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--mapping", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--import-root")
    args = parser.parse_args()
    try:
        report = write_adapter_pack(args.input, read_mapping(args.mapping),
                                    args.output_dir, import_root=args.import_root)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Adapter failed: {exc}\n")
    print({"canonical_records": report["canonical_records"],
           "matching_ready_records": report["matching_ready_records"],
           "output_dir": args.output_dir, "erp_writes": False})


if __name__ == "__main__":
    main()
