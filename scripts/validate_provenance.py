#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import html5lib
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
PAGES = ("index.html", "whitepaper.html", "threat-model.html")
CONFIDENCE_RANK = {
    "design": 0,
    "conformance": 1,
    "deployment": 2,
    "clinical": 3,
}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_json(name: str):
    path = WEB / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {error}")
        return None


def validate_json(instance, schema, label: str) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as error:
        fail(f"{label} schema is invalid: {error}")
        return
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        fail(f"{label} schema violation at {location}: {error.message}")


def unique_by(items, key: str, label: str):
    result = {}
    for item in items:
        value = item.get(key)
        if value in result:
            fail(f"duplicate {label} {value!r}")
        else:
            result[value] = item
    return result


def parse_page(page_name: str):
    path = WEB / page_name
    text = path.read_text(encoding="utf-8")
    parser = html5lib.HTMLParser(
        tree=html5lib.getTreeBuilder("etree"),
        namespaceHTMLElements=False,
    )
    root = parser.parse(text)
    for position, code, data in parser.errors:
        fail(f"{path.relative_to(ROOT)}:{position}: HTML parse error {code}: {data}")
    return text, root


provenance = load_json("provenance.json")
claims_doc = load_json("claims.json")
provenance_schema = load_json("provenance.schema.json")
claims_schema = load_json("claims.schema.json")

if all(item is not None for item in (provenance, provenance_schema)):
    validate_json(provenance, provenance_schema, "provenance")
if all(item is not None for item in (claims_doc, claims_schema)):
    validate_json(claims_doc, claims_schema, "claims")

if provenance is None or claims_doc is None:
    raise SystemExit(1)

source_by_id = unique_by(provenance.get("sources", []), "id", "source id")
evidence_by_id = unique_by(provenance.get("evidence", []), "id", "evidence id")
page_by_path = unique_by(provenance.get("pages", []), "path", "page path")
claim_by_id = unique_by(claims_doc.get("claims", []), "id", "claim id")

expected_pages = set(PAGES)
manifest_pages = set(page_by_path)
if manifest_pages != expected_pages:
    fail(
        "provenance pages must exactly match deployed HTML pages: "
        f"expected {sorted(expected_pages)}, got {sorted(manifest_pages)}"
    )

today = date.today()
for label, value in [
    ("provenance reviewedAt", provenance.get("reviewedAt")),
    *[
        (f"{page_name} reviewedAt", page.get("reviewedAt"))
        for page_name, page in page_by_path.items()
    ],
    *[
        (f"{claim_id} reviewedAt", claim.get("reviewedAt"))
        for claim_id, claim in claim_by_id.items()
    ],
]:
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        continue
    if parsed > today:
        fail(f"{label} cannot be in the future: {value}")

for evidence_id, evidence in evidence_by_id.items():
    try:
        reviewed = date.fromisoformat(evidence["reviewedAt"])
    except (KeyError, TypeError, ValueError):
        continue
    if reviewed > today:
        fail(f"{evidence_id} reviewedAt cannot be in the future")
    if evidence.get("sourceRevision") != provenance.get("sourceRevision"):
        fail(
            f"{evidence_id} is stale relative to provenance sourceRevision: "
            f"{evidence.get('sourceRevision')} != {provenance.get('sourceRevision')}"
        )

referenced_claims: dict[str, set[str]] = {claim_id: set() for claim_id in claim_by_id}

for page_name in PAGES:
    text, root = parse_page(page_name)
    page_meta = page_by_path.get(page_name)
    if page_meta is None:
        continue

    if page_meta.get("sourceRevision") != provenance.get("sourceRevision"):
        fail(
            f"{page_name} sourceRevision is stale: "
            f"{page_meta.get('sourceRevision')} != {provenance.get('sourceRevision')}"
        )

    def meta_content(name: str) -> str | None:
        matches = [
            node.attrib.get("content")
            for node in root.findall(".//meta")
            if node.attrib.get("name") == name
        ]
        if len(matches) != 1:
            fail(f"{page_name} must contain exactly one meta[name={name!r}]")
            return None
        return matches[0]

    source_revision = meta_content("myosotis-source-revision")
    reviewed_at = meta_content("myosotis-reviewed-at")
    publication_status = meta_content("myosotis-publication-status")

    if source_revision != page_meta.get("sourceRevision"):
        fail(f"{page_name} source revision meta does not match provenance manifest")
    if reviewed_at != page_meta.get("reviewedAt"):
        fail(f"{page_name} review-date meta does not match provenance manifest")
    if publication_status != provenance.get("publicationStatus"):
        fail(f"{page_name} publication-status meta does not match provenance manifest")

    alternates = {
        node.attrib.get("href")
        for node in root.findall(".//link")
        if node.attrib.get("rel") == "alternate"
        and node.attrib.get("type") == "application/json"
    }
    for required in ("provenance.json", "claims.json"):
        if required not in alternates:
            fail(f"{page_name} must advertise {required} as application/json metadata")

    sections = root.findall(".//section")
    section_claims: list[str] = []
    for section in sections:
        claim_id = section.attrib.get("data-claim-id")
        confidence = section.attrib.get("data-claim-confidence")
        if not claim_id or not confidence:
            fail(f"{page_name} contains a section without claim id/confidence metadata")
            continue
        if claim_id in section_claims:
            fail(f"{page_name} repeats claim id {claim_id}")
        section_claims.append(claim_id)

        claim = claim_by_id.get(claim_id)
        if claim is None:
            fail(f"{page_name} references unknown claim {claim_id}")
            continue

        referenced_claims.setdefault(claim_id, set()).add(page_name)
        if page_name not in claim.get("publicSurfaces", []):
            fail(f"{claim_id} does not declare {page_name} as a public surface")
        if confidence != claim.get("confidence"):
            fail(
                f"{page_name} {claim_id} confidence {confidence!r} "
                f"does not match ledger {claim.get('confidence')!r}"
            )

        section_text = " ".join(
            text_fragment.strip()
            for text_fragment in section.itertext()
            if text_fragment.strip()
        )
        if confidence != "clinical":
            prohibited_assertions = (
                r"\b(?:is|are)\s+HIPAA[- ]compliant\b",
                r"\b(?:is|are)\s+PIPEDA[- ]compliant\b",
                r"\bclinically\s+(?:validated|proven|effective)\b",
                r"\b(?:has|have)\s+clinical\s+efficacy\b",
                r"\b(?:is|are)\s+regulator(?:y|ily)\s+approved\b",
                r"\bproduction[- ]ready\b",
            )
            for pattern in prohibited_assertions:
                if re.search(pattern, section_text, flags=re.IGNORECASE):
                    fail(
                        f"{page_name} {claim_id} contains a clinical/production "
                        "assertion without clinical evidence"
                    )

    if section_claims != page_meta.get("claimIds"):
        fail(
            f"{page_name} section claim order does not match provenance manifest: "
            f"{section_claims} != {page_meta.get('claimIds')}"
        )

