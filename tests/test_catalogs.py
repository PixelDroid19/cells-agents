"""Regression tests for portable Cells catalog integrity and query behavior."""

from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
COMPONENT_SKILL = "cells-components-catalog"
OFFICIAL_SKILL = "cells-official-docs-catalog"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, *args],
        cwd=cwd or ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def copy_skill(temp_root: Path, skill_name: str) -> Path:
    destination = temp_root / "skills" / skill_name
    shutil.copytree(ROOT / "skills" / skill_name, destination)
    return destination


def make_zip(skill_root: Path, zip_path: Path, prefix: str, *, fake_bytes: bool = False) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(path for path in skill_root.rglob("*") if path.is_file() and "__pycache__" not in path.parts):
            relative = path.relative_to(skill_root).as_posix()
            archive.writestr(f"{prefix}/{relative}", b"not the packaged file" if fake_bytes else path.read_bytes())


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class CatalogIntegrityTests(unittest.TestCase):
    def test_component_source_build_preserves_cem_api_and_exact_selector_forms(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp_root = Path(raw_temp) / "repo"
            skill_root = copy_skill(temp_root, COMPONENT_SKILL)
            packages_root = temp_root / "packages"
            package = packages_root / "bbva-demo-element"
            package.mkdir(parents=True)
            (package / "package.json").write_text(
                json.dumps(
                    {
                        "name": "@bbva-spherica-components/bbva-demo-element",
                        "version": "1.0.0",
                        "description": "Source-backed demo component",
                        "keywords": ["demo"],
                        "dependencies": {"@bbva-web-components/bbva-core-lit-helpers": "^1.0.0"},
                    }
                ),
                encoding="utf-8",
            )
            (package / "custom-elements.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": "1.0.0",
                        "modules": [
                            {
                                "path": "bbva-demo-element.js",
                                "exports": [{"kind": "custom-element-definition", "declaration": {"name": "BbvaDemoElement"}}],
                                "declarations": [
                                    {
                                        "kind": "class",
                                        "name": "BbvaDemoElement",
                                        "members": [
                                            {
                                                "kind": "field",
                                                "name": "label",
                                                "attribute": "label",
                                                "type": {"text": "string"},
                                                "description": "Visible label",
                                            }
                                        ],
                                        "events": [{"name": "demo-change", "description": "Source event"}],
                                    }
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            build = run(
                str(skill_root / "scripts" / "build_index.py"),
                "--packages-root",
                str(packages_root),
                "--source-revision",
                "fixture@abc123",
                cwd=temp_root,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            search = run(
                str(skill_root / "scripts" / "search_docs.py"),
                "--query",
                "bbva_demo_element",
                "--detail",
                "--format",
                "json",
                cwd=temp_root,
            )
            self.assertEqual(search.returncode, 0, search.stderr)
            payload = json.loads(search.stdout)
            self.assertEqual(payload["search_strategy"], "exact_selector")
            record = payload["results"][0]
            self.assertEqual(record["custom_elements"], ["bbva-demo-element"])
            self.assertEqual(record["properties"][0]["name"], "label")
            self.assertEqual(record["events"][0]["name"], "demo-change")
            self.assertTrue(record["source"]["files"][0]["path"].startswith("packages/"))
            hyphen_selector = run(
                str(skill_root / "scripts" / "search_docs.py"),
                "--query",
                "bbva-demo-element",
                "--format",
                "json",
                cwd=temp_root,
            )
            self.assertEqual(hyphen_selector.returncode, 0, hyphen_selector.stderr)
            self.assertEqual(json.loads(hyphen_selector.stdout)["search_strategy"], "exact_selector")

    def test_component_summary_is_bounded_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp_root = Path(raw_temp) / "repo"
            skill_root = copy_skill(temp_root, COMPONENT_SKILL)
            db_path = skill_root / "assets" / "bbva_cells_components.db"
            before = sorted(path.name for path in db_path.parent.iterdir())
            result = run(
                str(skill_root / "scripts" / "search_docs.py"),
                "--query",
                "form input",
                "--limit",
                "3",
                "--format",
                "json",
                cwd=temp_root,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["search_strategy"], "and")
            self.assertLessEqual(payload["count"], 3)
            self.assertNotIn("properties", payload["results"][0])
            self.assertLess(len(result.stdout.encode("utf-8")), 14000)
            self.assertEqual(before, sorted(path.name for path in db_path.parent.iterdir()))
            self.assertFalse(list(db_path.parent.glob(f"{db_path.name}-*")))
            oversized = run(
                str(skill_root / "scripts" / "search_docs.py"),
                "--query",
                "form",
                "--limit",
                "13",
                cwd=temp_root,
            )
            self.assertEqual(oversized.returncode, 2)
            self.assertIn("between 1 and 12", oversized.stderr)

    def test_component_stale_records_fail_without_auto_rebuild(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp_root = Path(raw_temp) / "repo"
            skill_root = copy_skill(temp_root, COMPONENT_SKILL)
            records_path = skill_root / "assets" / "component_records.json"
            db_path = skill_root / "assets" / "bbva_cells_components.db"
            db_hash_before = db_path.read_bytes()
            records = json.loads(records_path.read_text(encoding="utf-8"))
            records.append({"slug": "sentinel-stale-record"})
            records_path.write_text(json.dumps(records), encoding="utf-8")
            result = run(str(skill_root / "scripts" / "search_docs.py"), "--query", "sentinel", "--format", "json", cwd=temp_root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("records hash does not match", result.stderr)
            self.assertEqual(db_hash_before, db_path.read_bytes())
            self.assertFalse(list(db_path.parent.glob(f"{db_path.name}-*")))

    def test_component_manifest_revision_mismatch_fails_validator_and_search(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp_root = Path(raw_temp) / "repo"
            skill_root = copy_skill(temp_root, COMPONENT_SKILL)
            manifest_path = skill_root / "assets" / "component_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["metadata"]["source_revision"] = "different-revision"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            search = run(str(skill_root / "scripts" / "search_docs.py"), "--query", "button", "--format", "json", cwd=temp_root)
            self.assertEqual(search.returncode, 2)
            self.assertIn("metadata.source_revision", search.stderr)
            valid_zip = temp_root / "components.zip"
            make_zip(skill_root, valid_zip, COMPONENT_SKILL)
            validator = run(str(ROOT / "scripts" / "validate_component_catalog.py"), "--skill-root", str(skill_root), "--zip", str(valid_zip), cwd=temp_root)
            self.assertEqual(validator.returncode, 1)
            self.assertIn("metadata.source_revision", validator.stderr)

    def test_component_database_source_mismatch_is_rejected_even_with_updated_hash(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp_root = Path(raw_temp) / "repo"
            skill_root = copy_skill(temp_root, COMPONENT_SKILL)
            manifest_path = skill_root / "assets" / "component_manifest.json"
            db_path = skill_root / "assets" / "bbva_cells_components.db"
            import sqlite3

            connection = sqlite3.connect(db_path)
            source_json = connection.execute("SELECT source_json FROM packages LIMIT 1").fetchone()[0]
            source = json.loads(source_json)
            source["fingerprint"] = "0" * 64
            connection.execute("UPDATE packages SET source_json = ? WHERE id = 1", (json.dumps(source),))
            connection.commit()
            connection.close()
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["integrity"]["database_sha256"] = hashlib.sha256(db_path.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            search = run(str(skill_root / "scripts" / "search_docs.py"), "--query", "button", "--format", "json", cwd=temp_root)
            self.assertEqual(search.returncode, 2)
            self.assertIn("package source records do not match", search.stderr)
            valid_zip = temp_root / "components.zip"
            make_zip(skill_root, valid_zip, COMPONENT_SKILL)
            validator = run(str(ROOT / "scripts" / "validate_component_catalog.py"), "--skill-root", str(skill_root), "--zip", str(valid_zip), cwd=temp_root)
            self.assertEqual(validator.returncode, 1)
            self.assertIn("package source records do not match", validator.stderr)

    def test_official_database_revision_mismatch_is_rejected_even_with_updated_hash(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp_root = Path(raw_temp) / "repo"
            skill_root = copy_skill(temp_root, OFFICIAL_SKILL)
            manifest_path = skill_root / "assets" / "manifest.json"
            db_path = skill_root / "assets" / "cells_official_docs.db"
            import sqlite3

            connection = sqlite3.connect(db_path)
            connection.execute(
                "UPDATE metadata SET value = ? WHERE key = 'source_revision'",
                (json.dumps("different-revision"),),
            )
            connection.commit()
            connection.close()
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["integrity"]["database_sha256"] = hashlib.sha256(db_path.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            search = run(str(skill_root / "scripts" / "search_docs.py"), "--query", "testing", "--format", "json", cwd=temp_root)
            self.assertEqual(search.returncode, 2)
            self.assertIn("metadata.source_revision", search.stderr)
            valid_zip = temp_root / "official.zip"
            make_zip(skill_root, valid_zip, OFFICIAL_SKILL)
            validator = run(str(ROOT / "scripts" / "validate_official_docs_catalog.py"), "--skill-root", str(skill_root), "--zip", str(valid_zip), cwd=temp_root)
            self.assertEqual(validator.returncode, 1)
            self.assertIn("metadata.source_revision", validator.stderr)

    def test_official_fake_zip_with_expected_names_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp_root = Path(raw_temp) / "repo"
            skill_root = copy_skill(temp_root, OFFICIAL_SKILL)
            fake_zip = temp_root / "official-fake.zip"
            make_zip(skill_root, fake_zip, OFFICIAL_SKILL, fake_bytes=True)
            validator = run(str(ROOT / "scripts" / "validate_official_docs_catalog.py"), "--skill-root", str(skill_root), "--zip", str(fake_zip), cwd=temp_root)
            self.assertEqual(validator.returncode, 1)
            self.assertIn("stale or mismatched member", validator.stderr)

    def test_official_read_only_query_rejects_literal_percent_and_escapes_like(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp_root = Path(raw_temp) / "repo"
            skill_root = copy_skill(temp_root, OFFICIAL_SKILL)
            db_path = skill_root / "assets" / "cells_official_docs.db"
            before = sorted(path.name for path in db_path.parent.iterdir())
            normal = run(str(skill_root / "scripts" / "search_docs.py"), "--query", "internacionalización", "--format", "json", cwd=temp_root)
            self.assertEqual(normal.returncode, 0, normal.stderr)
            literal = run(str(skill_root / "scripts" / "search_docs.py"), "--query", "%", "--format", "json", cwd=temp_root)
            self.assertEqual(literal.returncode, 2)
            self.assertIn("Unicode letter or number", literal.stderr)
            self.assertEqual(before, sorted(path.name for path in db_path.parent.iterdir()))
            self.assertFalse(list(db_path.parent.glob(f"{db_path.name}-*")))
            module = load_module("official_search_for_test", skill_root / "scripts" / "search_docs.py")
            self.assertEqual(module.like_pattern("50%_\\"), "%50\\%\\_\\\\%")


if __name__ == "__main__":
    unittest.main()
