#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def make_case() -> Path:
    root = Path(tempfile.mkdtemp(prefix="myosotis-governance-"))
    for relative in (
        "LICENSE",
        "LICENSES",
        "LICENSING.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "docs",
        ".github",
        "scripts",
    ):
        source = ROOT / relative
        target = root / relative
        if source.is_dir():
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return root


def run_validator(root: Path):
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "validate_governance.py")],
        text=True,
        capture_output=True,
        check=False,
    )


def expect_failure(name: str, mutate, expected: str) -> None:
    root = make_case()
    try:
        mutate(root)
        result = run_validator(root)
        output = result.stdout + result.stderr
        if result.returncode == 0:
            raise AssertionError(f"{name}: validator unexpectedly passed")
        if expected not in output:
            raise AssertionError(
                f"{name}: expected {expected!r} in validator output:\n{output}"
            )
    finally:
        shutil.rmtree(root)


baseline = make_case()
try:
    result = run_validator(baseline)
    if result.returncode != 0:
        raise AssertionError(
            "baseline governance policy must pass:\n"
            + result.stdout
            + result.stderr
        )
finally:
    shutil.rmtree(baseline)


def add_normative_tree(root: Path) -> None:
    path = root / "rfcs"
    path.mkdir()
    (path / "rfc_0001_public.md").write_text("# RFC\n", encoding="utf-8")


def add_rfc_like_doc(root: Path) -> None:
    (root / "docs" / "rfc_9999_accidental.md").write_text(
        "# Accidental normative source\n",
        encoding="utf-8",
    )


def enable_blank_issues(root: Path) -> None:
    path = root / ".github" / "ISSUE_TEMPLATE" / "config.yml"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace("blank_issues_enabled: false", "blank_issues_enabled: true"),
        encoding="utf-8",
    )


def remove_reference_license(root: Path) -> None:
    (root / "LICENSES" / "MPL-2.0.txt").unlink()


def weaken_pr_template(root: Path) -> None:
    path = root / ".github" / "PULL_REQUEST_TEMPLATE.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace("Rights and licensing", "Contribution"),
        encoding="utf-8",
    )


expect_failure(
    "normative source tree",
    add_normative_tree,
    "reserved normative/implementation surfaces",
)
expect_failure(
    "RFC-like document",
    add_rfc_like_doc,
    "RFC-like source file is not allowed",
)
expect_failure(
    "blank issue bypass",
    enable_blank_issues,
    "blank public issues must remain disabled",
)
expect_failure(
    "missing MPL license text",
    remove_reference_license,
    "missing governance artifact",
)
expect_failure(
    "weakened PR rights boundary",
    weaken_pr_template,
    "pull-request template missing required field",
)

print("governance adversarial tests passed")
