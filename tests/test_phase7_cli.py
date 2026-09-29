import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from prototype_registry import RegistryStore, load_phase3_records

ROOT = Path(__file__).resolve().parents[1]


class Phase7CliTests(unittest.TestCase):
    def test_cli_decision_and_restart_preview(self):
        records = {r["source_record_id"]: r for r in load_phase3_records(
            ROOT / "output/phase3-v0.1/material_attributes.jsonl")}
        with tempfile.TemporaryDirectory() as temp:
            database = Path(temp) / "registry.db"
            with RegistryStore(database) as store:
                store.import_records([records["M000753"], records["M000925"]])
            command = [sys.executable, str(ROOT / "phase7_registry.py"), "--db", str(database)]
            approved = subprocess.run(command + ["decide", "approve", "identity",
                "M000753", "M000925", "--reason", "CLI fixture reviewed", "--actor", "fixture"],
                cwd=ROOT, text=True, capture_output=True, check=True)
            result = json.loads(approved.stdout)
            self.assertRegex(result["proposed_code"], r"^SMV-P-[0-9A-F]{12}$")
            preview = subprocess.run(command + ["preview"], cwd=ROOT, text=True,
                                     capture_output=True, check=True)
            summary = json.loads(preview.stdout)
            self.assertEqual(summary["mapped_records"], 2)
            self.assertNotIn("rows", summary)

    def test_demonstration_pack_manifest_and_separation(self):
        output = ROOT / "output/phase7-v0.1"
        report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        example = json.loads((output / "example_registry_entry.json").read_text(encoding="utf-8"))
        self.assertTrue(report["demonstration_only"])
        self.assertEqual(report["evaluation_labels_created"], 0)
        self.assertTrue(report["stable_repeat_code_check"])
        self.assertEqual(example["prototype_status"], "prototype_proposed")
        self.assertEqual(len(example["members"]), 2)
        self.assertTrue(all(member["original_description"] for member in example["members"]))
        import hashlib
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        for name, expected in manifest["artifacts"].items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
