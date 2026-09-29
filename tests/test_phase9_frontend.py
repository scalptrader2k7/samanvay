from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from api_service import Settings, create_app
from service_storage import LocalWorkspaceStorage


class Phase9FrontendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        storage = LocalWorkspaceStorage(Path(self.temp.name) / "storage")
        storage.create_workspace("public-demo", "fixture-owner", public_read=True)
        app = create_app(settings=Settings(local_storage_dir=self.temp.name), storage=storage)
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()

    def test_reviewer_application_is_served_by_fastapi(self):
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        for text in ("Samanvay Reviewer", "Materials", "Review queue", "Registry"):
            self.assertIn(text, page.text)
        self.assertEqual(self.client.get("/static/app.css").status_code, 200)
        self.assertEqual(self.client.get("/static/app.js").status_code, 200)

    def test_thin_client_uses_phase8_contract_and_write_guards(self):
        script = self.client.get("/static/app.js").text
        for path in ("/materials", "/candidates", "/pairs/", "/decisions",
                     "/reconsider", "/registry", "/mappings", "/exports/"):
            self.assertIn(path, script)
        self.assertIn("Idempotency-Key", script)
        self.assertIn("Bearer", script)
        self.assertIn("retrieval_score", script)
        self.assertIn("possible_functional_equivalent", script)
        self.assertIn("Missing / not supplied", script)

    def test_upload_limit_and_outcomes_are_explicit(self):
        page = self.client.get("/").text
        self.assertIn("No upload endpoint", page)
        for outcome in ("Exact duplicate", "Near duplicate", "Possible equivalent",
                        "Conflict", "No match"):
            self.assertIn(outcome, page)


if __name__ == "__main__":
    unittest.main()
