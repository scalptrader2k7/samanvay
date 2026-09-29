import json
from pathlib import Path
import tempfile
import csv
import unittest

from prototype_registry import (PROTOTYPE_STATUS, RegistrySafetyError, RegistryStore,
                                build_readable_description, build_standard_description,
                                load_phase3_records)

ROOT = Path(__file__).resolve().parents[1]


class Phase7RegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {r["source_record_id"]: r for r in load_phase3_records(
            ROOT / "output/phase3-v0.1/material_attributes.jsonl")}

    def test_standard_description_uses_supported_values_and_unknowns(self):
        description, evidence = build_standard_description(
            [self.records["M000753"], self.records["M000925"]])
        self.assertIn("FAMILY=pipe", description)
        self.assertIn("STANDARD=ASTM A312", description)
        self.assertIn("PRESSURE=UNKNOWN", description)
        for item in evidence["fields"]["standard"]["evidence"]:
            record = self.records[item["source_record_id"]]
            self.assertEqual(record["description_original"][item["start"]:item["end"]], item["value_raw"])
        readable = build_readable_description(evidence)
        self.assertIn("Pipe", readable)
        self.assertIn("dimensions/specification values 125NB, 141.3MM, 9.53MM", readable)
        self.assertIn("standard ASTM A312", readable)
        self.assertIn("Unknown: material grade", readable)
        self.assertNotIn("diameter", readable.casefold())

    def test_code_and_source_snapshot_survive_reload_and_repeat(self):
        with tempfile.TemporaryDirectory() as temp:
            database = Path(temp) / "registry.sqlite3"
            member_ids = ["M000753", "M000925"]
            with RegistryStore(database) as store:
                self.assertEqual(store.import_records([self.records[x] for x in member_ids]), 2)
                with store.transaction():
                    code, created = store.create_or_get_registry(member_ids)
                self.assertTrue(created)
                self.assertRegex(code, r"^SMV-P-[0-9A-F]{12}$")
                self.assertEqual(store.get_registry(code)["prototype_status"], PROTOTYPE_STATUS)
            with RegistryStore(database) as store:
                self.assertEqual(store.import_records([self.records[x] for x in member_ids]), 0)
                with store.transaction():
                    repeated, created = store.create_or_get_registry(reversed(member_ids))
                self.assertFalse(created)
                self.assertEqual(repeated, code)
                members = store.get_registry(code)["members"]
                self.assertEqual([x["source_record_id"] for x in members], sorted(member_ids))
                self.assertTrue(all(not x["genuine_material_codes"] for x in members))
                self.assertTrue(all("corpus_id" in x["source_identifiers"] for x in members))

    def test_changed_source_snapshot_is_rejected_atomically(self):
        with tempfile.TemporaryDirectory() as temp, RegistryStore(Path(temp) / "r.db") as store:
            record = self.records["M000114"]
            store.import_records([record])
            changed = dict(record); changed["description_original"] = "changed"
            with self.assertRaises(ValueError):
                store.import_records([changed])
            self.assertEqual(store.get_source_record("M000114")["description_original"], "Centrifugal Pump")

    def store(self, temp, ids):
        store = RegistryStore(Path(temp) / "registry.sqlite3")
        store.import_records([self.records[x] for x in ids])
        return store

    def test_explicit_approval_is_idempotent_and_reconsideration_keeps_history(self):
        ids = ["M000753", "M000925"]
        with tempfile.TemporaryDirectory() as temp, self.store(temp, ids) as store:
            first = store.decide("approve", "identity", ids, "Reviewed matching specifications", "demo-reviewer")
            repeated = store.decide("approve", "identity", reversed(ids), "Repeat reviewed action", "demo-reviewer")
            self.assertEqual(first["proposed_code"], repeated["proposed_code"])
            rejected = store.reconsider(first["decision_id"], "reject", "Second review reversed decision", "demo-reviewer")
            self.assertIsNone(rejected["proposed_code"])
            entry = store.get_registry(first["proposed_code"])
            self.assertEqual(entry["active"], 0)
            self.assertTrue(all(x["membership_status"] == "revoked" for x in entry["members"]))
            history = store.decision_history()
            self.assertEqual(len(history), 3)
            self.assertEqual(history[-1]["supersedes_decision_id"], first["decision_id"])

    def test_every_group_pair_is_checked_and_conflict_rolls_back(self):
        ids = ["M000753", "M000925", "M000913"]
        with tempfile.TemporaryDirectory() as temp, self.store(temp, ids) as store:
            with self.assertRaises(RegistrySafetyError) as caught:
                store.decide("approve", "identity", ids, "Proposed three-member group", "demo-reviewer")
            checked = {(x["left_source_record_id"], x["right_source_record_id"])
                       for x in caught.exception.checks}
            self.assertEqual(len(checked), 3)
            self.assertTrue(any(x.get("blocking_reason") == "critical_conflict"
                                for x in caught.exception.checks))
            self.assertEqual(store.connection.execute("SELECT COUNT(*) FROM registry_entries").fetchone()[0], 0)
            self.assertEqual(store.connection.execute("SELECT COUNT(*) FROM decisions").fetchone()[0], 0)

    def test_functional_equivalence_is_separate_and_creates_no_registry(self):
        ids = ["M000041", "M000114"]
        with tempfile.TemporaryDirectory() as temp, self.store(temp, ids) as store:
            with self.assertRaises(RegistrySafetyError):
                store.decide("approve", "identity", ids, "Identity proposal", "demo-reviewer")
            result = store.decide("approve", "functional_equivalence", ids,
                                  "Qualified reviewer relationship suggestion", "demo-reviewer")
            self.assertIsNone(result["proposed_code"])
            self.assertIsNotNone(result["functional_relationship_id"])
            self.assertEqual(store.connection.execute("SELECT COUNT(*) FROM registry_entries").fetchone()[0], 0)

    def test_source_cannot_join_two_active_identity_registries(self):
        ids = ["M000114", "M008245", "M005047"]
        with tempfile.TemporaryDirectory() as temp, self.store(temp, ids) as store:
            with store.transaction():
                store.create_or_get_registry(ids[:2])
            with self.assertRaises(RegistrySafetyError):
                with store.transaction():
                    store.create_or_get_registry([ids[0], ids[2]])
            self.assertEqual(store.connection.execute(
                "SELECT COUNT(*) FROM registry_entries").fetchone()[0], 1)

    def test_reject_defer_and_phase6_warnings_are_recorded_without_membership(self):
        ids = ["M000830", "M000834"]
        with tempfile.TemporaryDirectory() as temp, self.store(temp, ids) as store:
            inserted = store.import_phase6_warnings(
                ROOT / "reports/phase6/review_sample.csv", ROOT / "reports/phase6/error_log.csv")
            self.assertEqual(inserted, 10)
            store.decide("reject", "identity", ids, "Critical cable area conflict", "demo-reviewer")
            store.decide("defer", "identity", ids, "Await engineering review", "demo-reviewer")
            self.assertEqual(store.connection.execute("SELECT COUNT(*) FROM registry_entries").fetchone()[0], 0)
            self.assertEqual(len(store.decision_history()), 2)

    def test_migration_preview_and_exports_preserve_originals_and_missing_codes(self):
        ids = ["M000753", "M000925", "M000830", "M000834"]
        with tempfile.TemporaryDirectory() as temp, self.store(temp, ids) as store:
            approved = store.decide("approve", "identity", ids[:2],
                                     "Reviewed identical specifications", "demo-reviewer")
            store.decide("reject", "identity", ids[2:], "Different cable areas", "demo-reviewer")
            preview = store.migration_preview()
            self.assertEqual(preview["source_records"], 4)
            self.assertEqual(preview["mapped_records"], 2)
            self.assertEqual(preview["unresolved_records"], 2)
            self.assertEqual(preview["records_missing_genuine_material_code"], 4)
            output = Path(temp) / "export"
            store.export(output)
            with (output / "source_mappings.csv").open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            mapped = [row for row in rows if row["mapping_status"] == "mapped_to_prototype"]
            self.assertEqual({row["proposed_samanvay_code"] for row in mapped},
                             {approved["proposed_code"]})
            self.assertTrue(all(row["source_record_id_role"] ==
                                "internal_row_locator_not_official_material_code" for row in rows))
            self.assertTrue(all(row["missing_genuine_material_code"] == "True" for row in rows))
            self.assertTrue((output / "conflicts.json").exists())
            self.assertTrue((output / "unresolved_records.json").exists())
            with self.assertRaises(FileExistsError):
                store.export(output)


if __name__ == "__main__":
    unittest.main()
