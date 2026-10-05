#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def make_case() -> Path:
    root = Path(tempfile.mkdtemp(prefix="myosotis-provenance-"))
    shutil.copytree(ROOT / "web", root / "web")
    (root / "scripts").mkdir()
    shutil.copy2(ROOT / "scripts" / "validate_provenance.py", root / "scripts")
    return root


def run_validator(root: Path):
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "validate_provenance.py")],
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
            "baseline provenance must pass:\n" + result.stdout + result.stderr
        )
finally:
    shutil.rmtree(baseline)


def stale_source(root: Path) -> None:
    path = root / "web" / "provenance.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["sourceRevision"] = "0" * 40
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def unknown_rfc(root: Path) -> None:
    path = root / "web" / "provenance.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["sources"].append({"id": "RFC-999", "status": "Draft"})
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def missing_binding(root: Path) -> None:
    path = root / "web" / "index.html"
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(
        r' data-claim-id="MYO-WEB-INDEX-OVERVIEW"',
        "",
        text,
        count=1,
    )
    if count != 1:
        raise AssertionError("fixture did not contain expected claim binding")
    path.write_text(text, encoding="utf-8")


def inflate_evidence(root: Path) -> None:
    claims_path = root / "web" / "claims.json"
    claims = json.loads(claims_path.read_text(encoding="utf-8"))
    for claim in claims["claims"]:
        if claim["id"] == "MYO-WEB-INDEX-STATE":
            claim["confidence"] = "deployment"
            break
    else:
        raise AssertionError("state claim missing")
    claims_path.write_text(json.dumps(claims, indent=2) + "\n", encoding="utf-8")

    page = root / "web" / "index.html"
    text = page.read_text(encoding="utf-8")
    text = text.replace(
        'data-claim-id="MYO-WEB-INDEX-STATE" data-claim-confidence="conformance"',
        'data-claim-id="MYO-WEB-INDEX-STATE" data-claim-confidence="deployment"',
        1,
    )
    page.write_text(text, encoding="utf-8")


def clinical_without_governance(root: Path) -> None:
    claims_path = root / "web" / "claims.json"
    claims = json.loads(claims_path.read_text(encoding="utf-8"))
    for claim in claims["claims"]:
        if claim["id"] == "MYO-WEB-INDEX-STATE":
            claim["type"] = "clinical"
            claim["confidence"] = "clinical"
            break
    else:
        raise AssertionError("state claim missing")
    claims_path.write_text(json.dumps(claims, indent=2) + "\n", encoding="utf-8")

    page = root / "web" / "index.html"
    text = page.read_text(encoding="utf-8")
    text = text.replace(
        'data-claim-id="MYO-WEB-INDEX-STATE" data-claim-confidence="conformance"',
        'data-claim-id="MYO-WEB-INDEX-STATE" data-claim-confidence="clinical"',
        1,
    )
    page.write_text(text, encoding="utf-8")


expect_failure("stale source revision", stale_source, "sourceRevision is stale")
expect_failure("unknown RFC id", unknown_rfc, "unknown RFC ids")
expect_failure("missing section claim binding", missing_binding, "without claim id/confidence")
expect_failure("evidence inflation", inflate_evidence, "exceeds referenced evidence level")
expect_failure("clinical evidence governance", clinical_without_governance, "clinicalEvidence")

print("provenance adversarial contract tests passed")
