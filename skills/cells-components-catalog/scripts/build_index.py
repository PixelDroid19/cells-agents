#!/usr/bin/env python3
"""Build the portable BBVA Cells component catalog from CEM source files.

The catalog deliberately keeps its source snapshot separate from the SQLite
index. A manifest binds the records, database, and source fingerprints so a
consumer can detect a stale or partially copied bundle without needing the
original Spherica checkout.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from typing import Any, Iterable


SCHEMA_VERSION = "3"
CATALOG_ROOT = "skills/cells-components-catalog"
RECORDS_RELATIVE_PATH = f"{CATALOG_ROOT}/assets/component_records.json"
DATABASE_RELATIVE_PATH = f"{CATALOG_ROOT}/assets/bbva_cells_components.db"
MANIFEST_RELATIVE_PATH = f"{CATALOG_ROOT}/assets/component_manifest.json"
SOURCE_FILE_NAMES = ("package.json", "custom-elements.json", "README.md")
EXAMPLE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)


def find_repo_root(start: Path) -> Path:
    """Find the checkout root without persisting an absolute path."""
    current = start.resolve()
    for parent in (current, *current.parents):
        if (parent / "skills").is_dir():
            return parent
    raise FileNotFoundError("Could not locate a repository containing skills/")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_text(value: object) -> str:
    return " ".join(str(value or "").split())


def unique(values: Iterable[str]) -> list[str]:
    """Return non-empty values once, preserving source order."""
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = str(value or "").strip()
        key = normalized.casefold()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def relative_or_default(path: Path, root: Path, default: str) -> str:
    """Keep generated provenance portable even for an external output path."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return default


