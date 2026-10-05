#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


required_files = (
    "LICENSE",
    "LICENSING.md",
    "LICENSES/MPL-2.0.txt",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "docs/public-artifact-boundary.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/public-change.yml",
    ".github/ISSUE_TEMPLATE/publication-review.yml",
)
for relative in required_files:
    if not (ROOT / relative).is_file():
        fail(f"missing governance artifact: {relative}")

license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
if "Apache License" not in license_text or "Version 2.0" not in license_text:
    fail("LICENSE must remain Apache License 2.0")

licensing = (ROOT / "LICENSING.md").read_text(encoding="utf-8")
for marker in (
    "Website source",
    "Prose documentation",
    "First-party diagrams and media",
    "Examples and synthetic fixtures",
    "Public JSON schemas",
    "Future sanitized protocol schemas",
    "Future SDK/reference implementation source",
    "MPL-2.0",
    "No Contributor License Agreement (CLA) or Developer Certificate of Origin (DCO) sign-off is currently required",
):
    if marker not in licensing:
        fail(f"LICENSING.md missing required boundary marker: {marker}")

contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
for marker in (
    "not** the normative protocol repository",
    "What requires explicit publication review",
    "What must never be published here",
    "Public proposal to canonical decision",
    "No CLA or DCO sign-off is currently required",
):
    if marker not in contributing:
        fail(f"CONTRIBUTING.md missing required boundary marker: {marker}")

boundary = (ROOT / "docs" / "public-artifact-boundary.md").read_text(encoding="utf-8")
for marker in (
    "Stage 1",
    "Stage 2",
    "Stage 3",
    "normative authority",
    "Sanitization review",
    "Proposal/import flow",
):
    if marker not in boundary:
        fail(f"public artifact boundary missing required marker: {marker}")

reserved_top_level = {
    "rfcs",
    "protocol",
    "protocols",
    "spec",
    "sdk",
    "schemas",
    "fixtures",
    "conformance",
    "reference",
    "reference-client",
    "reference-clients",
    "src",
    "crates",
}
present_reserved = sorted(
    name for name in reserved_top_level if (ROOT / name).exists()
)
if present_reserved:
    fail(
        "reserved normative/implementation surfaces require an explicit "
        "public-boundary decision before publication: "
        + ", ".join(present_reserved)
    )

for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    if path.name.lower().startswith("rfc_") and path.suffix.lower() in {".md", ".txt", ".json", ".yaml", ".yml"}:
        fail(
            "RFC-like source file is not allowed in the Stage 1 public surface: "
            + str(path.relative_to(ROOT))
        )

issue_config = (ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml").read_text(encoding="utf-8")
if "blank_issues_enabled: false" not in issue_config:
    fail("blank public issues must remain disabled so boundary/provenance fields cannot be bypassed")

pr_template = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
for marker in (
    "Authority and boundary",
    "Provenance and evidence",
    "Privacy, healthcare, and security",
    "Compatibility",
    "Rights and licensing",
    "right to submit",
):
    if marker not in pr_template:
        fail(f"pull-request template missing required field: {marker}")

public_issue = (
    ROOT / ".github" / "ISSUE_TEMPLATE" / "public-change.yml"
).read_text(encoding="utf-8")
publication_issue = (
    ROOT / ".github" / "ISSUE_TEMPLATE" / "publication-review.yml"
).read_text(encoding="utf-8")
for marker in (
    "Provenance and source",
    "Highest evidence confidence affected",
    "Privacy, healthcare, and security impact",
    "Compatibility impact",
    "cannot create a normative Myosotis protocol or SDK requirement",
):
    if marker not in public_issue:
        fail(f"public-change issue form missing required field: {marker}")

for marker in (
    "Canonical source and revision",
    "Intended authority",
    "Highest evidence confidence",
    "Sanitization and disclosure review",
    "Compatibility and synchronization",
    "does not itself transfer normative authority",
):
    if marker not in publication_issue:
        fail(f"publication-review issue form missing required field: {marker}")

if errors:
    print("governance boundary validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print("governance boundary validation passed")
