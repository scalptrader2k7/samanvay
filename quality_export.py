"""Deterministic Phase 11 current-state quality export pack."""
from datetime import datetime, timezone
from io import BytesIO
import json
import re
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from openpyxl import Workbook


FIXED_TIME = datetime(2000, 1, 1, tzinfo=timezone.utc)


def registry_export_rows(store):
    rows = []
    codes = [row[0] for row in store.connection.execute(
        "SELECT proposed_code FROM registry_entries ORDER BY proposed_code")]
    for code in codes:
        entry = store.get_registry(code)
        members = sorted(entry["members"], key=lambda item: item["source_record_id"])
        rows.append({
            "proposed_code": entry["proposed_code"],
            "prototype_status": entry["prototype_status"],
            "active": bool(entry["active"]),
            "readable_description": entry["readable_description"],
            "standard_description": entry["standard_description"],
            "member_count": len(members),
            "member_source_ids": [item["source_record_id"] for item in members],
            "created_at": entry["created_at"],
            "updated_at": entry["updated_at"],
        })
    return rows


def _cell(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"))
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]",
                      lambda match: f"\\u{ord(match.group(0)):04x}", value)
    return value


def _sheet(workbook, title, rows, fields):
    sheet = workbook.create_sheet(title)
    sheet.append(fields)
    for row in rows:
        sheet.append([_cell(row.get(field)) for field in fields])
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    return sheet


def _normalized_zip(payload):
    source, target = BytesIO(payload), BytesIO()
    with ZipFile(source, "r") as incoming, ZipFile(
            target, "w", compression=ZIP_DEFLATED, compresslevel=9) as outgoing:
        for item in sorted(incoming.infolist(), key=lambda value: value.filename):
            info = ZipInfo(item.filename, (2000, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = item.external_attr
            info.create_system = item.create_system
            data = incoming.read(item.filename)
            if item.filename == "docProps/core.xml":
                data = re.sub(
                    br'<dcterms:modified([^>]*)>[^<]*</dcterms:modified>',
                    br'<dcterms:modified\1>2000-01-01T00:00:00Z</dcterms:modified>',
                    data)
            outgoing.writestr(info, data)
    return target.getvalue()


def build_quality_workbook(store):
    dashboard = store.quality_dashboard()
    registry = registry_export_rows(store)
    mappings = store.migration_rows()
    workbook = Workbook()
    workbook.remove(workbook.active)
    workbook.properties.title = "Samanvay quality export pack"
    workbook.properties.subject = "Current persisted workspace state"
    workbook.properties.creator = "Samanvay"
    workbook.properties.created = FIXED_TIME
    workbook.properties.modified = FIXED_TIME

    manifest = [
        {"field": "workspace_id", "value": dashboard["workspace_id"]},
        {"field": "schema_version", "value": dashboard["schema_version"]},
        {"field": "workspace_state_sha256", "value": dashboard["workspace_state_sha256"]},
        {"field": "scope", "value": "current persisted registry and mappings"},
        {"field": "history_included", "value": False},
        {"field": "financial_metrics", "value": "unsupported; no savings claims"},
        {"field": "excel_control_character_policy",
         "value": "OpenXML-illegal controls are preserved as explicit Unicode escape text"},
    ]
    _sheet(workbook, "Manifest", manifest, ["field", "value"])
    summary = [
        {"metric": "loaded_records", "value": dashboard["records"]["loaded"]},
        {"metric": "mapped_records", "value": dashboard["mapping_coverage"]["mapped"]},
        {"metric": "unresolved_records", "value": dashboard["mapping_coverage"]["unresolved"]},
        {"metric": "pending_deferred_reviews", "value": dashboard["reviews"]["deferred_pending"]},
        {"metric": "active_registry_entries", "value": dashboard["registry"]["active_prototype_entries"]},
        {"metric": "conflict_numerator", "value": dashboard["conflict_rate"]["numerator"]},
        {"metric": "conflict_denominator", "value": dashboard["conflict_rate"]["denominator"]},
    ]
    _sheet(workbook, "Dashboard", summary, ["metric", "value"])
    completeness = [{"field": name, **values}
                    for name, values in sorted(dashboard["completeness"].items())]
    _sheet(workbook, "Completeness", completeness,
           ["field", "present", "missing", "unknown", "total"])
    _sheet(workbook, "Registry", registry, [
        "proposed_code", "prototype_status", "active", "readable_description",
        "standard_description", "member_count", "member_source_ids", "created_at", "updated_at"])
    _sheet(workbook, "Current Mappings", mappings, [
        "source_record_id", "source_record_id_role", "source_organization",
        "original_description", "source_identifiers", "genuine_material_codes",
        "missing_genuine_material_code", "mapping_status", "proposed_samanvay_code",
        "prototype_status", "review_warnings"])
    buffer = BytesIO()
    workbook.save(buffer)
    return _normalized_zip(buffer.getvalue())
