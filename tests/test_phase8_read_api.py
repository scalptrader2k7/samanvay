from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from api_service import Settings, create_app
from prototype_registry import load_phase3_records
from service_storage import LocalWorkspaceStorage

ROOT = Path(__file__).resolve().parents[1]


class Phase8ReadApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        all_records = {r["source_record_id"]: r for r in load_phase3_records(
            ROOT / "output/phase3-v0.1/material_attributes.jsonl")}
        cls.records = [all_records[x] for x in
                       ("M000041", "M000114", "M000753", "M000925", "M000830", "M000834")]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.storage = LocalWorkspaceStorage(Path(self.temp.name) / "storage")
        self.storage.create_workspace("public-demo", "fixture-owner", public_read=True)
        with self.storage.open_workspace("public-demo", "fixture-owner", write=True) as store:
            store.import_records(self.records)
            store.decide("approve", "identity", ["M000753", "M000925"],
                         "Fixture reviewed", "fixture-owner", demonstration=True)
        app = create_app(settings=Settings(local_storage_dir=self.temp.name), storage=self.storage)
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close(); self.temp.cleanup()

    def test_health_readiness_material_pagination_and_search(self):
        self.assertEqual(self.client.get("/health").json()["status"], "ok")
        ready = self.client.get("/ready").json()
        self.assertEqual(ready["status"], "ready")
        page = self.client.get("/api/v1/workspaces/public-demo/materials?limit=2").json()
        self.assertEqual(page["total"], 6)
        self.assertEqual(len(page["items"]), 2)
        self.assertEqual(page["next_offset"], 2)
        search = self.client.get(
            "/api/v1/workspaces/public-demo/materials/search?q=ASTM%20A312").json()
        self.assertEqual(search["total"], 2)
        self.assertEqual(self.client.get(
            "/api/v1/workspaces/public-demo/materials?limit=101").status_code, 422)

    def test_lexical_candidates_and_pair_evidence(self):
        response = self.client.get(
            "/api/v1/workspaces/public-demo/materials/M000753/candidates?top_k=5")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["retrieval_type"], "bounded_lexical")
        self.assertFalse(body["identity_decision"])
        self.assertIn("M000925", [x["candidate_source_record_id"] for x in body["items"]])
        pair = self.client.get("/api/v1/workspaces/public-demo/pairs/M000830/M000834").json()
        self.assertEqual(pair["outcome"]["label"], "conflict")
        self.assertEqual(pair["left"]["source_record_id"], "M000830")

    def test_registry_mappings_history_relationships_and_dashboard(self):
        registry = self.client.get("/api/v1/workspaces/public-demo/registry").json()
        self.assertEqual(registry["total"], 1)
        self.assertIn("dimensions/specification values", registry["items"][0]["readable_description"])
        mappings = self.client.get("/api/v1/workspaces/public-demo/mappings?limit=100").json()
        self.assertEqual(mappings["total"], 6)
        history = self.client.get("/api/v1/workspaces/public-demo/decisions").json()
        self.assertEqual(history["total"], 1)
        relationships = self.client.get(
            "/api/v1/workspaces/public-demo/functional-relationships").json()
        self.assertEqual(relationships["total"], 0)
        dashboard = self.client.get("/api/v1/workspaces/public-demo/dashboard").json()
        self.assertEqual(dashboard["source_records"], 6)
        self.assertEqual(dashboard["mapped_records"], 2)
        self.assertEqual(dashboard["counts_source"], "persisted workspace records and decisions")

    def test_missing_resources_return_useful_errors(self):
        self.assertEqual(self.client.get("/api/v1/workspaces/missing/materials").status_code, 404)
        response = self.client.get("/api/v1/workspaces/public-demo/pairs/UNKNOWN/M000834")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Material not found", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
