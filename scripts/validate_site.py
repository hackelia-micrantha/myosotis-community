#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

import html5lib
import tinycss2
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
PAGES = [WEB / "index.html", WEB / "whitepaper.html", WEB / "threat-model.html"]
TEXT_SUFFIXES = {".css", ".html", ".json", ".jsonc", ".md", ".py", ".txt", ".yaml", ".yml"}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)



def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        raise ValueError(value)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def luminance(value: str) -> float:
    channels = []
    for channel in hex_rgb(value):
        normalized = channel / 255
        channels.append(
            normalized / 12.92
            if normalized <= 0.04045
            else ((normalized + 0.055) / 1.055) ** 2.4
        )
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(foreground: str, background: str) -> float:
    first, second = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (first + 0.05) / (second + 0.05)


def css_variable(css: str, name: str) -> str | None:
    match = re.search(rf"{re.escape(name)}\s*:\s*(#[0-9a-fA-F]{{3,6}})\s*;", css)
    return match.group(1) if match else None


def parse_page(path: Path):
    text = path.read_text(encoding="utf-8")
    parser = html5lib.HTMLParser(
        tree=html5lib.getTreeBuilder("etree"),
        namespaceHTMLElements=False,
    )
    root = parser.parse(text)
    for position, code, data in parser.errors:
        fail(f"{path.relative_to(ROOT)}:{position}: HTML parse error {code}: {data}")
    return text, root


page_ids: dict[Path, set[str]] = {}
page_roots = {}

for page in PAGES:
    text, root = parse_page(page)
    page_roots[page] = root

    if root.attrib.get("lang") != "en":
        fail(f"{page.relative_to(ROOT)} must declare html lang=en")
    if root.attrib.get("data-phyllotaxis-profile") != "utility":
        fail(f"{page.relative_to(ROOT)} must declare the Phyllotaxis utility profile")
    if root.attrib.get("data-phyllotaxis-scheme") != "light":
        fail(f"{page.relative_to(ROOT)} must declare the current light scheme")

    mains = root.findall(".//main")
    h1s = root.findall(".//h1")
    if len(mains) != 1:
        fail(f"{page.relative_to(ROOT)} must contain exactly one main landmark")
    if len(h1s) != 1:
        fail(f"{page.relative_to(ROOT)} must contain exactly one h1")

    ids = [node.attrib["id"] for node in root.iter() if "id" in node.attrib]
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        fail(f"{page.relative_to(ROOT)} contains duplicate ids: {duplicates}")
    page_ids[page] = set(ids)

    skips = [
        node
        for node in root.iter("a")
        if "skip-link" in node.attrib.get("class", "").split()
    ]
    if len(skips) != 1 or skips[0].attrib.get("href") != "#main-content":
        fail(f"{page.relative_to(ROOT)} must contain one skip link to #main-content")
    if not mains or mains[0].attrib.get("id") != "main-content":
        fail(f"{page.relative_to(ROOT)} main landmark must have id=main-content")

    navs = root.findall(".//nav")
    if not navs or any(not nav.attrib.get("aria-label") for nav in navs):
        fail(f"{page.relative_to(ROOT)} navigation landmarks must have accessible labels")

    stylesheets = [
        node.attrib.get("href", "")
        for node in root.iter("link")
        if node.attrib.get("rel") == "stylesheet"
    ]
    if stylesheets != ["assets/styles.css"]:
        fail(f"{page.relative_to(ROOT)} must load only the local assets/styles.css stylesheet")

    if "fonts.googleapis.com" in text or "fonts.gstatic.com" in text:
        fail(f"{page.relative_to(ROOT)} must not depend on external font services")