known_sources = set(source_by_id)
known_evidence = set(evidence_by_id)

for claim_id, claim in claim_by_id.items():
    unknown_sources = sorted(set(claim.get("sourceIds", [])) - known_sources)
    if unknown_sources:
        fail(f"{claim_id} references unapproved RFC ids: {unknown_sources}")

    declared_surfaces = set(claim.get("publicSurfaces", []))
    actual_surfaces = referenced_claims.get(claim_id, set())
    if declared_surfaces != actual_surfaces:
        fail(
            f"{claim_id} surface mismatch: declared {sorted(declared_surfaces)}, "
            f"referenced {sorted(actual_surfaces)}"
        )

    for surface in declared_surfaces:
        page = page_by_path.get(surface)
        if page is None:
            continue
        try:
            claim_date = date.fromisoformat(claim["reviewedAt"])
            page_date = date.fromisoformat(page["reviewedAt"])
        except (KeyError, TypeError, ValueError):
            continue
        if claim_date > page_date:
            fail(
                f"{claim_id} review date {claim_date} is newer than its "
                f"surface review date {page_date}"
            )

    confidence = claim.get("confidence")
    claim_type = claim.get("type")
    evidence_refs = claim.get("evidenceRefs", [])

    if confidence in CONFIDENCE_RANK and CONFIDENCE_RANK[confidence] > 0:
        if not evidence_refs:
            fail(f"{claim_id} has {confidence} confidence without evidenceRefs")

    unknown_evidence = sorted(set(evidence_refs) - known_evidence)
    if unknown_evidence:
        fail(f"{claim_id} references unknown evidence ids: {unknown_evidence}")

    if evidence_refs and confidence in CONFIDENCE_RANK:
        strongest = max(
            (CONFIDENCE_RANK[evidence_by_id[evidence]["level"]]
             for evidence in evidence_refs
             if evidence in evidence_by_id),
            default=-1,
        )
        if strongest < CONFIDENCE_RANK[confidence]:
            fail(
                f"{claim_id} confidence {confidence} exceeds referenced evidence level"
            )
        try:
            claim_date = date.fromisoformat(claim["reviewedAt"])
        except (KeyError, TypeError, ValueError):
            claim_date = None
        if claim_date is not None:
            for evidence_id in evidence_refs:
                evidence = evidence_by_id.get(evidence_id)
                if evidence is None:
                    continue
                try:
                    evidence_date = date.fromisoformat(evidence["reviewedAt"])
                except (KeyError, TypeError, ValueError):
                    continue
                if evidence_date > claim_date:
                    fail(
                        f"{claim_id} was reviewed before referenced evidence "
                        f"{evidence_id}"
                    )

    minimum_type_confidence = {
        "conformance": "conformance",
        "deployment": "deployment",
        "clinical": "clinical",
    }.get(claim_type)
    if (
        minimum_type_confidence
        and confidence in CONFIDENCE_RANK
        and CONFIDENCE_RANK[confidence] < CONFIDENCE_RANK[minimum_type_confidence]
    ):
        fail(
            f"{claim_id} type {claim_type} requires at least "
            f"{minimum_type_confidence} confidence"
        )

if errors:
    print("provenance validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    f"provenance validation passed: {len(page_by_path)} pages, "
    f"{len(claim_by_id)} claims, {len(source_by_id)} RFC sources, "
    f"{len(evidence_by_id)} evidence records"
)
