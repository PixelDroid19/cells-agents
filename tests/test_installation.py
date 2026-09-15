import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "scripts"))
from bundle import build, render
from install import install
from validate_adapters import validate
from install import digest


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cells installed with spaces ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_dry_run_has_no_destination_writes(self):
        target = self.root / "new home"
        result = install("codex", target, dry_run=True)
        self.assertFalse(result["applied"])
        self.assertFalse(target.exists())

    def test_legacy_setup_uses_current_installer_and_includes_memory(self):
        target = self.root / "setup home"
        command = ["bash", str(ROOT / "scripts/setup.sh"), "--agent", "codex", "--home", str(target)]
        preview = subprocess.run([*command, "--dry-run"], capture_output=True, text=True, timeout=20)
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertFalse(json.loads(preview.stdout)["applied"])
        self.assertFalse(target.exists())
        result = subprocess.run(command, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((target / ".codex/runtime/cells_agent/memory.py").is_file())
        validate("codex", installed=target)

    def test_install_and_reinstall_are_idempotent(self):
        target = self.root / "home"
        self.assertTrue(install("codex", target)["applied"])
        second = install("codex", target)
        self.assertEqual(second["changed_files"], 0)
        self.assertFalse(second["conflicts"])
        validate("codex", installed=target)

    def test_user_conflicts_are_preserved_and_explicit_replace_backs_up(self):
        target = self.root / "home"
        config = target / ".codex/config.toml"
        config.parent.mkdir(parents=True)
        config.write_text("user setting")
        result = install("codex", target)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(config.read_text(), "user setting")
        self.assertFalse((target / ".codex/runtime").exists())
        result = install("codex", target, replace=True)
        backup = Path(result["backup"]) / ".codex/config.toml"
        self.assertEqual(backup.read_text(), "user setting")

    def test_installer_rejects_symlink_escape(self):
        target = self.root / "home"
        target.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        (target / ".codex").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            install("codex", target, replace=True)
        self.assertEqual(list(outside.iterdir()), [])

    def test_old_managed_files_are_pruned_with_backup(self):
        target = self.root / "home"
        install("codex", target)
        marker = target / ".cells-agent-install-codex.json"
        stale = target / ".codex/runtime/cells_agent/obsolete.py"
        stale.write_text("old managed module")
        data = json.loads(marker.read_text())
        data["files"][str(stale.relative_to(target))] = digest(stale)
        marker.write_text(json.dumps(data))
        result = install("codex", target)
        self.assertEqual(result["removed_files"], 1)
        self.assertFalse(stale.exists())
        self.assertEqual((Path(result["backup"]) / stale.relative_to(target)).read_text(), "old managed module")

    def test_all_global_preflights_both_hosts_before_writes(self):
        target = self.root / "global home"
        conflict = target / ".codex/config.toml"
        conflict.parent.mkdir(parents=True)
        conflict.write_text("user config")
        result = subprocess.run([sys.executable, str(ROOT / "scripts/install.py"), "--agent", "all-global", "--home", str(target)], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse((target / ".config/opencode").exists())
        self.assertEqual(conflict.read_text(), "user config")

    def test_custom_bundle_includes_documentation_and_capabilities(self):
        target = self.root / "custom"
        self.assertTrue(install("custom", target)["applied"])
        for relative in ("skills/cells-apply/SKILL.md", "runtime/cells-agent.py", "docs/runtime.md", "adapters/hosts.json"):
            self.assertTrue((target / relative).is_file(), relative)

    def test_standalone_plugin_runs_from_another_workspace(self):
        target = self.root / "plugin space"
        build("vscode-plugin", target)
        validate("vscode", plugin=target)

    def test_vscode_workspace_and_opencode_installations(self):
        for agent in ("vscode", "opencode"):
            with self.subTest(agent=agent):
                target = self.root / agent
                self.assertTrue(install(agent, target)["applied"])
                validate(agent, installed=target / ".github" if agent == "vscode" else target)

    def test_builder_refuses_unowned_output(self):
        target = self.root / "user files"
        target.mkdir()
        (target / "keep").write_text("keep")
        with self.assertRaises(ValueError):
            build("codex-plugin", target)
        self.assertEqual((target / "keep").read_text(), "keep")

    def test_builder_preserves_modified_or_additional_output_files(self):
        for relative in ("runtime/cells-agent.py", "personal-note.md"):
            with self.subTest(relative=relative):
                target = self.root / relative.replace("/", "-")
                build("codex-plugin", target)
                changed = target / relative
                changed.write_text("user edit")
                with self.assertRaises(ValueError):
                    build("codex-plugin", target)
                self.assertEqual(changed.read_text(), "user edit")

    def test_builder_can_update_untouched_managed_bundle(self):
        target = self.root / "managed"
        build("codex-plugin", target)
        first = (target / ".cells-bundle.json").read_bytes()
        build("codex-plugin", target)
        self.assertEqual((target / ".cells-bundle.json").read_bytes(), first)

    def test_cli_and_mcp_from_copied_bundle(self):
        target = self.root / "plugin"
        render("codex-plugin", target)
        request = {"jsonrpc": "2.0", "id": 9, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "clientInfo": {"name": "install-test", "version": "1"}, "capabilities": {}}}
        result = subprocess.run([sys.executable, str(target / "runtime/cells-agent.py"), "mcp"], cwd=self.root, input=json.dumps(request) + "\n", capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["result"]["serverInfo"]["name"], "cells-agent")