for page, root in page_roots.items():
    for node in root.iter():
        for attr in ("href", "src"):
            raw = node.attrib.get(attr)
            if not raw:
                continue
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc or raw.startswith("mailto:"):
                continue

            target_path = parsed.path
            if target_path:
                target = (page.parent / unquote(target_path)).resolve()
                if not target.is_relative_to(WEB.resolve()):
                    fail(f"{page.relative_to(ROOT)} {attr} escapes web root: {raw}")
                    continue
                if not target.exists():
                    fail(f"{page.relative_to(ROOT)} references missing local target: {raw}")
                    continue
            else:
                target = page

            if parsed.fragment and target.suffix == ".html":
                target_ids = page_ids.get(target)
                if target_ids is None and target.exists():
                    _, target_root = parse_page(target)
                    target_ids = {
                        item.attrib["id"]
                        for item in target_root.iter()
                        if "id" in item.attrib
                    }
                    page_ids[target] = target_ids
                if parsed.fragment not in (target_ids or set()):
                    fail(
                        f"{page.relative_to(ROOT)} references missing fragment "
                        f"#{parsed.fragment} in {target.relative_to(ROOT)}"
                    )

css_path = WEB / "assets" / "styles.css"
css = css_path.read_text(encoding="utf-8")
for token in tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True):
    if token.type == "error":
        fail(f"{css_path.relative_to(ROOT)} CSS parse error: {token.message}")

for required in (
    ":focus-visible",
    ".skip-link:focus",
    "@media (prefers-reduced-motion: reduce)",
    "--phyllotaxis-color-focus",
):
    if required not in css:
        fail(f"{css_path.relative_to(ROOT)} missing required accessibility contract: {required}")


contrast_pairs = (
    ("--phyllotaxis-color-text", "--phyllotaxis-color-canvas", 4.5),
    ("--phyllotaxis-color-text-muted", "--phyllotaxis-color-canvas", 4.5),
    ("--phyllotaxis-color-link", "--phyllotaxis-color-canvas", 4.5),
    ("--phyllotaxis-color-link-visited", "--phyllotaxis-color-canvas", 4.5),
    ("--phyllotaxis-color-text", "--phyllotaxis-color-surface", 4.5),
    ("--phyllotaxis-color-text-muted", "--phyllotaxis-color-surface", 4.5),
)
for foreground_name, background_name, minimum in contrast_pairs:
    foreground = css_variable(css, foreground_name)
    background = css_variable(css, background_name)
    if foreground is None or background is None:
        fail(f"missing contrast token {foreground_name} or {background_name}")
        continue
    ratio = contrast_ratio(foreground, background)
    if ratio < minimum:
        fail(
            f"contrast {foreground_name} on {background_name} is {ratio:.2f}:1; "
            f"requires at least {minimum:.1f}:1"
        )

wrangler_text = (ROOT / "wrangler.jsonc").read_text(encoding="utf-8")
try:
    wrangler = json.loads(wrangler_text)
except json.JSONDecodeError as error:
    fail(f"wrangler.jsonc must remain parseable by the current JSON-only config: {error}")
else:
    if wrangler.get("name") != "myosotis-community":
        fail("wrangler.jsonc must retain the myosotis-community worker name")
    if wrangler.get("assets", {}).get("directory") != "./web":
        fail("wrangler.jsonc must serve ./web as the static asset directory")

workflow_path = ROOT / ".github" / "workflows" / "site-validation.yml"
workflow = workflow_path.read_text(encoding="utf-8")
if not re.search(r"(?m)^permissions:\s*\n\s+contents:\s+read\s*$", workflow):
    fail("site-validation workflow must default to contents: read")
for line in workflow.splitlines():
    stripped = line.strip()
    if not stripped.startswith("uses:"):
        continue
    action = stripped.split(":", 1)[1].strip()
    if not re.search(r"@[0-9a-f]{40}(?:\s+#.*)?$", action):
        fail(f"third-party action is not pinned to an immutable SHA: {action}")

headers_path = WEB / "_headers"
headers = headers_path.read_text(encoding="utf-8")
required_headers = {
    "Content-Security-Policy:": ("default-src 'none'", "frame-ancestors 'none'"),
    "Referrer-Policy:": ("no-referrer",),
    "X-Content-Type-Options:": ("nosniff",),
    "Permissions-Policy:": ("camera=()", "microphone=()", "geolocation=()"),
    "Strict-Transport-Security:": ("max-age=",),
}
for name, required_values in required_headers.items():
    line = next((line.strip() for line in headers.splitlines() if line.strip().startswith(name)), None)
    if line is None:
        fail(f"web/_headers missing {name}")
        continue
    for value in required_values:
        if value not in line:
            fail(f"web/_headers {name} missing required value {value!r}")

