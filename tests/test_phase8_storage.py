from pathlib import Path
import tempfile
import unittest

from api_service import Settings, create_app
from prototype_registry import RegistryStore, load_phase3_records
from service_storage import restore_registry, serialize_registry

ROOT = Path(__file__).resolve().parents[1]


class Phase8StorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records = {r["source_record_id"]: r for r in load_phase3_records(
            ROOT / "output/phase3-v0.1/material_attributes.jsonl")}
        cls.records = [records["M000753"], records["M000925"]]

    def test_sqlite_image_roundtrip_preserves_code_history_and_idempotency(self):
        original = RegistryStore(":memory:")
        try:
            original.import_records(self.records)
            result = original.decide_idempotent("storage-roundtrip", "hash-1", "approve",
                "identity", ["M000753", "M000925"], "Storage fixture approval",
                "fixture-owner", demonstration=True)
            image = serialize_registry(original)
        finally:
            original.close()
        restored = restore_registry(image)
        try:
            entry = restored.get_registry(result["proposed_code"])
            self.assertEqual(entry["proposed_code"], result["proposed_code"])
            self.assertIn("dimensions/specification values", entry["readable_description"])
            self.assertEqual(len(restored.decision_history()), 1)
            replay = restored.decide_idempotent("storage-roundtrip", "hash-1", "approve",
                "identity", ["M000753", "M000925"], "Storage fixture approval",
                "fixture-owner", demonstration=True)
            self.assertTrue(replay["idempotent_replay"])
            self.assertEqual(replay["proposed_code"], result["proposed_code"])
        finally:
            restored.close()

    def test_deployment_refuses_demo_auth(self):
        with self.assertRaises(RuntimeError):
            create_app(settings=Settings(deployment_mode=True, auth_mode="demo"),
                       storage=object())


if __name__ == "__main__":
    unittest.main()
