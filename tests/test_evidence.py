import json
from datetime import datetime
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from cells_agent.evidence import fingerprint, read_evidence, run_check


@unittest.skipUnless(shutil.which("npm") and shutil.which("node"), "npm/node required for real command evidence")
class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cells checks ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "project"
        self.root.mkdir()
        self.store = Path(self.tmp.name) / "private/evidence.db"

    def package(self, command):
        (self.root / "package.json").write_text(json.dumps({"scripts": {"test": command}}))

    def test_current_evidence_becomes_stale_after_file_edit(self):
        self.package("node -e 'console.log(42)'")
        result = run_check(self.root, "test", store=self.store)
        self.assertEqual(result["status"], "success")
        self.assertIn("42", result["output_tail"])
        self.assertTrue(read_evidence(self.root, store=self.store)["records"][0]["current"])
        (self.root / "source.js").write_text("changed")
        self.assertFalse(read_evidence(self.root, store=self.store)["records"][0]["current"])

    def test_failure_is_not_reported_as_success(self):
        self.package("node -e 'process.exit(7)'")
        result = run_check(self.root, "test", store=self.store)
        self.assertEqual(result["status"], "failed")
        self.assertNotEqual(result["exit_code"], 0)
        overview = read_evidence(self.root, store=self.store)
        self.assertEqual(overview["status"], "partial")
        self.assertTrue(overview["records"][0]["current"])
        self.assertFalse(overview["records"][0]["passed"])

    def test_start_timestamp_precedes_child_output(self):
        self.package('node -e \'console.log("child-start="+Date.now());setTimeout(()=>{},100)\'')
        result = run_check(self.root, "test", store=self.store)
        child_time = int(re.search(r"^child-start=(\d+)$", result["output_tail"], re.M)[1]) / 1000
        self.assertLessEqual(datetime.fromisoformat(result["started_at"]).timestamp(), child_time)
        self.assertGreaterEqual(result["duration_seconds"], 0.1)

    def test_source_mutation_during_check_is_partial(self):
        self.package('node -e "require(\'fs\').writeFileSync(\'source.js\',\'changed\')"')
        self.assertEqual(run_check(self.root, "test", store=self.store)["status"], "partial")

    def test_partial_check_cli_has_a_nonzero_exit_status(self):
        self.package('node -e "require(\'fs\').writeFileSync(\'source.js\',\'changed\')"')
        entry = Path(__file__).resolve().parents[1] / "runtime/cells-agent.py"
        result = subprocess.run([sys.executable, str(entry), "--root", str(self.root), "--data-dir", str(self.store.parent), "check", "test"], capture_output=True, text=True, timeout=10)
        self.assertEqual(json.loads(result.stdout)["status"], "partial")
        self.assertEqual(result.returncode, 1)

    def test_timeout_is_bounded(self):
        self.package("node -e 'setInterval(()=>{},1000)'")
        self.assertEqual(run_check(self.root, "test", timeout=1, store=self.store)["status"], "timed_out")

    def test_fingerprint_does_not_follow_file_symlinks(self):
        outside = Path(self.tmp.name) / "outside"
        outside.write_text("first")
        (self.root / "link").symlink_to(outside)
        before = fingerprint(self.root)
        outside.write_text("second")
        self.assertEqual(before, fingerprint(self.root))
