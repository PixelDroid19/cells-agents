"""Regression tests for behavior that the old text-presence validators missed."""
import json
from pathlib import Path
import tempfile
import unittest

from cells_agent.project import project_info, resolve_command
from cells_agent.policy import assess_command, assess_tool


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cells project ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def package(self, **values):
        (self.root / "package.json").write_text(json.dumps(values))

    def test_plain_lit_is_not_cells(self):
        self.package(dependencies={"lit": "3"}, scripts={"test": "vitest run"})
        self.assertFalse(project_info(self.root)["is_cells"])
        self.assertEqual(resolve_command(self.root, "test")["selected"]["argv"], ["npm", "run", "test"])

    def test_real_cells_script_and_alias(self):
        self.package(scripts={"test": "npm run unit", "unit": "cells component:test"})
        result = resolve_command(self.root, "test")
        self.assertTrue(result["selected"]["native"])
        self.assertEqual(assess_command("npm test", self.root)["decision"], "allow")

    def test_unverified_lifecycle_script_is_not_approved(self):
        self.package(scripts={"test": "cells lit-component:test", "pretest": "echo setup"})
        self.assertEqual(resolve_command(self.root, "test")["status"], "blocked")
        self.assertEqual(assess_command("npm test", self.root)["decision"], "review")

    def test_echo_does_not_make_command_verified(self):
        self.package(dependencies={"@bbva-spherica-components/bbva-button-default": "1"}, scripts={"test": "echo cells component:test"})
        self.assertEqual(resolve_command(self.root, "test")["status"], "blocked")

    def test_mention_in_echo_is_not_cells_project_evidence(self):
        self.package(scripts={"example": "echo cells component:test"})
        self.assertFalse(project_info(self.root)["is_cells"])

    def test_watch_and_snapshot_update_scripts_are_not_automatic_checks(self):
        self.package(scripts={"test:watch": "cells component:test --watch", "test:update-snapshots": "cells component:test --update-snapshots"})
        self.assertEqual(resolve_command(self.root, "test")["status"], "blocked")
        self.package(scripts={"test": "cells component:test --watch=true"})
        self.assertEqual(resolve_command(self.root, "test")["status"], "blocked")
        for flag in ("--updateSnapshots", "--updateSnapshots=true", "--updateLocales", "--update-locales"):
            self.package(scripts={"test": f"cells component:test {flag}"})
            self.assertEqual(resolve_command(self.root, "test")["status"], "blocked", flag)

    def test_documented_component_coverage_uses_existing_test_script(self):
        for family in ("component", "lit-component"):
            self.package(scripts={"test": f"cells {family}:test --wtr"})
            self.assertEqual(resolve_command(self.root, "coverage")["selected"]["argv"], ["npm", "run", "test"])
        for flag in ("--no-coverage", "--coverage=false", "--coverage false"):
            self.package(scripts={"test": f"cells component:test {flag}"})
            self.assertEqual(resolve_command(self.root, "coverage")["status"], "blocked", flag)

    def test_native_environment_prefix_and_declared_package_manager(self):
        self.package(packageManager="pnpm@9.0.0", scripts={"test": "NODE_OPTIONS=--trace-warnings cells component:test"})
        self.assertEqual(resolve_command(self.root, "test")["selected"]["argv"], ["pnpm", "run", "test"])

    def test_workspace_package_manager(self):
        self.package(packageManager="pnpm@9.0.0", workspaces=["packages/*"])
        member = self.root / "packages/component"
        member.mkdir(parents=True)
        (member / "package.json").write_text(json.dumps({"scripts": {"test": "cells component:test"}}))
        self.assertEqual(resolve_command(member, "test")["selected"]["argv"], ["pnpm", "run", "test"])

    def test_prose_does_not_trigger_destructive_rule(self):
        payload = {"tool_name": "create_file", "tool_input": {"text": "Do not execute git reset --hard."}}
        self.assertEqual(assess_tool(payload)["decision"], "allow")

    def test_destructive_variants(self):
        for command in ("git reset --hard", "git -C . reset --hard", "git -c x=y push --force", "rm -rf .", "bash -c 'git reset --hard'", "bash -c -- 'git reset --hard'", "sudo -- git reset --hard", "env -- git reset --hard", "/usr/bin/env -- git reset --hard"):
            with self.subTest(command=command):
                self.assertEqual(assess_command(command, self.root)["decision"], "review")

    def test_additional_shells_cannot_hide_destructive_commands(self):
        for command in ("dash -c 'git reset --hard'", "ksh -c 'git reset --hard'", "fish -c 'git reset --hard'", "bash -lc 'git reset --hard'", "cmd /c git reset --hard", "powershell -Command 'git reset --hard'", "pwsh -Command 'git reset --hard'"):
            self.assertEqual(assess_command(command, self.root)["decision"], "review", command)

    def test_generic_repository_does_not_receive_cells_test_policy(self):
        self.assertEqual(assess_command("npm test", self.root)["decision"], "allow")

    def test_malformed_terminal_payload_requires_review(self):
        self.assertEqual(assess_tool({"tool_name": "Bash"})["decision"], "review")

    def test_project_identity_does_not_collide_for_same_basename(self):
        for folder in (self.root / "a/repo", self.root / "b/repo"):
            folder.mkdir(parents=True)
            (folder / "package.json").write_text("{}")
        self.assertNotEqual(project_info(self.root / "a/repo")["project"], project_info(self.root / "b/repo")["project"])
