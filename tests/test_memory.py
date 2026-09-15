"""The public bundle tests the subprocess contract, not private storage internals."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from cells_agent.memory import LocalMemory, LocalMemoryError
from memory_stub import make_backend


class MemoryBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cells bridge with spaces ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        command = make_backend(self.root)
        env = patch.dict("os.environ", {"CELLS_MEMORY_COMMAND": str(command)})
        env.start()
        self.addCleanup(env.stop)
        self.database = self.root / "data/memory.db"

    def test_missing_backend_is_actionable_and_does_not_create_storage(self):
        with patch.dict("os.environ", {"CELLS_MEMORY_COMMAND": str(self.root / "missing")}):
            with self.assertRaisesRegex(LocalMemoryError, "not installed"):
                LocalMemory(self.database)
        self.assertFalse(self.database.parent.exists())

    def test_request_keeps_text_out_of_command_arguments(self):
        memory = LocalMemory(self.database)
        content = 'Literal $() & pipes | and quotes " are just memory data.'
        source = {"origin": "test", "nested": ["á", 3]}
        saved = memory.save("project with spaces", "Title", content, source=source)
        found = memory.get("project with spaces", saved["id"])
        self.assertEqual(found["content"], content)
        self.assertEqual(found["source"], source)
        self.assertIsNone(memory.get("other-project", saved["id"]))

    def test_import_forwards_dry_run_and_explicit_database(self):
        memory = LocalMemory(self.database)
        report = memory.import_data("project", {"sample": [1, 2]})
        request = report["received"]
        self.assertEqual(request["database"], str(self.database))
        self.assertEqual(request["protocol_version"], 1)
        self.assertFalse(request["arguments"]["apply"])
        self.assertFalse(self.database.exists())

    def test_bad_json_and_failed_process_become_bridge_errors(self):
        memory = LocalMemory(self.database)
        for result in (subprocess.CompletedProcess([], 0, "invalid-json", ""), subprocess.CompletedProcess([], 2, "", "failed")):
            with patch("cells_agent.memory.subprocess.run", return_value=result):
                with self.assertRaises(LocalMemoryError):
                    memory.context("project")

    def test_invalid_project_never_starts_backend(self):
        memory = LocalMemory(self.database)
        with patch("cells_agent.memory.subprocess.run") as call:
            with self.assertRaises(ValueError):
                memory.context("")
            call.assert_not_called()
