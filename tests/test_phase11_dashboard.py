from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from api_service import Settings, create_app
from prototype_registry import load_phase3_records
from service_storage import LocalWorkspaceStorage


ROOT = Path(__file__).resolve().parents[1]


class Phase11DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        all_records = {r["source_record_id"]: r for r in load_phase3_records(
            ROOT / "output/phase3-v0.1/material_attributes.jsonl")}
        cls.records = [all_records[x] for x in
                       ("M000753", "M000925", "M000830", "M000834")]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.storage = LocalWorkspaceStorage(Path(self.temp.name) / "storage")
        self.storage.create_workspace("quality-demo", "quality-owner", public_read=True)
        self.storage.create_workspace("quality-private", "other-owner", public_read=False)
        with self.storage.open_workspace("quality-demo", "quality-owner", write=True) as store:
            store.import_records(self.records)
            store.decide("approve", "identity", ["M000753", "M000925"],
                         "Supported matching pipe evidence", "quality-owner")
            store.decide("reject", "identity", ["M000830", "M000834"],
                         "Supported cable area conflict", "quality-owner")
        self.client = TestClient(create_app(settings=Settings(
            demo_token="quality-secret", demo_subject="quality-owner"), storage=self.storage))
        self.auth = {"Authorization": "Bearer quality-secret"}
        self.path = "/api/v1/workspaces/quality-demo/quality-dashboard"

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()

    def test_counts_completeness_conflict_and_mapping_reconcile(self):
        result = self.client.get(self.path).json()
        self.assertEqual(result["records"]["loaded"], 4)
        self.assertEqual(sum(result["records"]["status"].values()), 4)
        for field in result["completeness"].values():
            self.assertEqual(field["present"] + field["missing"] + field["unknown"], 4)
        self.assertEqual(result["reviews"]["current_decisions"], 2)
        self.assertEqual(result["reviews"]["approved"], 1)
        self.assertEqual(result["reviews"]["rejected"], 1)
        self.assertEqual(result["reviews"]["deferred_pending"], 0)
        self.assertEqual(result["conflict_rate"]["numerator"], 1)
        self.assertEqual(result["conflict_rate"]["denominator"], 2)
        self.assertEqual(result["conflict_rate"]["rate"], 0.5)
        self.assertEqual(result["mapping_coverage"], {
            "mapped": 2, "unresolved": 2, "total": 4, "rate": 0.5,
            "historically_revoked_or_reconsidered_sources": 0})
        self.assertIsNone(result["candidate_metrics"]["persisted_candidate_proposals"])
        self.assertEqual(result["financial_metrics"]["status"], "unsupported")

    def test_reconsideration_separates_current_and_historical_mapping(self):
        with self.storage.open_workspace("quality-demo", "quality-owner", write=True) as store:
            approval = next(x for x in store.decision_history()
                            if x["action"] == "approve")
            store.reconsider(approval["decision_id"], "defer",
                             "Needs an additional qualified review", "quality-owner")
        result = self.client.get(self.path).json()
        self.assertEqual(result["mapping_coverage"]["mapped"], 0)
        self.assertEqual(result["mapping_coverage"]["unresolved"], 4)
        self.assertEqual(result["mapping_coverage"]
                         ["historically_revoked_or_reconsidered_sources"], 2)
        self.assertEqual(result["reviews"]["deferred_pending"], 1)
        self.assertEqual(result["reviews"]["reconsideration_events"], 1)

    def test_workspace_access_and_stable_state_hash(self):
        first = self.client.get(self.path).json()
        second = self.client.get(self.path).json()
        self.assertEqual(first["workspace_state_sha256"], second["workspace_state_sha256"])
        denied = self.client.get(
            "/api/v1/workspaces/quality-private/quality-dashboard", headers=self.auth)
        self.assertEqual(denied.status_code, 403)

    def test_quality_interface_uses_authoritative_api_and_explains_exports(self):
        page = self.client.get("/").text
        script = self.client.get("/static/app.js").text
        for text in ("Quality dashboard", "Persisted-field completeness",
                     "Conflict rule output", "Reproducible exports",
                     "Current mappings", "Separate history"):
            self.assertIn(text, page)
        for text in ("/quality-dashboard", "financial_metrics.reason",
                     "conflict.numerator", "mapping_coverage"):
            self.assertIn(text, script)


if __name__ == "__main__":
    unittest.main()
