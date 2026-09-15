"""Remote harness contracts exercised through the shared modular implementation."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "scripts"))
from bundle import render
from install import install
from validate_adapters import validate


class HarnessIntegrationTests(unittest.TestCase):
    def test_profiles_install_only_the_selected_roles_and_switch_cleanly(self):
        with tempfile.TemporaryDirectory() as temp:
            for host, directory, suffix in (("vscode", ".github/agents", ".agent.md"), ("codex", ".codex/agents", ".toml")):
                target = Path(temp) / host
                install(host, target, profile="multi")
                self.assertEqual(len(list((target / directory).glob("cells-*" + suffix))), 4)
                result = install(host, target, profile="single")
                self.assertEqual(result["removed_files"], 3)
                self.assertEqual([p.name for p in (target / directory).glob("cells-*" + suffix)], ["cells-orchestrator" + suffix])
                validate(host, installed=target / ".github" if host == "vscode" else target)

    def test_opencode_profiles_have_one_or_four_native_agents(self):
        with tempfile.TemporaryDirectory() as temp:
            for profile, count in (("single", 1), ("multi", 4)):
                target = Path(temp) / profile
                render("project-local", target, profile)
                config = json.loads((target / ".opencode/opencode.json").read_text())
                self.assertEqual(len(config["agent"]), count)

    def test_harness_doctor_does_not_classify_generic_package_or_write_context(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            (target / "package.json").write_text('{"name":"plain-lit","dependencies":{"lit":"3"}}')
            result = subprocess.run([sys.executable, str(ROOT / "scripts/cells_agent.py"), "doctor", "--workspace", temp], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(json.loads(result.stdout)["context"]["cells_project"])
            self.assertFalse((target / ".cells-agent").exists())

    def test_harness_install_dry_run_and_explicit_context(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            command = [sys.executable, str(ROOT / "scripts/cells_agent.py"), "install", "--host", "vscode", "--scope", "workspace", "--workspace", temp, "--write-context"]
            preview = subprocess.run(command + ["--dry-run"], capture_output=True, text=True)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertEqual(list(target.iterdir()), [])
            applied = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertTrue((target / ".cells-agent/context.json").is_file())