def write_atomic(path: Path, payload: bytes) -> Path:
    """Stage bytes beside their final destination for an atomic replacement."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_path = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    staged = Path(raw_path)
    try:
        with os.fdopen(descriptor, "wb") as target:
            target.write(payload)
            target.flush()
            os.fsync(target.fileno())
    except Exception:
        staged.unlink(missing_ok=True)
        raise
    return staged


def load_records(records_path: Path) -> list[dict[str, Any]]:
    try:
        raw = json.loads(records_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read component records {records_path}: {exc}") from exc
    if not isinstance(raw, list):
        raise ValueError("component records must be a JSON array")
    if not raw:
        raise ValueError("component records must not be empty")
    if not all(isinstance(item, dict) for item in raw):
        raise ValueError("component records must contain JSON objects")
    return raw


def source_file_fingerprint(package_dir: Path, source_root_name: str = "packages") -> dict[str, Any]:
    """Hash the source inputs that produced one portable record."""
    files: list[dict[str, str]] = []
    for name in SOURCE_FILE_NAMES:
        source = package_dir / name
        if source.is_file():
            files.append(
                {
                    "path": f"{source_root_name}/{package_dir.name}/{name}",
                    "sha256": sha256_file(source),
                }
            )
    required = {"package.json", "custom-elements.json"}
    actual = {Path(item["path"]).name for item in files}
    missing = sorted(required - actual)
    if missing:
        raise ValueError(f"{package_dir} is missing required source file(s): {', '.join(missing)}")
    digest = hashlib.sha256()
    for item in files:
        digest.update(item["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(item["sha256"].encode("ascii"))
        digest.update(b"\n")
    return {"algorithm": "sha256", "files": files, "fingerprint": digest.hexdigest()}


def aggregate_source_fingerprint(records: Iterable[dict[str, Any]]) -> str:
    """Hash record-level CEM fingerprints in stable package order."""
    digest = hashlib.sha256()
    for record in sorted(records, key=lambda item: str(item.get("slug", ""))):
        source = record.get("source") or {}
        fingerprint = str(source.get("fingerprint", ""))
        slug = str(record.get("slug", ""))
        if not slug or not fingerprint:
            raise ValueError(f"record {slug or '<unknown>'} is missing a source fingerprint")
        digest.update(slug.encode("utf-8"))
        digest.update(b"\0")
        digest.update(fingerprint.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def type_text(value: object) -> str | None:
    if isinstance(value, dict):
        text = value.get("text")
        return str(text) if text else None
    return str(value) if value else None


def source_name(value: object) -> str | None:
    if isinstance(value, dict):
        name = value.get("name")
        return str(name) if name else None
    return str(value) if value else None


def is_public(member: dict[str, Any]) -> bool:
    name = str(member.get("name") or "")
    return bool(name) and not name.startswith("_") and member.get("privacy") not in {"private", "protected"}


def category_for_slug(slug: str, category_hints: dict[str, str]) -> str:
    """Preserve existing taxonomy where available, then use stable name families."""
    hinted = category_hints.get(slug)
    if hinted:
        return hinted
    families = (
        ("bbva-form-", "forms"),
        ("bbva-button-", "buttons"),
        ("bbva-badge-", "badges"),
        ("bbva-chat-", "chat"),
        ("bbva-clip-", "media"),
        ("bbva-data-visualization-", "data-visualization"),
        ("bbva-expandable-", "expandable"),
        ("bbva-header-", "headers"),
        ("bbva-help-", "help"),
        ("bbva-list-", "lists"),
        ("bbva-map-", "maps"),
        ("bbva-navigation-", "navigation"),
        ("bbva-notification-", "notifications"),
        ("bbva-panel-", "panels"),
        ("bbva-progress-", "progress"),
        ("bbva-table-", "tables"),
        ("bbva-type-", "typography"),
    )
    for prefix, category in families:
        if slug.startswith(prefix):
            return category
    if "mixin" in slug:
        return "mixins"
    if slug.startswith(("bbva-ambient-", "bbva-divider-")):
        return "foundations"
    return "other"


def read_category_hints(records_path: Path) -> dict[str, str]:
    """Use the prior catalog taxonomy only as a stable display classification."""
    if not records_path.is_file():
        return {}
    try:
        records = load_records(records_path)
    except ValueError:
        return {}
    return {
        str(record.get("slug")): str(record.get("category"))
        for record in records
        if record.get("slug") and record.get("category")
    }


def class_declarations(cem: dict[str, Any]) -> list[dict[str, Any]]:
    declarations: list[dict[str, Any]] = []
    for module in cem.get("modules", []):
        if not isinstance(module, dict):
            continue
        for declaration in module.get("declarations", []):
            if isinstance(declaration, dict) and declaration.get("kind") == "class":
                declarations.append(declaration)
    return declarations


def custom_elements(cem: dict[str, Any]) -> list[str]:
    """Get tags from CEM custom-element-definition entry modules."""
    names: list[str] = []
    for module in cem.get("modules", []):
        if not isinstance(module, dict):
            continue
        module_path = str(module.get("path") or "")
        module_stem = Path(module_path).stem
        for export in module.get("exports", []):
            if not isinstance(export, dict) or export.get("kind") != "custom-element-definition":
                continue
            tag = export.get("tagName") or export.get("name")
            if not tag:
                declaration = export.get("declaration")
                if isinstance(declaration, dict):
                    tag = declaration.get("tagName")
            names.append(str(tag or module_stem))
    return unique(name for name in names if name and name != "index")


def public_properties(class_name: str, declaration: dict[str, Any]) -> list[dict[str, Any]]:
    properties: list[dict[str, Any]] = []
    for member in declaration.get("members", []):
        if not isinstance(member, dict) or member.get("kind") != "field" or member.get("static") or not is_public(member):
            continue
        attribute = member.get("attribute")
        properties.append(
            {
                "class_name": class_name,
                "name": str(member["name"]),
                "attribute": str(attribute) if isinstance(attribute, str) else None,
                "type": type_text(member.get("type")),
                "default": member.get("default"),
                "description": normalize_text(member.get("description")),
                "reflects": bool(member.get("reflects")),
                "readonly": bool(member.get("readonly")),
            }
        )
    return properties


def public_methods(class_name: str, declaration: dict[str, Any]) -> list[dict[str, Any]]:
    methods: list[dict[str, Any]] = []
    for member in declaration.get("members", []):
        if not isinstance(member, dict) or member.get("kind") != "method" or member.get("static") or not is_public(member):
            continue
        parameters: list[dict[str, Any]] = []
        for parameter in member.get("parameters", []):
            if not isinstance(parameter, dict) or not parameter.get("name"):
                continue
            payload: dict[str, Any] = {"name": str(parameter["name"])}
            parameter_type = type_text(parameter.get("type"))
            if parameter_type:
                payload["type"] = parameter_type
            if parameter.get("default") is not None:
                payload["default"] = parameter["default"]
            if parameter.get("description"):
                payload["description"] = normalize_text(parameter["description"])
            parameters.append(payload)
        payload = {"class_name": class_name, "name": str(member["name"]), "parameters": parameters}
        return_type = type_text(member.get("return"))
        if return_type:
            payload["return_type"] = return_type
        if member.get("description"):
            payload["description"] = normalize_text(member["description"])
        inherited = source_name(member.get("inheritedFrom"))
        if inherited:
            payload["inherited_from"] = inherited
        methods.append(payload)
    return methods


def class_events(class_name: str, declaration: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for event in declaration.get("events", []):
        if not isinstance(event, dict) or not event.get("name"):
            continue
        payload: dict[str, Any] = {
            "class_name": class_name,
            "name": str(event["name"]),
            "type": type_text(event.get("type")),
            "description": normalize_text(event.get("description")),
        }
        inherited = source_name(event.get("inheritedFrom"))
        if inherited:
            payload["inherited_from"] = inherited
        events.append(payload)
    return events


def class_css_properties(class_name: str, declaration: dict[str, Any]) -> list[dict[str, Any]]:
    properties: list[dict[str, Any]] = []
    for css_property in declaration.get("cssProperties", []):
        if not isinstance(css_property, dict) or not css_property.get("name"):
            continue
        properties.append(
            {
                "class_name": class_name,
                "name": str(css_property["name"]),
                "type": type_text(css_property.get("type")),
                "default": css_property.get("default"),
                "description": normalize_text(css_property.get("description")),
            }
        )
    return properties


def source_examples(readme_path: Path) -> list[str]:
    """Retain short source-authored README snippets instead of inventing usage."""
    if not readme_path.is_file():
        return []
    text = readme_path.read_text(encoding="utf-8")
    examples: list[str] = []
    for match in EXAMPLE_RE.finditer(text):
        example = match.group(1).strip()
        if example:
            examples.append(example[:1600])
        if len(examples) == 2:
            break
    return examples


def extract_record(package_dir: Path, category_hints: dict[str, str]) -> dict[str, Any]:
    """Extract one source-backed record from package.json and CEM."""
    try:
        package = json.loads((package_dir / "package.json").read_text(encoding="utf-8"))
        cem = json.loads((package_dir / "custom-elements.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not parse component package {package_dir}: {exc}") from exc
    if not isinstance(package, dict) or not isinstance(cem, dict):
        raise ValueError(f"component package {package_dir} must contain JSON objects")

    slug = package_dir.name
    npm_package = str(package.get("name") or slug)
    declarations = class_declarations(cem)
    classes = unique(str(declaration.get("name")) for declaration in declarations if declaration.get("name"))
    description = normalize_text(package.get("description"))
    if not description:
        description = next(
            (normalize_text(declaration.get("description")) for declaration in declarations if declaration.get("description")),
            "",
        )

    properties: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    methods: list[dict[str, Any]] = []
    css_properties: list[dict[str, Any]] = []
    mixins: list[str] = []
    for declaration in declarations:
        class_name = str(declaration.get("name") or "")
        if not class_name:
            continue
        properties.extend(public_properties(class_name, declaration))
        events.extend(class_events(class_name, declaration))
        methods.extend(public_methods(class_name, declaration))
        css_properties.extend(class_css_properties(class_name, declaration))
        for mixin in declaration.get("mixins", []):
            name = source_name(mixin)
            if name:
                mixins.append(name)
        superclass = source_name(declaration.get("superclass"))
        if superclass:
            mixins.append(f"extends:{superclass}")

    keywords = [str(item) for item in package.get("keywords", []) if isinstance(item, str)]
    dependencies = [
        name
        for name in sorted((package.get("dependencies") or {}).keys())
        if isinstance(name, str) and name.startswith("@bbva")
    ]
    fingerprint = source_file_fingerprint(package_dir)
    return {
        "slug": slug,
        "npm_package": npm_package,
        "version": package.get("version"),
        "category": category_for_slug(slug, category_hints),
        "description": description,
        "keywords": unique(keywords),
        "dependencies": dependencies,
        "custom_elements": custom_elements(cem),
        "classes": classes,
        "properties": properties,
        "events": events,
        "methods": methods,
        "css_properties": css_properties,
        "mixins": unique(mixins),
        "usage_examples": source_examples(package_dir / "README.md"),
        "source": fingerprint,
        "catalog_record": f"{RECORDS_RELATIVE_PATH}#{slug}",
    }


def records_from_packages(packages_root: Path, category_hints: dict[str, str]) -> list[dict[str, Any]]:
    if not packages_root.is_dir():
        raise ValueError(f"--packages-root does not exist or is not a directory: {packages_root}")
    packages = sorted(path for path in packages_root.iterdir() if path.is_dir())
    records = [extract_record(package, category_hints) for package in packages]
    if not records:
        raise ValueError(f"no component packages found under {packages_root}")
    slugs = [record["slug"] for record in records]
    if len(set(slugs)) != len(slugs):
        raise ValueError("component source contains duplicate package slugs")
    return records


def render_records(records: list[dict[str, Any]]) -> bytes:
    return (json.dumps(records, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def summarize_record(record: dict[str, Any]) -> str:
    prop_names = ", ".join(item.get("name", "") for item in record.get("properties", [])[:8] if item.get("name")) or "None detected"
    event_names = ", ".join(item.get("name", "") for item in record.get("events", [])[:6] if item.get("name")) or "None detected"
    elements = ", ".join(record.get("custom_elements", [])[:8]) or "None detected"
    return "\n".join(
        [
            f"# {record['slug']}",
            "",
            f"- Package: `{record['npm_package']}`",
            f"- Version: `{record.get('version') or 'unknown'}`",
            f"- Category: `{record.get('category') or 'other'}`",
            f"- Description: {record.get('description') or 'No description found.'}",
            f"- Custom elements: {elements}",
            f"- Key properties: {prop_names}",
            f"- Key events: {event_names}",
            f"- Catalog record: `{record.get('catalog_record')}`",
        ]
    )


def make_search_text(record: dict[str, Any], summary_markdown: str) -> str:
    parts = [
        record.get("slug", ""),
        record.get("npm_package", ""),
        record.get("category", ""),
        record.get("description", ""),
        " ".join(record.get("keywords", [])),
        " ".join(record.get("dependencies", [])),
        " ".join(record.get("custom_elements", [])),
        " ".join(record.get("classes", [])),
        " ".join(item.get("name", "") for item in record.get("properties", [])),
        " ".join(item.get("name", "") for item in record.get("events", [])),
        " ".join(item.get("name", "") for item in record.get("css_properties", [])),
        " ".join(record.get("mixins", [])),
        summary_markdown,
    ]
    return normalize_text(" ".join(parts))


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            npm_package TEXT NOT NULL,
            version TEXT,
            category TEXT,
            description TEXT,
            keywords_json TEXT NOT NULL,
            dependencies_json TEXT NOT NULL,
            custom_elements_json TEXT NOT NULL,
            classes_json TEXT NOT NULL,
            properties_json TEXT NOT NULL,
            events_json TEXT NOT NULL,
            methods_json TEXT NOT NULL,
            css_properties_json TEXT NOT NULL,
            mixins_json TEXT NOT NULL,
            usage_examples_json TEXT NOT NULL,
            catalog_record TEXT NOT NULL,
            source_json TEXT NOT NULL,
            summary_markdown TEXT NOT NULL,
            search_text TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE package_fts USING fts5(
            package_id UNINDEXED,
            slug,
            npm_package,
            category,
            description,
            custom_elements,
            class_names,
            property_names,
            event_names,
            css_property_names,
            keywords,
            dependencies,
            usage_examples,
            summary_markdown,
            search_text,
            tokenize = 'porter unicode61 remove_diacritics 2'
        );
        """
    )


