from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cells_agent.py"
SPEC = importlib.util.spec_from_file_location("cells_agent", SCRIPT)
assert SPEC and SPEC.loader
cells_agent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cells_agent)


class HarnessTests(unittest.TestCase):
    def test_every_host_renders_from_canonical_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for host in ("vscode", "codex", "opencode"):
                output = cells_agent.render_host(host, root / host, "multi")
                manifest = json.loads((output / "render-manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(host, manifest["host"])
                self.assertGreater(len(manifest["files"]), 10)

            self.assertTrue((root / "vscode/workspace/.github/skills/cells-apply/SKILL.md").is_file())
            vscode_apply = (
                root / "vscode/workspace/.github/skills/cells-apply/SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertIn(".github/skills/_shared/", vscode_apply)
            self.assertNotIn("`skills/_shared/", vscode_apply)
            self.assertTrue(
                (
                    root
                    / "codex/home/.codex/skills"
                    / "cells-components-catalog/assets/bbva_cells_components.db"
                ).is_file()
            )
            self.assertTrue((root / "opencode/workspace/.opencode/opencode.json").is_file())
            opencode_apply = (
                root / "opencode/workspace/.opencode/skills/cells-apply/SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertIn(".opencode/skills/_shared/", opencode_apply)

    def test_profiles_change_agent_fanout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cells_agent.render_host("opencode", root / "single", "single")
            cells_agent.render_host("opencode", root / "multi", "multi")
            single = cells_agent.read_json(root / "single/workspace/.opencode/opencode.json")
            multi = cells_agent.read_json(root / "multi/workspace/.opencode/opencode.json")
            self.assertEqual(["cells-orchestrator"], list(single["agent"]))
            self.assertGreater(len(multi["agent"]), len(single["agent"]))

            cells_agent.render_host("vscode", root / "vscode-single", "single")
            cells_agent.render_host("vscode", root / "vscode-multi", "multi")
            self.assertEqual(
                1, len(list((root / "vscode-single/workspace/.github/agents").glob("*.agent.md")))
            )
            self.assertEqual(
                4, len(list((root / "vscode-multi/workspace/.github/agents").glob("*.agent.md")))
            )

            cells_agent.render_host("codex", root / "codex-single", "single")
            cells_agent.render_host("codex", root / "codex-multi", "multi")
            self.assertEqual(1, len(list((root / "codex-single/home/.codex/agents").glob("*.toml"))))
            self.assertEqual(4, len(list((root / "codex-multi/home/.codex/agents").glob("*.toml"))))
            self.assertFalse((root / "codex-single/home/.codex/config.toml").exists())
            self.assertTrue((root / "codex-single/home/.codex/config.cells.example.toml").is_file())
            for host, single_root, multi_root in (
                ("vscode", root / "vscode-single", root / "vscode-multi"),
                ("codex", root / "codex-single", root / "codex-multi"),
                ("opencode", root / "single", root / "multi"),
            ):
                self.assertEqual([], cells_agent.validate_rendered_profile(host, single_root, "single"))
                self.assertEqual([], cells_agent.validate_rendered_profile(host, multi_root, "multi"))

    def test_opencode_install_merges_existing_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rendered = cells_agent.render_host("opencode", root / "rendered", "single")
            target = root / "home"
            config = target / ".config/opencode/opencode.json"
            cells_agent.write_json(
                config,
                {
                    "theme": "user-theme",
                    "agent": {
                        "personal": {"mode": "primary"},
                        "cells-custom": {"mode": "subagent"},
                    },
                },
            )
            cells_agent.install_tree(rendered / "home", target, force=False)
            merged = cells_agent.read_json(config)
            self.assertEqual("user-theme", merged["theme"])
            self.assertIn("personal", merged["agent"])
            self.assertIn("cells-custom", merged["agent"])
            self.assertIn("cells-orchestrator", merged["agent"])

    def test_single_profile_removes_managed_multi_agents(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cases = (
                ("vscode", "workspace", "workspace"),
                ("codex", "user", "home"),
                ("opencode", "workspace", "workspace"),
            )
            for host, scope, source_leaf in cases:
                target = root / f"{host}-target"
                multi = cells_agent.render_host(host, root / f"{host}-multi", "multi")
                single = cells_agent.render_host(host, root / f"{host}-single", "single")
                cells_agent.install_tree(multi / source_leaf, target, force=False)
                cells_agent.install_tree(single / source_leaf, target, force=False)
                cells_agent.cleanup_profile_assets(host, scope, target, "single")
                if host == "opencode":
                    config = cells_agent.read_json(target / ".opencode/opencode.json")
                    self.assertEqual({"cells-orchestrator"}, set(config["agent"]) & {"cells-orchestrator", *cells_agent.ROLE_AGENTS})
                elif host == "vscode":
                    self.assertEqual(
                        ["cells-orchestrator.agent.md"],
                        sorted(path.name for path in (target / ".github/agents").glob("cells-*.agent.md")),
                    )
                else:
                    self.assertEqual(
                        ["cells-orchestrator.toml"],
                        sorted(path.name for path in (target / ".codex/agents").glob("cells-*.toml")),
                    )

    def test_markdown_install_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.md"
            target = root / "AGENTS.md"
            source.write_text("# Cells\n\nRule.", encoding="utf-8")
            target.write_text("# Existing\n", encoding="utf-8")
            cells_agent.merge_markdown(source, target)
            cells_agent.merge_markdown(source, target)
            text = target.read_text(encoding="utf-8")
            self.assertEqual(1, text.count(cells_agent.MANAGED_BEGIN))
            self.assertIn("# Existing", text)

    def test_context_autodetects_sibling_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / "bbva-feature-demo"
            workspace.mkdir()
            (workspace / "package.json").write_text("{}", encoding="utf-8")
            packages = root / "bbva-spherica-components-master@abc" / "packages"
            packages.mkdir(parents=True)
            args = type("Args", (), {"catalog": None, "docs": None, "cells_cli": None})()
            context = cells_agent.detect_context(workspace, args)
            self.assertTrue(context["cells_project"])
            self.assertEqual(str(packages.resolve()), context["component_catalog_root"])

    def test_context_preserves_multiple_host_skill_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            base = {"schema_version": 1, "host_skill_roots": {"vscode": "a"}}
            cells_agent.write_context(workspace, base)
            update = {"schema_version": 1, "host_skill_roots": {"codex": "b"}}
            path = cells_agent.write_context(workspace, update)
            context = cells_agent.read_json(path)
            self.assertEqual({"vscode": "a", "codex": "b"}, context["host_skill_roots"])

    def test_render_refuses_protected_force_targets(self) -> None:
        with self.assertRaises(cells_agent.HarnessError):
            cells_agent.ensure_safe_render_target(cells_agent.REPO_ROOT)
        with self.assertRaises(cells_agent.HarnessError):
            cells_agent.ensure_safe_render_target(Path.home())

    def test_upgrade_requires_force_to_remove_deprecated_skill_names(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            deprecated = target / ".codex/skills/skill-registry"
            unrelated = target / ".codex/skills/my-team-skill"
            deprecated.mkdir(parents=True)
            unrelated.mkdir(parents=True)
            (deprecated / "SKILL.md").write_text("old", encoding="utf-8")
            (unrelated / "SKILL.md").write_text("keep", encoding="utf-8")
            self.assertEqual(
                [],
                cells_agent.cleanup_deprecated_assets("codex", "user", target),
            )
            self.assertTrue(deprecated.is_dir())
            removed = cells_agent.cleanup_deprecated_assets(
                "codex",
                "user",
                target,
                force=True,
            )
            self.assertEqual([str(deprecated.resolve())], removed)
            self.assertFalse(deprecated.exists())
            self.assertTrue(unrelated.is_dir())

    def test_install_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            target = root / "target"
            outside = root / "outside"
            (source / ".codex").mkdir(parents=True)
            target.mkdir()
            outside.mkdir()
            (source / ".codex/AGENTS.md").write_text("managed", encoding="utf-8")
            try:
                (target / ".codex").symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Symlinks unavailable: {exc}")
            with self.assertRaises(cells_agent.HarnessError):
                cells_agent.install_tree(source, target, force=False)
            self.assertEqual([], list(outside.iterdir()))

    def test_copy_tree_skips_sqlite_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            (source / "catalog.db").write_bytes(b"db")
            (source / "catalog.db-wal").write_bytes(b"wal")
            (source / "catalog.db-shm").write_bytes(b"shm")
            cells_agent.copy_tree(source, target)
            self.assertTrue((target / "catalog.db").is_file())
            self.assertFalse((target / "catalog.db-wal").exists())
            self.assertFalse((target / "catalog.db-shm").exists())


if __name__ == "__main__":
    unittest.main()
