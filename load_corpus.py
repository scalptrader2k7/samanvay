"""Read fixed or explicitly mapped CSV inputs without writing any files."""

from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path


CORPUS_COLUMNS = {
    "source_organization": "organization",
    "source_record_id": "corpus_id",
    "description_original": "description",
    "uom_original": "unit",
    "category_original": "product_category",
    "source_system": "source_system",
    "source_section": "source_section",
    "source_url": "source_url",
    "document_reference": "document_url",
    "quantity_original": "quantity",
}
IDENTIFIER_COLUMNS = ("corpus_id", "tender_reference", "tender_id")
SCALAR_FIELDS = (*CORPUS_COLUMNS, "legacy_material_code")


def validate_mapping(mapping):
    """Validate an explicit mapping; never guess columns or resolve conflicts."""
    allowed = {"mapping_id", "columns", "identifiers", "specifications",
               "organization_constant", "legacy_code_evidence"}
    if not isinstance(mapping, dict) or set(mapping) - allowed:
        raise ValueError("Mapping must be an object with known keys")
    if not isinstance(mapping.get("mapping_id"), str) or not mapping["mapping_id"].strip():
        raise ValueError("Mapping requires a nonblank versioned mapping_id")
    columns = mapping.get("columns")
    if not isinstance(columns, dict) or set(columns) - set(SCALAR_FIELDS):
        raise ValueError("Mapping columns must use known scalar fields")
    if any(not isinstance(v, str) or not v.strip() for v in columns.values()):
        raise ValueError("Each mapped column must be one nonblank header")
    if len(set(columns.values())) != len(columns):
        raise ValueError("Ambiguous mapping: a column maps to multiple scalar fields")
    for key in ("identifiers", "specifications"):
        values = mapping.get(key, [])
        if (not isinstance(values, (list, tuple)) or
                any(not isinstance(v, str) or not v.strip() for v in values) or
                len(values) != len(set(values))):
            raise ValueError(f"{key} must contain distinct nonblank column names")
    if set(mapping.get("specifications", [])) & (set(columns.values()) | set(mapping.get("identifiers", []))):
        raise ValueError("Ambiguous specification mapping")
    constant = mapping.get("organization_constant")
    if constant is not None:
        if (not isinstance(constant, dict) or set(constant) != {"value", "evidence"} or
                any(not isinstance(v, str) or not v.strip() for v in constant.values()) or
                "source_organization" in columns):
            raise ValueError("Organization constant needs value/evidence and cannot override a column")
    if "legacy_material_code" in columns:
        evidence = mapping.get("legacy_code_evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError("A legacy code mapping requires legacy_code_evidence")


def load_mapped_csv(path, mapping, *, import_root=None):
    """Load UTF-8 CSV using an explicit mapping object (no column inference)."""
    validate_mapping(mapping)
    constant = mapping.get("organization_constant")
    return _load_csv(path, import_root, mapping["columns"], mapping.get("identifiers", []),
                     mapping["mapping_id"],
                     (constant["value"], constant["evidence"]) if constant else None,
                     mapping.get("specifications", []), mapping.get("legacy_code_evidence"))


def read_mapping(path):
    """Read a JSON mapping, rejecting duplicate keys rather than overwriting them."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate mapping key: {key}")
            result[key] = value
        return result
    mapping = json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique)
    validate_mapping(mapping)
    return mapping


def load_candidates_csv(path, *, import_root=None):
    """Load the provisional subset; heuristic fields stay in raw_fields only."""
    return _load_csv(path, import_root,
                     {k: v for k, v in CORPUS_COLUMNS.items() if k not in ("source_system", "source_section")},
                     IDENTIFIER_COLUMNS, "material-candidates-v0.1")


def load_corpus_csv(path, *, import_root=None):
    """Load the fixed raw-corpus profile, preserving original source values."""
    return _load_csv(path, import_root, CORPUS_COLUMNS, IDENTIFIER_COLUMNS,
                     "raw-corpus-v0.1")


def load_ntpc_csv(path, *, import_root=None):
    """Load known NTPC extracted items; organization is profile metadata."""
    return _load_csv(path, import_root, {
        "description_original": "item_text", "uom_original": "unit",
        "document_reference": "doc_name", "quantity_original": "quantity",
    }, ("nit_id", "doc_name", "line_no"), "raw-ntpc-v0.1",
        ("NTPC Limited", "SOURCES.md section 2.2"))


def load_iocl_csv(path, *, import_root=None):
    """Load known IOCL plan items; organization is profile metadata."""
    return _load_csv(path, import_root, {
        "description_original": "item_description", "uom_original": "unit",
        "source_section": "section", "document_reference": "source_pdf",
        "quantity_original": "quantity",
    }, ("source_pdf", "page", "sl_no"), "raw-iocl-v0.1",
        ("Indian Oil Corporation Limited", "SOURCES.md section 2.3"))


def _load_csv(path, import_root, columns, identifier_columns, mapping_id,
              organization_constant=None, specification_columns=(), legacy_code_evidence=None):
    """Return all records, or raise ValueError for an invalid CSV/profile.

    Paths are resolved relative to the caller's working directory. import_root
    defaults to the file's parent; source_file is relative to that root.
    Read/hash one byte snapshot so provenance describes exactly the parsed data.
    No records are returned before the entire input passes structural validation.
    """
    path = Path(path).resolve()
    root = Path(import_root).resolve() if import_root is not None else path.parent
    try:
        source_file = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("Input file must be inside import_root") from exc
    snapshot = path.read_bytes()
    digest = hashlib.sha256(snapshot).hexdigest()
    try:
        text = snapshot.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{source_file}: expected UTF-8 CSV") from exc

    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    rows = []
    try:
        headers = next(reader, None)
        if not headers or any(not h.strip() for h in headers):
            raise ValueError(f"{source_file}: missing or empty headers")
        if len(headers) != len(set(headers)):
            raise ValueError(f"{source_file}: duplicate headers")
        missing = (set(columns.values()) | set(identifier_columns) | set(specification_columns)) - set(headers)
        if missing:
            raise ValueError(f"{source_file}: missing mapped columns: {', '.join(sorted(missing))}")
        for ordinal, cells in enumerate(reader, 1):
            if len(cells) != len(headers):
                raise ValueError(f"{source_file}: data record {ordinal}: wrong CSV row width")
            rows.append(dict(zip(headers, cells)))
    except csv.Error as exc:
        raise ValueError(f"{source_file}: malformed CSV near physical line {reader.line_num}: {exc}") from exc

    return _map_rows(rows, source_file, digest, columns, identifier_columns, mapping_id,
                     organization_constant, specification_columns, legacy_code_evidence)


def _map_rows(rows, source_file, digest, columns, identifier_columns, mapping_id,
              organization_constant=None, specification_columns=(), legacy_code_evidence=None):
    id_column = columns.get("source_record_id")
    id_counts = Counter(row[id_column] for row in rows if id_column and row[id_column].strip())
    records = []
    for ordinal, raw in enumerate(rows, 1):
        issues = []
        origins = {}
        record = {
            "schema_version": "0.1",
            "source_file": source_file,
            "source_sha256": digest,
            "source_sheet": None,
            "source_row": ordinal,
            "mapping_id": mapping_id,
            "raw_fields": raw,
            "field_origins": origins,
            "issues": issues,
        }
        for target in SCALAR_FIELDS:
            if target == "source_organization" and organization_constant:
                value, evidence = organization_constant
                record[target] = value
                origins[target] = {"kind": "constant", "value": value, "evidence": evidence}
                continue
            column = columns.get(target)
            value = raw[column] if column else ""
            record[target] = value if value.strip() else None
            origins[target] = {"kind": "column", "name": column} if column else {"kind": "unmapped"}
            if target == "legacy_material_code" and column:
                origins[target]["evidence"] = legacy_code_evidence
            if not value.strip():
                severity = "error" if target in ("source_organization", "description_original") else "warning"
                issues.append({"field": target, "reason": "blank" if column else "unmapped", "severity": severity})
        record["source_identifiers"] = {column: raw[column] for column in identifier_columns}
        origins["source_identifiers"] = {
            column: {"kind": "column", "name": column} for column in identifier_columns
        }
        for column in identifier_columns:
            if not raw[column].strip():
                issues.append({"field": f"source_identifiers.{column}", "reason": "blank", "severity": "warning"})
        record["specifications_original"] = {column: raw[column] for column in specification_columns}
        origins["specifications_original"] = {
            column: {"kind": "column", "name": column} for column in specification_columns
        }
        for column in specification_columns:
            if not raw[column].strip():
                issues.append({"field": f"specifications_original.{column}", "reason": "blank", "severity": "warning"})
        for target, mapped in (("source_identifiers", identifier_columns), ("specifications_original", specification_columns)):
            if not mapped:
                origins[target] = {"kind": "unmapped"}
                issues.append({"field": target, "reason": "unmapped", "severity": "warning"})
        if id_column and id_counts[raw[id_column]] > 1:
            issues.append({"field": "source_record_id", "reason": "duplicate", "severity": "warning"})
        record["eligible_for_processing"] = not any(issue["severity"] == "error" for issue in issues)
        records.append(record)
    return records