def insert_metadata(conn: sqlite3.Connection, metadata: dict[str, Any]) -> None:
    for key, value in metadata.items():
        conn.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", (key, json.dumps(value, ensure_ascii=True)))


def json_field(record: dict[str, Any], name: str) -> str:
    return json.dumps(record.get(name, []), ensure_ascii=True, separators=(",", ":"))


def build_database(db_path: Path, records: list[dict[str, Any]], metadata: dict[str, Any]) -> Path:
    """Build a complete database in a staged file and return that file."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_path = tempfile.mkstemp(prefix=f".{db_path.name}.", suffix=".tmp", dir=db_path.parent)
    os.close(descriptor)
    staged = Path(raw_path)
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(staged)
        create_schema(conn)
        for record in records:
            summary_markdown = summarize_record(record)
            search_text = make_search_text(record, summary_markdown)
            cursor = conn.execute(
                """
                INSERT INTO packages (
                    slug, npm_package, version, category, description,
                    keywords_json, dependencies_json, custom_elements_json, classes_json,
                    properties_json, events_json, methods_json, css_properties_json,
                    mixins_json, usage_examples_json, catalog_record, source_json,
                    summary_markdown, search_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["slug"], record["npm_package"], record.get("version"), record.get("category"), record.get("description"),
                    json_field(record, "keywords"), json_field(record, "dependencies"), json_field(record, "custom_elements"), json_field(record, "classes"),
                    json_field(record, "properties"), json_field(record, "events"), json_field(record, "methods"), json_field(record, "css_properties"),
                    json_field(record, "mixins"), json_field(record, "usage_examples"),
                    str(record.get("catalog_record") or f"{RECORDS_RELATIVE_PATH}#{record['slug']}"), canonical_json(record.get("source") or {}),
                    summary_markdown, search_text,
                ),
            )
            package_id = int(cursor.lastrowid)
            conn.execute(
                """
                INSERT INTO package_fts (
                    package_id, slug, npm_package, category, description,
                    custom_elements, class_names, property_names, event_names,
                    css_property_names, keywords, dependencies, usage_examples,
                    summary_markdown, search_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    package_id, record["slug"], record["npm_package"], record.get("category", ""), record.get("description", ""),
                    " ".join(record.get("custom_elements", [])), " ".join(record.get("classes", [])),
                    " ".join(item.get("name", "") for item in record.get("properties", [])),
                    " ".join(item.get("name", "") for item in record.get("events", [])),
                    " ".join(item.get("name", "") for item in record.get("css_properties", [])),
                    " ".join(record.get("keywords", [])), " ".join(record.get("dependencies", [])),
                    " ".join(record.get("usage_examples", [])), summary_markdown, search_text,
                ),
            )
        insert_metadata(conn, metadata)
        conn.commit()
        conn.close()
        conn = None
        return staged
    except Exception:
        if conn is not None:
            conn.close()
        staged.unlink(missing_ok=True)
        raise


def manifest_payload(
    root: Path, records_path: Path, db_path: Path, records: list[dict[str, Any]], metadata: dict[str, Any], records_sha256: str, database_sha256: str
) -> dict[str, Any]:
    return {
        "metadata": {
            "schema_version": metadata["schema_version"],
            "generated_at": metadata["generated_at"],
            "generator": relative_or_default(Path(__file__), root, f"{CATALOG_ROOT}/scripts/build_index.py"),
            "source_root": metadata["source_root"],
            "source_revision": metadata["source_revision"],
            "source_fingerprint": metadata["source_fingerprint"],
        },
        "database": relative_or_default(db_path, root, DATABASE_RELATIVE_PATH),
        "source_records": relative_or_default(records_path, root, RECORDS_RELATIVE_PATH),
        "package_count": len(records),
        "integrity": {
            "algorithm": "sha256",
            "records_sha256": records_sha256,
            "database_sha256": database_sha256,
            "source_fingerprint": metadata["source_fingerprint"],
        },
        "packages": [
            {"slug": record["slug"], "package": record["npm_package"], "category": record.get("category"), "source_fingerprint": (record.get("source") or {}).get("fingerprint")}
            for record in records
        ],
    }


def build_catalog(
    records_path: Path,
    db_path: Path,
    manifest_path: Path,
    records: list[dict[str, Any]],
    records_bytes: bytes,
    source_revision: str,
    source_root: str = "packages",
    write_records: bool = False,
) -> dict[str, Any]:
    """Stage records, database, and manifest before replacing any live asset."""
    root = find_repo_root(Path(__file__).resolve().parent)
    source_fingerprint = aggregate_source_fingerprint(records)
    records_sha256 = sha256_bytes(records_bytes)
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "source_root": source_root,
        "source_revision": source_revision,
        "source_fingerprint": source_fingerprint,
        "records_sha256": records_sha256,
        "package_count": len(records),
    }
    staged_records: Path | None = None
    staged_db: Path | None = None
    staged_manifest: Path | None = None
    database_sha256 = ""
    try:
        if write_records:
            staged_records = write_atomic(records_path, records_bytes)
        staged_db = build_database(db_path, records, metadata)
        database_sha256 = sha256_file(staged_db)
        manifest = manifest_payload(root, records_path, db_path, records, metadata, records_sha256, database_sha256)
        staged_manifest = write_atomic(manifest_path, (json.dumps(manifest, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))

        # The manifest is the completion marker. A reader encountering a build
        # in progress sees a mismatch and gets a rebuild instruction instead of
        # a silently mixed catalog.
        if staged_records is not None:
            os.replace(staged_records, records_path)
            staged_records = None
        os.replace(staged_db, db_path)
        staged_db = None
        os.replace(staged_manifest, manifest_path)
        staged_manifest = None
    finally:
        for staged in (staged_records, staged_db, staged_manifest):
            if staged is not None:
                staged.unlink(missing_ok=True)
    return {
        "status": "ok", "schema_version": SCHEMA_VERSION, "packages": len(records), "source_revision": source_revision,
        "source_fingerprint": source_fingerprint, "records_sha256": records_sha256, "database_sha256": database_sha256,
    }


def build_index(
    records_path: Path, db_path: Path, manifest_path: Path, *, source_root: str | None = None, source_revision: str | None = None
) -> dict[str, Any]:
    """Compatibility API to build an index from an already bundled record file."""
    records = load_records(records_path)
    return build_catalog(
        records_path, db_path, manifest_path, records, records_path.read_bytes(), source_revision or "bundled-records", source_root or "packages", write_records=False
    )


def parse_args() -> argparse.Namespace:
    root = find_repo_root(Path(__file__).resolve().parent)
    parser = argparse.ArgumentParser(description="Build a portable BBVA Cells component SQLite FTS5 catalog")
    parser.add_argument("--packages-root", type=Path, help="Spherica packages directory to ingest from package.json and CEM")
    parser.add_argument("--source-records", type=Path, default=root / RECORDS_RELATIVE_PATH, help="Bundled component_records.json input or generated output")
    parser.add_argument("--db", type=Path, default=root / DATABASE_RELATIVE_PATH, help="Target SQLite database")
    parser.add_argument("--manifest", type=Path, default=root / MANIFEST_RELATIVE_PATH, help="Target manifest JSON")
    parser.add_argument("--source-revision", help="Source snapshot identifier; defaults to the packages parent directory name")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.packages_root:
            packages_root = args.packages_root.resolve()
            records = records_from_packages(packages_root, read_category_hints(args.source_records))
            result = build_catalog(
                args.source_records.resolve(), args.db.resolve(), args.manifest.resolve(), records, render_records(records),
                args.source_revision or packages_root.parent.name or "external-snapshot", source_root="packages", write_records=True,
            )
        else:
            result = build_index(args.source_records.resolve(), args.db.resolve(), args.manifest.resolve(), source_revision=args.source_revision)
    except (OSError, ValueError, sqlite3.DatabaseError) as exc:
        print(f"error: {exc}", file=os.sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
