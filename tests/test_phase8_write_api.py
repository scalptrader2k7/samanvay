from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from api_service import Settings, create_app
from prototype_registry import load_phase3_records
from service_storage import LocalWorkspaceStorage

ROOT = Path(__file__).resolve().parents[1]


class Phase8WriteApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        all_records = {r["source_record_id"]: r for r in load_phase3_records(
            ROOT / "output/phase3-v0.1/material_attributes.jsonl")}
        cls.records = [all_records[x] for x in
                       ("M000041", "M000114", "M000753", "M000925", "M000830", "M000834")]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name) / "storage"
        self.storage = LocalWorkspaceStorage(root)
        for workspace, owner in (("write-demo", "fixture-owner"), ("other-private", "other-owner")):
            self.storage.create_workspace(workspace, owner)
            with self.storage.open_workspace(workspace, owner, write=True) as store:
                store.import_records(self.records)
        settings = Settings(local_storage_dir=str(root), demo_token="fixture-secret",
                            demo_subject="fixture-owner")
        self.client = TestClient(create_app(settings=settings, storage=self.storage))
        self.auth = {"Authorization": "Bearer fixture-secret"}

    def tearDown(self):
        self.client.close(); self.temp.cleanup()

    def approve(self, key="approval-0001"):
        return self.client.post("/api/v1/workspaces/write-demo/decisions",
            headers={**self.auth, "Idempotency-Key": key}, json={
                "action": "approve", "relationship_type": "identity",
                "member_ids": ["M000753", "M000925"],
                "reason": "Reviewed matching pipe specifications", "demonstration": True})

    def test_approval_is_idempotent_actor_is_server_identity_and_exports_work(self):
        first = self.approve(); self.assertEqual(first.status_code, 200)
        result = first.json(); self.assertFalse(result["idempotent_replay"])
        self.assertRegex(result["proposed_code"], r"^SMV-P-[0-9A-F]{12}$")
        replay = self.approve(); self.assertEqual(replay.status_code, 200)
        self.assertTrue(replay.json()["idempotent_replay"])
        self.assertEqual(replay.json()["proposed_code"], result["proposed_code"])
        history = self.client.get("/api/v1/workspaces/write-demo/decisions", headers=self.auth).json()
        self.assertEqual(history["total"], 1)
        self.assertEqual(history["items"][0]["actor"], "fixture-owner")
        preview = self.client.get("/api/v1/workspaces/write-demo/migration-preview", headers=self.auth).json()
        self.assertEqual(preview["mapped_records"], 2)
        self.assertEqual(self.client.get(
            "/api/v1/workspaces/write-demo/exports/source-mappings.json", headers=self.auth).status_code, 200)
        csv_response = self.client.get(
            "/api/v1/workspaces/write-demo/exports/source-mappings.csv", headers=self.auth)
        self.assertEqual(csv_response.status_code, 200)
        self.assertIn("attachment; filename=source_mappings.csv", csv_response.headers["content-disposition"])
        entry = self.client.get(
            f"/api/v1/workspaces/write-demo/registry/{result['proposed_code']}",
            headers=self.auth)
        self.assertEqual(entry.status_code, 200)
        self.assertIn("readable_description", entry.json())
        unresolved = self.client.get(
            "/api/v1/workspaces/write-demo/exports/unresolved-records.json?limit=2",
            headers=self.auth).json()
        self.assertEqual(len(unresolved["items"]), 2)
        conflicts = self.client.get(
            "/api/v1/workspaces/write-demo/exports/conflicts.csv?limit=10",
            headers=self.auth)
        self.assertEqual(conflicts.status_code, 200)

    def test_authentication_ownership_conflict_and_changed_idempotency_payload(self):
        payload = {"action": "reject", "relationship_type": "identity",
                   "member_ids": ["M000830", "M000834"],
                   "reason": "Supported cable area conflict"}
        path = "/api/v1/workspaces/write-demo/decisions"
        self.assertEqual(self.client.post(path, headers={"Idempotency-Key": "reject-0001"},
                                          json=payload).status_code, 401)
        self.assertEqual(self.client.post("/api/v1/workspaces/other-private/decisions",
            headers={**self.auth, "Idempotency-Key": "reject-0002"}, json=payload).status_code, 403)
        first = self.client.post(path, headers={**self.auth, "Idempotency-Key": "reject-0003"}, json=payload)
        self.assertEqual(first.status_code, 200)
        changed = {**payload, "reason": "Changed reason under same key"}
        self.assertEqual(self.client.post(path, headers={**self.auth,
            "Idempotency-Key": "reject-0003"}, json=changed).status_code, 409)
        conflict = {"action": "approve", "relationship_type": "identity",
                    "member_ids": ["M000830", "M000834"],
                    "reason": "Unsafe approval fixture"}
        response = self.client.post(path, headers={**self.auth,
            "Idempotency-Key": "approval-conflict"}, json=conflict)
        self.assertEqual(response.status_code, 409)
        self.assertTrue(response.json()["pair_checks"])

    def test_reconsideration_functional_relationship_and_restart_persistence(self):
        approved = self.approve("approval-reconsider").json()
        response = self.client.post(
            f"/api/v1/workspaces/write-demo/decisions/{approved['decision_id']}/reconsider",
            headers={**self.auth, "Idempotency-Key": "reconsider-0001"},
            json={"action": "reject", "reason": "Second review rejected identity",
                  "demonstration": True})
        self.assertEqual(response.status_code, 200)
        functional = self.client.post("/api/v1/workspaces/write-demo/decisions",
            headers={**self.auth, "Idempotency-Key": "functional-0001"}, json={
                "action": "approve", "relationship_type": "functional_equivalence",
                "member_ids": ["M000041", "M000114"],
                "reason": "Qualified demonstration relationship", "demonstration": True})
        self.assertEqual(functional.status_code, 200)
        self.assertIsNone(functional.json()["proposed_code"])
        # A new storage/app instance reads the committed files.
        restarted = LocalWorkspaceStorage(self.storage.root)
        client = TestClient(create_app(settings=Settings(demo_token="fixture-secret",
            demo_subject="fixture-owner"), storage=restarted))
        try:
            history = client.get("/api/v1/workspaces/write-demo/decisions", headers=self.auth).json()
            self.assertEqual(history["total"], 3)
            relationships = client.get(
                "/api/v1/workspaces/write-demo/functional-relationships", headers=self.auth).json()
            self.assertEqual(relationships["total"], 1)
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main()
