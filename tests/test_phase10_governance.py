from pathlib import Path
import hashlib
import json
import tempfile
import unittest

from prototype_registry import RegistrySafetyError, load_phase3_records
from service_storage import LocalWorkspaceStorage


ROOT = Path(__file__).resolve().parents[1]


class Phase10GovernanceStorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records = {r["source_record_id"]: r for r in load_phase3_records(
            ROOT / "output/phase3-v0.1/material_attributes.jsonl")}
        cls.records = [records[x] for x in ("M000753", "M000925", "M000830", "M000834")]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.storage = LocalWorkspaceStorage(Path(self.temp.name) / "storage")
        self.storage.create_workspace("audit-demo", "owner-subject", public_read=True)
        with self.storage.open_workspace("audit-demo", "owner-subject", write=True) as store:
            store.import_records(self.records)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def source_digest(store):
        rows = [row[0] for row in store.connection.execute(
            "SELECT record_json FROM source_records ORDER BY source_record_id")]
        return hashlib.sha256("\n".join(rows).encode()).hexdigest()

    def test_approve_reconsider_persists_audit_versions_and_mapping_history(self):
        with self.storage.open_workspace("audit-demo", "owner-subject", write=True) as store:
            before = self.source_digest(store)
            first = store.decide("approve", "identity", ["M000753", "M000925"],
                                 "Supported pipe specifications", "owner-subject")
            second = store.reconsider(first["decision_id"], "reject",
                                      "Governance override after second review", "owner-subject")
            self.assertEqual(before, self.source_digest(store))
            audit = store.audit_history()
            self.assertEqual([x["event_type"] for x in audit],
                             ["decision_created", "decision_reconsidered"])
            self.assertEqual(audit[0]["workspace_id"], "audit-demo")
            self.assertEqual(audit[0]["actor"], "owner-subject")
            self.assertEqual(audit[0]["rule_versions"]["pair_evidence_version"],
                             "pair-evidence-v0.2")
            self.assertEqual(audit[0]["input_versions"][0]["mapping_id"],
                             "material-candidates-v0.1")
            self.assertEqual(len(store.mapping_history()), 4)
            self.assertTrue(all(x["new_status"] == "unresolved"
                                for x in store.mapping_history()[2:]))
            history = store.decision_history()
            self.assertFalse(history[0]["is_current"])
            self.assertTrue(history[1]["is_current"])
            self.assertEqual(second["audit_event_id"], audit[1]["event_id"])

        restarted = LocalWorkspaceStorage(self.storage.root)
        with restarted.open_workspace("audit-demo", "owner-subject") as store:
            self.assertEqual(len(store.audit_history()), 2)
            self.assertEqual(len(store.mapping_history(source_id="M000753")), 2)
            self.assertEqual(self.source_digest(store), before)
            self.assertEqual(store.migration_rows()[2]["mapping_status"], "unresolved")

    def test_audit_is_append_only_and_failed_transaction_leaves_no_event(self):
        with self.storage.open_workspace("audit-demo", "owner-subject", write=True) as store:
            with self.assertRaises(RegistrySafetyError):
                store.decide("approve", "identity", ["M000830", "M000834"],
                             "Deliberate conflicting fixture", "owner-subject")
            self.assertEqual(store.audit_history(), [])
            decision = store.decide("reject", "identity", ["M000830", "M000834"],
                                    "Supported cable area conflict", "owner-subject")
            with self.assertRaisesRegex(Exception, "append-only"):
                store.connection.execute("UPDATE audit_events SET reason='changed'")
            store.connection.rollback()
            with self.assertRaisesRegex(Exception, "append-only"):
                store.connection.execute("UPDATE decisions SET reason='changed'")
            store.connection.rollback()
            with self.assertRaisesRegex(Exception, "immutable"):
                store.connection.execute(
                    "UPDATE source_records SET original_description='changed' WHERE source_record_id='M000830'")
            store.connection.rollback()
            self.assertEqual(store.audit_history()[0]["decision_id"], decision["decision_id"])

    def test_filters_are_exact(self):
        with self.storage.open_workspace("audit-demo", "owner-subject", write=True) as store:
            store.decide("reject", "identity", ["M000830", "M000834"],
                         "Supported cable area conflict", "owner-subject")
            self.assertEqual(len(store.audit_history(source_id="M000830")), 1)
            self.assertEqual(store.audit_history(source_id="M000753"), [])
            self.assertEqual(len(store.audit_history(event_type="decision_created")), 1)
            self.assertEqual(store.mapping_history(), [])


if __name__ == "__main__":
    unittest.main()
