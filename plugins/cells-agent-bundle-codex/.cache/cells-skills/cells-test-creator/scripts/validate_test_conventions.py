#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Cells test conventions in this repository")
    parser.add_argument("--path", required=True, help="Test path, for example: test/foo/bar.test.js")
    return parser.parse_args()


def validate_location(path: Path, errors: list[str]) -> None:
    path_str = path.as_posix()
    if "/test/" not in f"/{path_str}":
        errors.append("The file must be inside the test/ directory")
    if not path_str.endswith(".test.js"):
        errors.append("The filename must end with .test.js")


def validate_structure(content: str, errors: list[str], warnings: list[str]) -> None:
    required_patterns = {
        "suite": r"\bsuite\s*\(",
        "setup": r"\bsetup\s*\(",
        "teardown": r"\bteardown\s*\(",
        "test": r"\btest\s*\(",
    }

    for label, pattern in required_patterns.items():
        if not re.search(pattern, content):
            errors.append(f"Missing minimum structure: {label}")

    if "@open-wc/testing" not in content:
        errors.append("Must import utilities from @open-wc/testing")

    has_sinon_calls = bool(re.search(r"\bsinon\.(spy|stub|useFakeTimers|replace|fake)\b", content))
    has_sinon_import = "sinon" in content
    has_teardown = bool(re.search(r"\bteardown\s*\(", content))
    has_restore = bool(re.search(r"sinon\.restore\s*\(", content))

    if has_sinon_calls and not has_sinon_import:
        errors.append("Sinon usage detected but sinon import is missing")

    if has_sinon_calls and not has_restore:
        warnings.append("Recommended: include sinon.restore() to avoid leaks between tests")

    if has_teardown and not has_restore and has_sinon_calls:
        warnings.append("teardown exists without sinon.restore() while sinon is used")


def validate_private_access(content: str, errors: list[str]) -> None:
    private_patterns = [
        r"\.\s*_[A-Za-z][A-Za-z0-9_]*",  # obj._private
        r"\[\s*['\"]_[^'\"]+['\"]\s*\]",  # obj['_private']
        r"\.\s*#[A-Za-z][A-Za-z0-9_]*",  # obj.#private
        r"\bsinon\.(?:spy|stub)\s*\([^\)]*_[A-Za-z][A-Za-z0-9_]*",  # spy/stub private
    ]

    for pattern in private_patterns:
        if re.search(pattern, content):
            errors.append("Detected access or reference to a private member (_ or #)")
            break


def validate_no_comments(content: str, errors: list[str]) -> None:
    comment_patterns = [
        r"(^|\s)//",
        r"/\*",
        r"\*/",
    ]

    for pattern in comment_patterns:
        if re.search(pattern, content, flags=re.MULTILINE):
            errors.append("Comments are not allowed in test files")
            break


def validate_english_descriptions(content: str, errors: list[str]) -> None:
    description_matches = re.findall(r"\b(?:suite|test)\s*\(\s*['\"]([^'\"]+)['\"]", content)
    invalid_markers = [
        "TODO",
        "replace-with",
    ]

    for description in description_matches:
        lowered = description.lower()
        if any(marker.lower() in lowered for marker in invalid_markers):
            errors.append(
                "suite/test descriptions must be in English and without TODO/placeholders"
            )
            break


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[4]
    file_path = (repo_root / args.path).resolve()

    errors = []
    warnings = []

    if not file_path.exists():
        errors.append(f"File does not exist: {file_path}")
    else:
        validate_location(file_path.relative_to(repo_root), errors)
        content = file_path.read_text(encoding="utf-8")
        validate_structure(content, errors, warnings)
        validate_private_access(content, errors)
        validate_no_comments(content, errors)
        validate_english_descriptions(content, errors)

    report = {
        "file": str(file_path),
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if len(errors) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
