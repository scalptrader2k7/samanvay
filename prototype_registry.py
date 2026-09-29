"""Persistent prototype common-material registry for Phase 7."""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
import csv

from itertools import combinations

from pair_evidence import COMPARISON_VERSION, compare_pair


REGISTRY_VERSION = "prototype-registry-v0.1"
PROTOTYPE_STATUS = "prototype_proposed"
ATTRIBUTE_FIELDS = ("size_dimension", "material_grade", "standard", "pressure", "voltage", "model_part")
GENUINE_MATERIAL_CODE_FIELDS = frozenset({
    "material_code", "cpse_material_code", "legacy_material_code", "sap_material_code"
})


class RegistrySafetyError(ValueError):
    def __init__(self, message, checks):
        super().__init__(message)
        self.checks = checks


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_phase3_records(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


def genuine_material_codes(record):
    return {key: value for key, value in record.get("source_identifiers", {}).items()
            if key.casefold() in GENUINE_MATERIAL_CODE_FIELDS and isinstance(value, str) and value.strip()}


def _evidence_copy(item, source_id):
    return {"source_record_id": source_id, "value_raw": item["value_raw"],
            "value_normalized": item["value_normalized"], "start": item["start"],
            "end": item["end"], "rule_id": item["rule_id"]}


def build_standard_description(records):
    """Use only values explicitly and compatibly present across every member."""
    if not records:
        raise ValueError("At least one source record is required")
    families = {record.get("family") for record in records if record.get("family")}
    family_known = len(families) == 1 and all(record.get("family") for record in records)
    fields = {}
    family_evidence = []
    for record in records:
        if record.get("family_evidence"):
            family_evidence.append(_evidence_copy(record["family_evidence"], record["source_record_id"]))
    fields["family"] = {"status": "supported" if family_known else "unknown",
                        "values": sorted(families) if family_known else [],
                        "evidence": family_evidence}
    for field in ATTRIBUTE_FIELDS:
        per_record, evidence = [], []
        for record in records:
            items = record.get("attributes", {}).get(field, [])
            values = sorted({item["value_normalized"] for item in items})
            per_record.append(values)
            evidence.extend(_evidence_copy(item, record["source_record_id"]) for item in items)
        supported = bool(per_record[0]) and all(values == per_record[0] for values in per_record)
        fields[field] = {"status": "supported" if supported else "unknown",
                         "values": per_record[0] if supported else [], "evidence": evidence,
                         "observed_by_source": {record["source_record_id"]: values
                                                for record, values in zip(records, per_record)}}
    parts = []
    for name in ("family",) + ATTRIBUTE_FIELDS:
        item = fields[name]
        display = ", ".join(item["values"]) if item["status"] == "supported" else "UNKNOWN"
        parts.append(f"{name.upper()}={display}")
    return " | ".join(parts), {"registry_version": REGISTRY_VERSION, "fields": fields}


def build_readable_description(description_evidence):
    """Render supported values without assigning roles to ambiguous dimensions."""
    fields = description_evidence["fields"]
    clauses = []
    family = fields["family"]
    if family["status"] == "supported":
        clauses.append(family["values"][0].capitalize())
    else:
        clauses.append("Material family unknown")
    labels = {
        "size_dimension": "dimensions/specification values",
        "material_grade": "material grade",
        "standard": "standard",
        "pressure": "pressure designation",
        "voltage": "voltage",
        "model_part": "model/part",
    }
    unknown = []
    for field in ATTRIBUTE_FIELDS:
        item = fields[field]
        if item["status"] == "supported":
            clauses.append(f"{labels[field]} {', '.join(item['values'])}")
        else:
            unknown.append(labels[field])
    text = "; ".join(clauses) + "."
    if unknown:
        text += " Unknown: " + ", ".join(unknown) + "."
    return text


class RegistryStore:
    def __init__(self, database_path, *, workspace_id="standalone"):
        self.database_path = str(database_path)
        self.workspace_id = workspace_id
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self._create_schema()

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()

    @contextmanager
    def transaction(self):
        if self.connection.in_transaction:
            raise RuntimeError("Nested registry transactions are not supported")
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            yield
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def _create_schema(self):
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS source_records (
            source_record_id TEXT PRIMARY KEY,
            organization TEXT NOT NULL,
            original_description TEXT NOT NULL,
            normalized_description TEXT NOT NULL,
            family TEXT,
            source_identifiers_json TEXT NOT NULL,
            genuine_material_codes_json TEXT NOT NULL,
            record_json TEXT NOT NULL,
            imported_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS registry_entries (
            proposed_code TEXT PRIMARY KEY,
            prototype_status TEXT NOT NULL CHECK(prototype_status = 'prototype_proposed'),
            member_fingerprint TEXT NOT NULL UNIQUE,
            standard_description TEXT NOT NULL,
            readable_description TEXT NOT NULL,
            description_evidence_json TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS registry_members (
            proposed_code TEXT NOT NULL REFERENCES registry_entries(proposed_code),
            source_record_id TEXT NOT NULL REFERENCES source_records(source_record_id),
            membership_status TEXT NOT NULL DEFAULT 'active',
            added_at TEXT NOT NULL,
            PRIMARY KEY (proposed_code, source_record_id)
        );
        CREATE TABLE IF NOT EXISTS decisions (
            decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            member_ids_json TEXT NOT NULL,
            reason TEXT NOT NULL,
            actor TEXT NOT NULL,
            proposed_code TEXT,
            resulting_relationship_id INTEGER,
            supersedes_decision_id INTEGER REFERENCES decisions(decision_id),
            demonstration INTEGER NOT NULL DEFAULT 0 CHECK(demonstration IN (0,1)),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS functional_relationships (
            relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
            left_source_record_id TEXT NOT NULL REFERENCES source_records(source_record_id),
            right_source_record_id TEXT NOT NULL REFERENCES source_records(source_record_id),
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(left_source_record_id, right_source_record_id)
        );
        CREATE TABLE IF NOT EXISTS review_warnings (
            warning_id TEXT PRIMARY KEY,
            source_record_ids_json TEXT NOT NULL,
            category TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            provenance TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS service_requests (
            idempotency_key TEXT PRIMARY KEY,
            request_hash TEXT NOT NULL,
            response_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            action TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            affected_source_ids_json TEXT NOT NULL,
            actor TEXT NOT NULL,
            reason TEXT NOT NULL,
            input_versions_json TEXT NOT NULL,
            rule_versions_json TEXT NOT NULL,
            previous_state_json TEXT NOT NULL,
            resulting_state_json TEXT NOT NULL,
            decision_id INTEGER REFERENCES decisions(decision_id),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS mapping_change_history (
            mapping_change_id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id TEXT NOT NULL,
            source_record_id TEXT NOT NULL REFERENCES source_records(source_record_id),
            previous_status TEXT NOT NULL,
            previous_proposed_code TEXT,
            new_status TEXT NOT NULL,
            new_proposed_code TEXT,
            actor TEXT NOT NULL,
            reason TEXT NOT NULL,
            decision_id INTEGER REFERENCES decisions(decision_id),
            created_at TEXT NOT NULL
        );
        CREATE TRIGGER IF NOT EXISTS audit_events_no_update
            BEFORE UPDATE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit events are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS audit_events_no_delete
            BEFORE DELETE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit events are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS mapping_history_no_update
            BEFORE UPDATE ON mapping_change_history BEGIN SELECT RAISE(ABORT, 'mapping history is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS mapping_history_no_delete
            BEFORE DELETE ON mapping_change_history BEGIN SELECT RAISE(ABORT, 'mapping history is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS decisions_no_update
            BEFORE UPDATE ON decisions BEGIN SELECT RAISE(ABORT, 'decisions are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS decisions_no_delete
            BEFORE DELETE ON decisions BEGIN SELECT RAISE(ABORT, 'decisions are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS source_records_no_update
            BEFORE UPDATE ON source_records BEGIN SELECT RAISE(ABORT, 'source records are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS source_records_no_delete
            BEFORE DELETE ON source_records BEGIN SELECT RAISE(ABORT, 'source records are immutable'); END;
        """)
        columns = {row[1] for row in self.connection.execute("PRAGMA table_info(registry_entries)")}
        if "readable_description" not in columns:
            self.connection.execute(
                "ALTER TABLE registry_entries ADD COLUMN readable_description TEXT NOT NULL DEFAULT ''")
        self.connection.commit()

    def import_records(self, records):
        inserted = 0
        with self.transaction():
            for record in records:
                source_id = record["source_record_id"]
                serialized = json.dumps(record, ensure_ascii=False, sort_keys=True)
                existing = self.connection.execute(
                    "SELECT record_json FROM source_records WHERE source_record_id=?", (source_id,)).fetchone()
                if existing:
                    if existing["record_json"] != serialized:
                        raise ValueError(f"Source snapshot changed for {source_id}")
                    continue
                self.connection.execute("""
                    INSERT INTO source_records VALUES (?,?,?,?,?,?,?,?,?)
                """, (source_id, record["source_organization"], record["description_original"],
                      record["description_normalized"], record.get("family"),
                      json.dumps(record.get("source_identifiers", {}), ensure_ascii=False, sort_keys=True),
                      json.dumps(genuine_material_codes(record), ensure_ascii=False, sort_keys=True),
                      serialized, utc_now()))
                inserted += 1
        return inserted

    def get_source_record(self, source_id):
        row = self.connection.execute(
            "SELECT record_json FROM source_records WHERE source_record_id=?", (source_id,)).fetchone()
        if not row:
            raise KeyError(source_id)
        return json.loads(row["record_json"])

    def _new_code(self):
        while True:
            code = "SMV-P-" + secrets.token_hex(6).upper()
            if not self.connection.execute(
                    "SELECT 1 FROM registry_entries WHERE proposed_code=?", (code,)).fetchone():
                return code

    @staticmethod
    def member_fingerprint(member_ids):
        canonical = "\n".join(sorted(set(member_ids)))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def create_or_get_registry(self, member_ids):
        member_ids = sorted(set(member_ids))
        if not member_ids:
            raise ValueError("Registry membership cannot be empty")
        fingerprint = self.member_fingerprint(member_ids)
        existing = self.connection.execute(
            "SELECT proposed_code FROM registry_entries WHERE member_fingerprint=?", (fingerprint,)).fetchone()
        if existing:
            timestamp = utc_now()
            self.connection.execute(
                "UPDATE registry_entries SET active=1, updated_at=? WHERE proposed_code=?",
                (timestamp, existing["proposed_code"]))
            self.connection.execute(
                "UPDATE registry_members SET membership_status='active' WHERE proposed_code=?",
                (existing["proposed_code"],))
            return existing["proposed_code"], False
        overlaps = self.connection.execute("""
            SELECT DISTINCT m.source_record_id, m.proposed_code
            FROM registry_members m JOIN registry_entries e USING(proposed_code)
            WHERE m.membership_status='active' AND e.active=1
              AND m.source_record_id IN (%s)
        """ % ",".join("?" for _ in member_ids), member_ids).fetchall()
        if overlaps:
            raise RegistrySafetyError("A source record already belongs to another active prototype registry",
                                      [dict(row) for row in overlaps])
        records = [self.get_source_record(source_id) for source_id in member_ids]
        description, evidence = build_standard_description(records)
        readable = build_readable_description(evidence)
        code, timestamp = self._new_code(), utc_now()
        self.connection.execute("""
            INSERT INTO registry_entries VALUES (?,?,?,?,?,?,?,?,?)
        """, (code, PROTOTYPE_STATUS, fingerprint, description, readable,
              json.dumps(evidence, ensure_ascii=False, sort_keys=True), 1, timestamp, timestamp))
        for source_id in member_ids:
            self.connection.execute(
                "INSERT INTO registry_members VALUES (?,?,?,?)",
                (code, source_id, "active", timestamp))
        return code, True

    def import_phase6_warnings(self, review_sample_path, error_log_path):
        import csv
        with Path(review_sample_path).open(encoding="utf-8-sig", newline="") as stream:
            sample = {row["review_pair_id"]: row for row in csv.DictReader(stream)}
        inserted = 0
        with Path(error_log_path).open(encoding="utf-8", newline="") as stream, self.transaction():
            for warning in csv.DictReader(stream):
                pair = sample.get(warning["review_pair_id"])
                if not pair:
                    raise ValueError(f"Unknown Phase 6 review pair {warning['review_pair_id']}")
                source_ids = sorted((pair["left_source_record_id"], pair["right_source_record_id"]))
                result = self.connection.execute("""
                    INSERT OR IGNORE INTO review_warnings VALUES (?,?,?,?,?,?)
                """, (warning["error_id"], json.dumps(source_ids), warning["category"],
                      warning["suspected_issue"], warning["status"],
                      f"phase6_error_log:{warning['review_pair_id']}"))
                inserted += result.rowcount
        return inserted

    def warnings_for(self, member_ids):
        wanted = set(member_ids)
        warnings = []
        for row in self.connection.execute("SELECT * FROM review_warnings ORDER BY warning_id"):
            source_ids = json.loads(row["source_record_ids_json"])
            if wanted & set(source_ids):
                item = dict(row); item["source_record_ids"] = source_ids
                item.pop("source_record_ids_json")
                warnings.append(item)
        return warnings

    def check_identity_group(self, member_ids):
        member_ids = sorted(set(member_ids))
        if len(member_ids) < 2:
            raise ValueError("Identity approval requires at least two distinct source records")
        records = {source_id: self.get_source_record(source_id) for source_id in member_ids}
        checks, blocking = [], []
        for left_id, right_id in combinations(member_ids, 2):
            comparison = compare_pair(records[left_id], records[right_id])
            outcome = comparison["outcome"]
            check = {"left_source_record_id": left_id, "right_source_record_id": right_id,
                     "outcome": outcome["label"],
                     "evidence_disposition": outcome["evidence_disposition"],
                     "critical_conflicts": [item["reason_code"] for field in
                        ("size_dimension", "material_grade", "standard", "pressure", "voltage")
                        for item in comparison["field_comparisons"][field]["conflicts"]],
                     "review_required": outcome["review_required"]}
            if check["critical_conflicts"]:
                check["blocking_reason"] = "critical_conflict"
                blocking.append(check)
            elif (outcome["label"] == "no_match" and
                  outcome["evidence_disposition"] == "supported_incompatibility"):
                check["blocking_reason"] = "supported_family_incompatibility"
                blocking.append(check)
            elif outcome["label"] == "possible_functional_equivalent":
                check["blocking_reason"] = "functional_equivalence_is_not_identity"
                blocking.append(check)
            checks.append(check)
        if blocking:
            raise RegistrySafetyError("Identity group failed all-member safety checks", checks)
        return checks

    def _record_decision(self, action, relationship_type, member_ids, reason, actor,
                         *, proposed_code=None, relationship_id=None, supersedes=None,
                         demonstration=False):
        cursor = self.connection.execute("""
            INSERT INTO decisions
            (action, relationship_type, member_ids_json, reason, actor, proposed_code,
             resulting_relationship_id, supersedes_decision_id, demonstration, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (action, relationship_type, json.dumps(sorted(set(member_ids))), reason.strip(),
              actor.strip(), proposed_code, relationship_id, supersedes,
              int(bool(demonstration)), utc_now()))
        return cursor.lastrowid

    def _mapping_state(self, source_id):
        row = self.connection.execute("""
            SELECT m.proposed_code FROM registry_members m
            JOIN registry_entries e USING(proposed_code)
            WHERE m.source_record_id=? AND m.membership_status='active' AND e.active=1
            ORDER BY m.proposed_code
        """, (source_id,)).fetchone()
        return {"status": "mapped_to_prototype" if row else "unresolved",
                "proposed_code": row["proposed_code"] if row else None}

    def _governance_state(self, member_ids):
        member_ids = sorted(set(member_ids))
        relationships = [dict(row) for row in self.connection.execute("""
            SELECT relationship_id, left_source_record_id, right_source_record_id, status
            FROM functional_relationships
            WHERE left_source_record_id IN (%s) AND right_source_record_id IN (%s)
            ORDER BY relationship_id
        """ % (",".join("?" for _ in member_ids), ",".join("?" for _ in member_ids)),
            member_ids + member_ids)] if member_ids else []
        return {"mappings": {source_id: self._mapping_state(source_id)
                              for source_id in member_ids},
                "functional_relationships": relationships}

    def _version_evidence(self, member_ids):
        input_versions, normalization, parsers = [], set(), set()
        for source_id in sorted(set(member_ids)):
            record = self.get_source_record(source_id)
            input_versions.append({
                "source_record_id": source_id,
                "source_sha256": record.get("source_sha256"),
                "mapping_id": record.get("mapping_id"),
                "schema_version": record.get("schema_version"),
            })
            if record.get("normalization_version"):
                normalization.add(record["normalization_version"])
            if record.get("attribute_parser_version"):
                parsers.add(record["attribute_parser_version"])
        return input_versions, {
            "normalization_versions": sorted(normalization),
            "attribute_parser_versions": sorted(parsers),
            "pair_evidence_version": COMPARISON_VERSION,
            "registry_version": REGISTRY_VERSION,
            "model_version": None,
        }

    def _record_audit(self, event_type, action, relationship_type, member_ids, reason,
                      actor, decision_id, previous_state, resulting_state):
        input_versions, rule_versions = self._version_evidence(member_ids)
        timestamp = utc_now()
        cursor = self.connection.execute("""
            INSERT INTO audit_events
            (workspace_id,event_type,action,relationship_type,affected_source_ids_json,
             actor,reason,input_versions_json,rule_versions_json,previous_state_json,
             resulting_state_json,decision_id,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (self.workspace_id, event_type, action, relationship_type,
              json.dumps(sorted(set(member_ids))), actor.strip(), reason.strip(),
              json.dumps(input_versions, ensure_ascii=False, sort_keys=True),
              json.dumps(rule_versions, ensure_ascii=False, sort_keys=True),
              json.dumps(previous_state, ensure_ascii=False, sort_keys=True),
              json.dumps(resulting_state, ensure_ascii=False, sort_keys=True),
              decision_id, timestamp))
        for source_id in sorted(set(member_ids)):
            previous = previous_state["mappings"][source_id]
            resulting = resulting_state["mappings"][source_id]
            if previous != resulting:
                self.connection.execute("""
                    INSERT INTO mapping_change_history
                    (workspace_id,source_record_id,previous_status,previous_proposed_code,
                     new_status,new_proposed_code,actor,reason,decision_id,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (self.workspace_id, source_id, previous["status"],
                      previous["proposed_code"], resulting["status"],
                      resulting["proposed_code"], actor.strip(), reason.strip(),
                      decision_id, timestamp))
        return cursor.lastrowid

    def _decide(self, action, relationship_type, member_ids, reason, actor, *, supersedes=None,
                demonstration=False, previous_state=None, event_type=None):
        if action not in {"approve", "reject", "defer"}:
            raise ValueError("action must be approve, reject or defer")
        if relationship_type not in {"identity", "functional_equivalence"}:
            raise ValueError("relationship_type must be identity or functional_equivalence")
        member_ids = sorted(set(member_ids))
        if len(member_ids) < 2:
            raise ValueError("A decision requires at least two distinct records")
        if not reason.strip() or not actor.strip():
            raise ValueError("Decision reason and actor are required")
        for source_id in member_ids:
            self.get_source_record(source_id)
        previous_state = previous_state or self._governance_state(member_ids)
        code = relationship_id = None
        checks = []
        if action == "approve" and relationship_type == "identity":
            checks = self.check_identity_group(member_ids)
            code, _ = self.create_or_get_registry(member_ids)
        elif action == "approve" and relationship_type == "functional_equivalence":
            if len(member_ids) != 2:
                raise ValueError("Functional equivalence decisions require exactly two records")
            left_id, right_id = member_ids
            self.connection.execute("""
                INSERT INTO functional_relationships
                (left_source_record_id,right_source_record_id,status,created_at)
                VALUES (?,?,?,?)
                ON CONFLICT(left_source_record_id,right_source_record_id)
                DO UPDATE SET status='active'
            """, (left_id, right_id, "active", utc_now()))
            relationship_id = self.connection.execute("""
                SELECT relationship_id FROM functional_relationships
                WHERE left_source_record_id=? AND right_source_record_id=?
            """, (left_id, right_id)).fetchone()["relationship_id"]
        decision_id = self._record_decision(
            action, relationship_type, member_ids, reason, actor, proposed_code=code,
            relationship_id=relationship_id, supersedes=supersedes,
            demonstration=demonstration)
        resulting_state = self._governance_state(member_ids)
        audit_event_id = self._record_audit(
            event_type or ("decision_reconsidered" if supersedes else "decision_created"),
            action, relationship_type, member_ids, reason, actor, decision_id,
            previous_state, resulting_state)
        return {"decision_id": decision_id, "action": action,
                "relationship_type": relationship_type, "proposed_code": code,
                "functional_relationship_id": relationship_id,
                "member_ids": member_ids, "pair_checks": checks,
                "review_warnings": self.warnings_for(member_ids),
                "audit_event_id": audit_event_id,
                "demonstration": bool(demonstration)}

    def decide(self, action, relationship_type, member_ids, reason, actor, *, demonstration=False):
        with self.transaction():
            return self._decide(action, relationship_type, member_ids, reason, actor,
                                demonstration=demonstration)

    def reconsider(self, decision_id, new_action, reason, actor, *, demonstration=False):
        with self.transaction():
            prior = self.connection.execute(
                "SELECT * FROM decisions WHERE decision_id=?", (decision_id,)).fetchone()
            if not prior:
                raise KeyError(decision_id)
            if self.connection.execute(
                    "SELECT 1 FROM decisions WHERE supersedes_decision_id=?", (decision_id,)).fetchone():
                raise ValueError("Only the current decision can be reconsidered")
            member_ids = json.loads(prior["member_ids_json"])
            previous_state = self._governance_state(member_ids)
            if prior["action"] == "approve" and prior["relationship_type"] == "identity" and prior["proposed_code"]:
                self.connection.execute(
                    "UPDATE registry_entries SET active=0, updated_at=? WHERE proposed_code=?",
                    (utc_now(), prior["proposed_code"]))
                self.connection.execute(
                    "UPDATE registry_members SET membership_status='revoked' WHERE proposed_code=?",
                    (prior["proposed_code"],))
            if (prior["action"] == "approve" and
                    prior["relationship_type"] == "functional_equivalence" and
                    prior["resulting_relationship_id"]):
                self.connection.execute(
                    "UPDATE functional_relationships SET status='reconsidered' WHERE relationship_id=?",
                    (prior["resulting_relationship_id"],))
            return self._decide(new_action, prior["relationship_type"], member_ids,
                                reason, actor, supersedes=decision_id,
                                demonstration=demonstration, previous_state=previous_state,
                                event_type="decision_reconsidered")

    def _idempotent(self, key, request_hash, operation):
        if not key or len(key) > 128:
            raise ValueError("Idempotency key must be 1-128 characters")
        with self.transaction():
            prior = self.connection.execute(
                "SELECT request_hash, response_json FROM service_requests WHERE idempotency_key=?",
                (key,)).fetchone()
            if prior:
                if prior["request_hash"] != request_hash:
                    raise RegistrySafetyError("Idempotency key was already used for a different request", [])
                response = json.loads(prior["response_json"])
                response["idempotent_replay"] = True
                return response
            response = operation()
            stored = {**response, "idempotent_replay": False}
            self.connection.execute("INSERT INTO service_requests VALUES (?,?,?,?)",
                                    (key, request_hash, json.dumps(stored, ensure_ascii=False,
                                                                 sort_keys=True), utc_now()))
            return stored

    def decide_idempotent(self, key, request_hash, action, relationship_type,
                          member_ids, reason, actor, *, demonstration=False):
        return self._idempotent(key, request_hash, lambda: self._decide(
            action, relationship_type, member_ids, reason, actor,
            demonstration=demonstration))

    def reconsider_idempotent(self, key, request_hash, decision_id, new_action,
                              reason, actor, *, demonstration=False):
        def operation():
            prior = self.connection.execute(
                "SELECT * FROM decisions WHERE decision_id=?", (decision_id,)).fetchone()
            if not prior:
                raise KeyError(decision_id)
            if self.connection.execute(
                    "SELECT 1 FROM decisions WHERE supersedes_decision_id=?", (decision_id,)).fetchone():
                raise ValueError("Only the current decision can be reconsidered")
            member_ids = json.loads(prior["member_ids_json"])
            previous_state = self._governance_state(member_ids)
            if prior["action"] == "approve" and prior["relationship_type"] == "identity" and prior["proposed_code"]:
                self.connection.execute(
                    "UPDATE registry_entries SET active=0, updated_at=? WHERE proposed_code=?",
                    (utc_now(), prior["proposed_code"]))
                self.connection.execute(
                    "UPDATE registry_members SET membership_status='revoked' WHERE proposed_code=?",
                    (prior["proposed_code"],))
            if prior["action"] == "approve" and prior["relationship_type"] == "functional_equivalence" and prior["resulting_relationship_id"]:
                self.connection.execute(
                    "UPDATE functional_relationships SET status='reconsidered' WHERE relationship_id=?",
                    (prior["resulting_relationship_id"],))
            return self._decide(new_action, prior["relationship_type"], member_ids,
                                reason, actor, supersedes=decision_id,
                                demonstration=demonstration, previous_state=previous_state,
                                event_type="decision_reconsidered")
        return self._idempotent(key, request_hash, operation)

    def decision_history(self):
        superseded = {row[0] for row in self.connection.execute(
            "SELECT supersedes_decision_id FROM decisions WHERE supersedes_decision_id IS NOT NULL")}
        history = []
        for row in self.connection.execute("SELECT * FROM decisions ORDER BY decision_id"):
            item = dict(row); item["member_ids"] = json.loads(item.pop("member_ids_json"))
            item["is_current"] = item["decision_id"] not in superseded
            history.append(item)
        return history

    @staticmethod
    def _decode_audit_row(row):
        item = dict(row)
        for key in ("affected_source_ids", "input_versions", "rule_versions",
                    "previous_state", "resulting_state"):
            item[key] = json.loads(item.pop(key + "_json"))
        return item

    def audit_history(self, *, source_id=None, event_type=None):
        rows = []
        for row in self.connection.execute("SELECT * FROM audit_events ORDER BY event_id"):
            item = self._decode_audit_row(row)
            if source_id and source_id not in item["affected_source_ids"]:
                continue
            if event_type and item["event_type"] != event_type:
                continue
            rows.append(item)
        return rows

    def mapping_history(self, *, source_id=None, proposed_code=None):
        rows = []
        for row in self.connection.execute(
                "SELECT * FROM mapping_change_history ORDER BY mapping_change_id"):
            item = dict(row)
            if source_id and item["source_record_id"] != source_id:
                continue
            if proposed_code and proposed_code not in {
                    item["previous_proposed_code"], item["new_proposed_code"]}:
                continue
            rows.append(item)
        return rows

    def quality_dashboard(self):
        """Calculate Phase 11 metrics from persisted workspace state only."""
        records = [json.loads(row[0]) for row in self.connection.execute(
            "SELECT record_json FROM source_records ORDER BY source_record_id")]
        total = len(records)
        mapped_ids = {row[0] for row in self.connection.execute("""
            SELECT DISTINCT m.source_record_id FROM registry_members m
            JOIN registry_entries e USING(proposed_code)
            WHERE m.membership_status='active' AND e.active=1
        """)}
        active_entries = [dict(row) for row in self.connection.execute("""
            SELECT proposed_code FROM registry_entries WHERE active=1 ORDER BY proposed_code
        """)]
        cluster_sizes = [self.connection.execute("""
            SELECT COUNT(*) FROM registry_members
            WHERE proposed_code=? AND membership_status='active'
        """, (row["proposed_code"],)).fetchone()[0] for row in active_entries]
        functional_count = self.connection.execute(
            "SELECT COUNT(*) FROM functional_relationships WHERE status='active'").fetchone()[0]

        scalar_fields = {
            "source_organization": lambda r: r.get("source_organization"),
            "source_record_id": lambda r: r.get("source_record_id"),
            "description": lambda r: r.get("description_original"),
            "uom": lambda r: r.get("uom_original"),
            "category": lambda r: r.get("category_original"),
        }
        completeness = {}
        for name, getter in scalar_fields.items():
            present = sum(isinstance(getter(record), str) and bool(getter(record).strip())
                          for record in records)
            completeness[name] = {"present": present, "missing": total - present,
                                  "unknown": 0, "total": total}
        structured_present = structured_missing = structured_unknown = 0
        for record in records:
            attributes = record.get("attributes")
            if not isinstance(attributes, dict):
                structured_missing += 1
            elif record.get("family") or any(attributes.get(field) for field in ATTRIBUTE_FIELDS):
                structured_present += 1
            else:
                structured_unknown += 1
        completeness["structured_attributes"] = {
            "present": structured_present, "missing": structured_missing,
            "unknown": structured_unknown, "total": total}

        eligible = Counter("eligible" if record.get("eligible_for_processing") is True else
                           "ineligible" if record.get("eligible_for_processing") is False else
                           "unknown" for record in records)
        decisions = self.decision_history()
        current = [row for row in decisions if row["is_current"]]
        current_actions = Counter(row["action"] for row in current)
        pair_ids = set()
        for decision in current:
            pair_ids.update(combinations(sorted(set(decision["member_ids"])), 2))
        outcome_counts = Counter()
        for left_id, right_id in sorted(pair_ids):
            outcome = compare_pair(self.get_source_record(left_id),
                                   self.get_source_record(right_id))["outcome"]["label"]
            outcome_counts[outcome] += 1
        conflict_numerator = outcome_counts["conflict"]
        conflict_denominator = len(pair_ids)
        revoked_sources = {row[0] for row in self.connection.execute("""
            SELECT DISTINCT source_record_id FROM mapping_change_history
            WHERE previous_status='mapped_to_prototype' AND new_status='unresolved'
        """)}
        state_material = {
            "sources": [record["source_record_id"] for record in records],
            "mapped": sorted(mapped_ids),
            "active_codes": [row["proposed_code"] for row in active_entries],
            "current_decisions": [{"decision_id": row["decision_id"], "action": row["action"]}
                                  for row in current],
        }
        state_hash = hashlib.sha256(json.dumps(
            state_material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return {
            "schema_version": "quality-dashboard-v0.1",
            "workspace_id": self.workspace_id,
            "workspace_state_sha256": state_hash,
            "records": {"loaded": total, "status": {
                "eligible": eligible["eligible"], "ineligible": eligible["ineligible"],
                "unknown": eligible["unknown"]}},
            "completeness": completeness,
            "reviews": {
                "current_decisions": len(current),
                "approved": current_actions["approve"],
                "rejected": current_actions["reject"],
                "deferred_pending": current_actions["defer"],
                "reconsideration_events": sum(row["supersedes_decision_id"] is not None
                                               for row in decisions),
                "persisted_review_pairs": len(pair_ids),
                "pair_outcomes": dict(sorted(outcome_counts.items())),
            },
            "candidate_metrics": {
                "persisted_candidate_proposals": None,
                "status": "not_persisted",
                "explanation": "Candidate retrieval is generated on demand; no workspace-wide candidate count is claimed.",
                "active_registry_clusters": len(active_entries),
                "active_registry_cluster_sizes": cluster_sizes,
                "active_functional_relationships": functional_count,
            },
            "conflict_rate": {
                "numerator": conflict_numerator,
                "denominator": conflict_denominator,
                "rate": (conflict_numerator / conflict_denominator
                         if conflict_denominator else None),
                "scope": "unique unordered pairs represented by current persisted decisions",
                "metric_kind": "pair-evidence rule output; not accuracy",
            },
            "mapping_coverage": {
                "mapped": len(mapped_ids), "unresolved": total - len(mapped_ids),
                "total": total,
                "rate": (len(mapped_ids) / total if total else None),
                "historically_revoked_or_reconsidered_sources": len(revoked_sources),
            },
            "registry": {"active_prototype_entries": len(active_entries),
                         "active_mapped_members": sum(cluster_sizes)},
            "financial_metrics": {"status": "unsupported",
                                  "reason": "No persisted transaction price/quantity evidence supports savings or ROI claims."},
        }

    def migration_rows(self):
        rows = []
        for source in self.connection.execute("SELECT * FROM source_records ORDER BY source_record_id"):
            membership = self.connection.execute("""
                SELECT m.proposed_code FROM registry_members m
                JOIN registry_entries e USING(proposed_code)
                WHERE m.source_record_id=? AND m.membership_status='active' AND e.active=1
                ORDER BY m.proposed_code
            """, (source["source_record_id"],)).fetchall()
            codes = [row["proposed_code"] for row in membership]
            if len(codes) > 1:
                raise ValueError(f"Source record has multiple active prototype mappings: {source['source_record_id']}")
            genuine = json.loads(source["genuine_material_codes_json"])
            warnings = self.warnings_for([source["source_record_id"]])
            rows.append({
                "source_record_id": source["source_record_id"],
                "source_record_id_role": "internal_row_locator_not_official_material_code",
                "source_organization": source["organization"],
                "original_description": source["original_description"],
                "source_identifiers": json.loads(source["source_identifiers_json"]),
                "genuine_material_codes": genuine,
                "missing_genuine_material_code": not bool(genuine),
                "mapping_status": "mapped_to_prototype" if codes else "unresolved",
                "proposed_samanvay_code": codes[0] if codes else None,
                "prototype_status": PROTOTYPE_STATUS if codes else None,
                "review_warnings": warnings,
            })
        return rows

    def conflict_rows(self):
        rows = []
        for warning in self.connection.execute("SELECT * FROM review_warnings ORDER BY warning_id"):
            rows.append({"kind": "phase6_review_warning", "reference": warning["warning_id"],
                         "source_record_ids": json.loads(warning["source_record_ids_json"]),
                         "status": warning["status"], "reason": warning["message"],
                         "category": warning["category"]})
        for decision in self.decision_history():
            if decision["relationship_type"] == "identity" and decision["action"] == "reject":
                rows.append({"kind": "identity_rejection", "reference": str(decision["decision_id"]),
                             "source_record_ids": decision["member_ids"], "status": "rejected",
                             "reason": decision["reason"], "category": "explicit_review_decision"})
        return rows

    def migration_preview(self):
        rows = self.migration_rows()
        return {"registry_version": REGISTRY_VERSION, "prototype_status": PROTOTYPE_STATUS,
                "source_records": len(rows),
                "mapped_records": sum(row["mapping_status"] == "mapped_to_prototype" for row in rows),
                "unresolved_records": sum(row["mapping_status"] == "unresolved" for row in rows),
                "records_missing_genuine_material_code": sum(row["missing_genuine_material_code"] for row in rows),
                "active_prototype_codes": self.connection.execute(
                    "SELECT COUNT(*) FROM registry_entries WHERE active=1").fetchone()[0],
                "functional_relationships": self.connection.execute(
                    "SELECT COUNT(*) FROM functional_relationships WHERE status='active'").fetchone()[0],
                "conflicts_and_warnings": len(self.conflict_rows()),
                "storage_boundary": "SQLite local development only; Phase 8 requires durable mounted or managed storage.",
                "rows": rows}

    @staticmethod
    def _write_csv(path, rows, fields):
        with Path(path).open("x", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: (json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value)
                                 for key, value in row.items()})

    @staticmethod
    def _write_json(path, value):
        with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write("\n")

    def export(self, output_dir):
        output = Path(output_dir)
        if output.exists():
            raise FileExistsError(f"Output directory already exists: {output}")
        output.mkdir(parents=True, exist_ok=False)
        mappings = self.migration_rows()
        unresolved = [row for row in mappings if row["mapping_status"] == "unresolved"]
        conflicts = self.conflict_rows()
        registry = [self.get_registry(row["proposed_code"]) for row in self.connection.execute(
            "SELECT proposed_code FROM registry_entries ORDER BY proposed_code")]
        relationships = [dict(row) for row in self.connection.execute(
            "SELECT * FROM functional_relationships ORDER BY relationship_id")]
        history = self.decision_history()
        preview = self.migration_preview(); preview.pop("rows")
        objects = {"registry.json": registry, "source_mappings.json": mappings,
                   "unresolved_records.json": unresolved, "conflicts.json": conflicts,
                   "functional_relationships.json": relationships,
                   "decision_history.json": history, "migration_preview.json": preview}
        for name, value in objects.items():
            self._write_json(output / name, value)
        mapping_fields = list(mappings[0]) if mappings else [
            "source_record_id", "source_record_id_role", "source_organization",
            "original_description", "source_identifiers", "genuine_material_codes",
            "missing_genuine_material_code", "mapping_status", "proposed_samanvay_code",
            "prototype_status", "review_warnings"]
        self._write_csv(output / "source_mappings.csv", mappings, mapping_fields)
        self._write_csv(output / "unresolved_records.csv", unresolved, mapping_fields)
        conflict_fields = ["kind", "reference", "source_record_ids", "status", "reason", "category"]
        self._write_csv(output / "conflicts.csv", conflicts, conflict_fields)
        artifacts = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in output.iterdir()}
        self._write_json(output / "manifest.json", {
            "registry_version": REGISTRY_VERSION, "prototype_status": PROTOTYPE_STATUS,
            "artifacts": artifacts})
        return preview

    def get_registry(self, proposed_code):
        entry = self.connection.execute(
            "SELECT * FROM registry_entries WHERE proposed_code=?", (proposed_code,)).fetchone()
        if not entry:
            raise KeyError(proposed_code)
        result = dict(entry)
        result["description_evidence"] = json.loads(result.pop("description_evidence_json"))
        result["members"] = [dict(row) for row in self.connection.execute("""
            SELECT m.source_record_id, m.membership_status, s.organization,
                   s.original_description, s.source_identifiers_json,
                   s.genuine_material_codes_json
            FROM registry_members m JOIN source_records s USING(source_record_id)
            WHERE m.proposed_code=? ORDER BY m.source_record_id
        """, (proposed_code,))]
        for member in result["members"]:
            member["source_identifiers"] = json.loads(member.pop("source_identifiers_json"))
            member["genuine_material_codes"] = json.loads(member.pop("genuine_material_codes_json"))
        return result
