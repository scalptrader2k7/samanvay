from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from api_service import Settings, create_app
from prototype_registry import load_phase3_records
from service_storage import LocalWorkspaceStorage


ROOT = Path(__file__).resolve().parents[1]


class Phase10GovernanceApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        all_records = {r["source_record_id"]: r for r in load_phase3_records(
            ROOT / "output/phase3-v0.1/material_attributes.jsonl")}
        cls.records = [all_records[x] for x in ("M000753", "M000925", "M000830", "M000834")]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.storage = LocalWorkspaceStorage(Path(self.temp.name) / "storage")
        self.storage.create_workspace("audit-public", "fixture-owner", public_read=True)
        self.storage.create_workspace("audit-private", "different-owner", public_read=False)
        with self.storage.open_workspace("audit-public", "fixture-owner", write=True) as store:
            store.import_records(self.records)
        settings = Settings(demo_token="fixture-secret", demo_subject="fixture-owner")
        self.client = TestClient(create_app(settings=settings, storage=self.storage))
        self.auth = {"Authorization": "Bearer fixture-secret"}
        self.base = "/api/v1/workspaces/audit-public"

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()

    def approve(self, key="phase10-approve"):
        return self.client.post(f"{self.base}/decisions", headers={
            **self.auth, "Idempotency-Key": key}, json={
                "action": "approve", "relationship_type": "identity",
                "member_ids": ["M000753", "M000925"],
                "reason": "Supported pipe evidence reviewed"})

    def test_capabilities_isolation_and_server_actor(self):
        public = self.client.get(f"{self.base}/governance/access").json()
        self.assertEqual(public["role"], "public_viewer")
        self.assertFalse(public["permissions"]["review_decide"])
        owner = self.client.get(f"{self.base}/governance/access", headers=self.auth).json()
        self.assertEqual(owner["role"], "governance_owner")
        self.assertTrue(owner["permissions"]["governance_reconsider"])
        self.assertEqual(self.client.get(
            "/api/v1/workspaces/audit-private/audit-events", headers=self.auth).status_code, 403)

        response = self.approve()
        self.assertEqual(response.status_code, 200)
        event = self.client.get(f"{self.base}/audit-events", headers=self.auth).json()["items"][0]
        self.assertEqual(event["actor"], "fixture-owner")
        self.assertEqual(event["workspace_id"], "audit-public")

    def test_override_history_filters_idempotency_and_restart(self):
        before = self.client.get(f"{self.base}/pairs/M000753/M000925").json()
        approved = self.approve("phase10-idempotent")
        replay = self.approve("phase10-idempotent")
        self.assertFalse(approved.json()["idempotent_replay"])
        self.assertTrue(replay.json()["idempotent_replay"])
        decision_id = approved.json()["decision_id"]
        override = self.client.post(f"{self.base}/decisions/{decision_id}/reconsider",
            headers={**self.auth, "Idempotency-Key": "phase10-override"}, json={
                "action": "reject", "reason": "Governance override after independent review"})
        self.assertEqual(override.status_code, 200)
        stale_override = self.client.post(
            f"{self.base}/decisions/{decision_id}/reconsider",
            headers={**self.auth, "Idempotency-Key": "phase10-stale-override"}, json={
                "action": "defer", "reason": "Attempt to branch superseded history"})
        self.assertEqual(stale_override.status_code, 422)
        self.assertIn("current decision", stale_override.json()["detail"])

        history = self.client.get(
            f"{self.base}/decisions?source_id=M000753", headers=self.auth).json()
        self.assertEqual(history["total"], 2)
        self.assertFalse(history["items"][0]["is_current"])
        self.assertTrue(history["items"][1]["is_current"])
        audits = self.client.get(
            f"{self.base}/audit-events?source_id=M000753", headers=self.auth).json()
        self.assertEqual(audits["total"], 2)
        mappings = self.client.get(
            f"{self.base}/mapping-history?source_id=M000753", headers=self.auth).json()
        self.assertEqual(mappings["total"], 2)
        self.assertEqual(mappings["items"][-1]["new_status"], "unresolved")
        self.assertEqual(self.client.get(f"{self.base}/pairs/M000753/M000925").json(), before)

        restarted = TestClient(create_app(settings=Settings(
            demo_token="fixture-secret", demo_subject="fixture-owner"),
            storage=LocalWorkspaceStorage(self.storage.root)))
        try:
            self.assertEqual(restarted.get(
                f"{self.base}/audit-events", headers=self.auth).json()["total"], 2)
            self.assertEqual(restarted.get(
                f"{self.base}/mapping-history", headers=self.auth).json()["total"], 4)
        finally:
            restarted.close()

    def test_governance_interface_uses_audit_contract(self):
        page = self.client.get("/").text
        script = self.client.get("/static/app.js").text
        for text in ("Governance and audit", "Governance event timeline",
                     "Mapping change history", "Previous states are retained"):
            self.assertIn(text, page)
        for text in ("/governance/access", "/audit-events", "/mapping-history",
                     "input_versions", "rule_versions", "d.is_current"):
            self.assertIn(text, script)


if __name__ == "__main__":
    unittest.main()