security_text = (WEB / ".well-known" / "security.txt").read_text(encoding="utf-8")
expires = next((line.split(":", 1)[1].strip() for line in security_text.splitlines() if line.startswith("Expires:")), None)
if expires is None:
    fail("web/.well-known/security.txt is missing Expires")
else:
    expiry = datetime.fromisoformat(expires.replace("Z", "+00:00"))
    if expiry <= datetime.now(timezone.utc):
        fail("web/.well-known/security.txt is expired")


provenance_path = WEB / "provenance.json"
claims_path = WEB / "claims.json"
provenance_schema_path = WEB / "provenance.schema.json"
claims_schema_path = WEB / "claims.schema.json"

provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
claims_document = json.loads(claims_path.read_text(encoding="utf-8"))
provenance_schema = json.loads(provenance_schema_path.read_text(encoding="utf-8"))
claims_schema = json.loads(claims_schema_path.read_text(encoding="utf-8"))

for label, schema, document in (
    ("provenance", provenance_schema, provenance),
    ("claims", claims_schema, claims_document),
):
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        fail(f"{label} schema error at {list(error.path)}: {error.message}")

source_ids = [source["id"] for source in provenance.get("sources", [])]
if len(source_ids) != len(set(source_ids)):
    fail("provenance source IDs must be unique")
known_sources = set(source_ids)

claims = claims_document.get("claims", [])
claim_ids = [claim["id"] for claim in claims]
if len(claim_ids) != len(set(claim_ids)):
    fail("public claim IDs must be unique")
claim_by_id = {claim["id"]: claim for claim in claims}

evidence = provenance.get("evidence", [])
evidence_ids = [item["id"] for item in evidence]
if len(evidence_ids) != len(set(evidence_ids)):
    fail("public evidence IDs must be unique")
evidence_by_id = {item["id"]: item for item in evidence}

confidence_rank = {
    "design": 0,
    "conformance": 1,
    "deployment": 2,
    "clinical": 3,
}
for item in evidence:
    if item["sourceRevision"] != provenance["sourceRevision"]:
        fail(
            f"evidence {item['id']} is stale relative to the site source revision"
        )
    if item["reviewedAt"] > provenance["reviewedAt"]:
        fail(
            f"evidence {item['id']} review date cannot be newer than the "
            "site provenance review date"
        )

for claim in claims:
    unknown_sources = sorted(set(claim["sourceIds"]) - known_sources)
    if unknown_sources:
        fail(f"{claim['id']} references unknown RFC sources: {unknown_sources}")
    if claim["confidence"] in {"conformance", "deployment", "clinical"} and not claim.get("evidenceRefs"):
        fail(f"{claim['id']} requires evidenceRefs at {claim['confidence']} confidence")
    if claim["confidence"] == "clinical" and not claim.get("clinicalEvidence"):
        fail(f"{claim['id']} requires governed clinicalEvidence")

    for evidence_id in claim.get("evidenceRefs", []):
        item = evidence_by_id.get(evidence_id)
        if item is None:
            fail(f"{claim['id']} references unknown evidence {evidence_id}")
            continue
        if confidence_rank[item["level"]] < confidence_rank[claim["confidence"]]:
            fail(
                f"{claim['id']} has {claim['confidence']} confidence but evidence "
                f"{evidence_id} is only {item['level']}"
            )
        if item["reviewedAt"] > claim["reviewedAt"]:
            fail(
                f"{claim['id']} was reviewed before its evidence {evidence_id}"
            )

page_manifest = {page["path"]: page for page in provenance.get("pages", [])}
if set(page_manifest) != {page.name for page in PAGES}:
    fail("provenance pages must exactly cover the public HTML pages")

