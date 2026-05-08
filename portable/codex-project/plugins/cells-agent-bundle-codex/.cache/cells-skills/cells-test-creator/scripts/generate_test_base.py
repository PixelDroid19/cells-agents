#!/usr/bin/env python3

import argparse
import os
import re
from pathlib import Path


def camel_to_kebab(value: str) -> str:
    cleaned = re.sub(r"\.test$", "", value)
    cleaned = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", cleaned)
    cleaned = cleaned.replace("_", "-")
    return cleaned.lower()


def compute_test_path(repo_root: Path, source: Path) -> Path:
    source = source.resolve()
    source_rel = source.relative_to(repo_root)
    source_rel_str = source_rel.as_posix()

    if not source_rel_str.startswith("src/"):
      raise ValueError("The source file must be under src/ to compute the mirrored path in test/")

    mirrored = Path("test") / Path(*source_rel.parts[1:])
    return repo_root / mirrored.with_name(f"{source.stem}.test.js")


def relative_import(from_dir: Path, target_file: Path) -> str:
    import_str = os.path.relpath(str(target_file), str(from_dir)).replace("\\", "/")
    return f"./{import_str}" if not import_str.startswith(".") else import_str


def build_template(component_name: str, tag_name: str, source_import: str) -> str:
    suite_name = component_name or tag_name
    return f"""import {{ assert, fixture, html, oneEvent }} from '@open-wc/testing';
import sinon from 'sinon';
import '{source_import}';

suite('{suite_name}', () => {{
  let el;

  setup(async () => {{
    el = await fixture(html`<{tag_name}></{tag_name}>`);
  }});

  teardown(() => {{
    sinon.restore();
  }});

  test('renders the component host', () => {{
    assert.exists(el);
  }});

  test('reacts to a public interaction and emits the expected event', async () => {{
    const eventPromise = oneEvent(el, 'replace-with-public-event-name');

    el.dispatchEvent(
      new CustomEvent('replace-with-public-interaction-event', {{
        bubbles: true,
        composed: true,
        detail: {{}},
      }}),
    );

    const emittedEvent = await eventPromise;
    assert.exists(emittedEvent);
  }});

  test('executes collaborator or service through public flow', () => {{
    const collaborator = {{ execute: () => {{}} }};
    const executeSpy = sinon.spy(collaborator, 'execute');

    collaborator.execute();

    assert.isTrue(executeSpy.calledOnce);
  }});

  test('covers branches for null, undefined, and empty values', () => {{
    assert.isTrue(true);
  }});

  test('covers error paths and guards through public API or events', () => {{
    assert.isTrue(true);
  }});
}});
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a base test using repository conventions")
    parser.add_argument("--source", help="Path to the source file in src/, for example src/foo/bar.js")
    parser.add_argument("--test-path", help="Final test path to create, for example test/foo/bar.test.js")
    parser.add_argument("--component-name", help="Suite name, for example MyComponent")
    parser.add_argument("--tag-name", help="Custom element tag, for example bbva-my-component")
    parser.add_argument("--force", action="store_true", help="Overwrite if the file already exists")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files, only print path and preview")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[4]

    if not args.source and not args.test_path:
        raise ValueError("You must provide --source or --test-path")

    source_file = (repo_root / args.source).resolve() if args.source else None

    if args.test_path:
        test_file = (repo_root / args.test_path).resolve()
    else:
        test_file = compute_test_path(repo_root, source_file)

    if test_file.exists() and not args.force and not args.dry_run:
        raise FileExistsError(f"Test already exists: {test_file}. Use --force to overwrite.")

    if source_file:
        import_path = relative_import(test_file.parent, source_file)
        stem = source_file.stem
    else:
        import_path = './replace-with-source-path.js'
        stem = test_file.stem.replace('.test', '')

    tag_name = args.tag_name or camel_to_kebab(stem)
    component_name = args.component_name or stem
    template = build_template(component_name, tag_name, import_path)

    if args.dry_run:
        print(f"[DRY-RUN] Destination file: {test_file}")
        if test_file.exists():
            print("[DRY-RUN] Note: file already exists and will not be modified.")
        print(template)
        return 0

    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(template, encoding="utf-8")
    print(f"Base test created: {test_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