used_claim_ids: set[str] = set()
for page, root in page_roots.items():
    page_name = page.name
    manifest = page_manifest.get(page_name)
    if manifest is None:
        continue

    metas = {
        node.attrib.get("name"): node.attrib.get("content")
        for node in root.findall(".//meta")
        if node.attrib.get("name", "").startswith("myosotis-")
    }
    if metas.get("myosotis-source-revision") != manifest["sourceRevision"]:
        fail(f"{page_name} source revision does not match provenance manifest")
    if metas.get("myosotis-reviewed-at") != manifest["reviewedAt"]:
        fail(f"{page_name} reviewed-at does not match provenance manifest")
    if metas.get("myosotis-publication-status") != provenance["publicationStatus"]:
        fail(f"{page_name} publication status does not match provenance manifest")

    alternates = {
        node.attrib.get("href")
        for node in root.findall(".//link")
        if node.attrib.get("rel") == "alternate"
        and node.attrib.get("type") == "application/json"
    }
    if not {"provenance.json", "claims.json"}.issubset(alternates):
        fail(f"{page_name} must link the public provenance and claims JSON")

    sections = root.findall(".//main//section")
    page_claim_ids = []
    for section in sections:
        claim_id = section.attrib.get("data-claim-id")
        confidence = section.attrib.get("data-claim-confidence")
        if not claim_id or not confidence:
            fail(f"{page_name} has an untracked substantive section")
            continue
        page_claim_ids.append(claim_id)
        used_claim_ids.add(claim_id)
        claim = claim_by_id.get(claim_id)
        if claim is None:
            fail(f"{page_name} references unknown claim {claim_id}")
            continue
        if confidence != claim["confidence"]:
            fail(
                f"{page_name} claim {claim_id} declares {confidence} confidence "
                f"but ledger records {claim['confidence']}"
            )
        if page_name not in claim["publicSurfaces"]:
            fail(f"{claim_id} does not declare {page_name} as a public surface")

    if page_claim_ids != manifest["claimIds"]:
        fail(f"{page_name} claim order/set does not match provenance manifest")

if used_claim_ids != set(claim_ids):
    missing = sorted(set(claim_ids) - used_claim_ids)
    extra = sorted(used_claim_ids - set(claim_ids))
    if missing:
        fail(f"claims ledger entries are not referenced by pages: {missing}")
    if extra:
        fail(f"pages reference claims absent from ledger: {extra}")

if provenance.get("sourceRevision") != next(
    (page["sourceRevision"] for page in provenance.get("pages", [])),
    None,
):
    fail("site-wide sourceRevision must match page sourceRevision baseline")

for page in provenance.get("pages", []):
    if page["sourceRevision"] != provenance["sourceRevision"]:
        fail(f"{page['path']} source revision is stale relative to site manifest")
    if page["reviewedAt"] != provenance["reviewedAt"]:
        fail(f"{page['path']} review date is stale relative to site manifest")

positive_clinical_patterns = (
    "is clinically validated",
    "has clinical efficacy",
    "is hipaa compliant",
    "is pipeda compliant",
    "has regulatory approval",
    "diagnoses patients",
    "treats patients",
)
for page, root in page_roots.items():
    for section in root.findall(".//main//section"):
        text = " ".join("".join(section.itertext()).lower().split())
        if any(pattern in text for pattern in positive_clinical_patterns):
            claim_id = section.attrib.get("data-claim-id")
            claim = claim_by_id.get(claim_id or "")
            if claim is None or claim.get("confidence") != "clinical":
                fail(
                    f"{page.name} contains clinical/regulatory claim language "
                    f"without clinical ledger confidence: {claim_id}"
                )


bad_names = ("Myo" + "tosis", "Mys" + "otosis")
private_repo = re.compile(r"github\.com/hackelia-micrantha/myosotis(?:[/?#\"'<>]|$)")
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
        continue
    if any(part in {".git", "result"} for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    for bad in bad_names:
        if bad in text:
            fail(f"{path.relative_to(ROOT)} contains obsolete project spelling {bad}")
    if path.is_relative_to(WEB) and private_repo.search(text):
        fail(f"{path.relative_to(ROOT)} exposes the private canonical repository path")

if errors:
    print("site validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print("site validation passed")
