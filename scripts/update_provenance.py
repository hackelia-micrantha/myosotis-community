#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
PAGES = ("index.html", "whitepaper.html", "threat-model.html")

parser = argparse.ArgumentParser(
    description=(
        "Apply already-approved, sanitized core provenance metadata to the public "
        "projection. This tool never reads the private canonical repository."
    )
)
parser.add_argument("--source-revision", required=True)
parser.add_argument("--reviewed-at", required=True)
parser.add_argument(
    "--source-status",
    action="append",
    default=[],
    metavar="RFC-NNN=STATUS",
    help="Update an existing public RFC status; repeat as needed.",
)
parser.add_argument(
    "--page-reviewed",
    action="append",
    default=[],
    choices=PAGES,
    help=(
        "Explicitly mark one public page reviewed against this source revision. "
        "Repeat for every page actually reviewed. Unreviewed pages intentionally "
        "remain stale and fail CI."
    ),
)
args = parser.parse_args()

if not re.fullmatch(r"[0-9a-f]{40}", args.source_revision):
    raise SystemExit("--source-revision must be a lowercase 40-character commit SHA")
try:
    date.fromisoformat(args.reviewed_at)
except ValueError as error:
    raise SystemExit("--reviewed-at must be YYYY-MM-DD") from error

provenance_path = WEB / "provenance.json"
claims_path = WEB / "claims.json"
provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
claims = json.loads(claims_path.read_text(encoding="utf-8"))

known_sources = {source["id"]: source for source in provenance["sources"]}
for assignment in args.source_status:
    try:
        source_id, status = assignment.split("=", 1)
    except ValueError as error:
        raise SystemExit(f"invalid --source-status {assignment!r}") from error
    if source_id not in known_sources:
        raise SystemExit(
            f"{source_id} is not already approved for the public source set; "
            "add it through review rather than this updater"
        )
    if status not in {"Draft", "Proposed", "Accepted", "Implemented", "Planned"}:
        raise SystemExit(f"unsupported RFC status: {status}")
    known_sources[source_id]["status"] = status

reviewed_pages = set(args.page_reviewed)
provenance["sourceRevision"] = args.source_revision
provenance["reviewedAt"] = args.reviewed_at

page_entries = {page["path"]: page for page in provenance["pages"]}
for page_name in reviewed_pages:
    page_entry = page_entries[page_name]
    page_entry["sourceRevision"] = args.source_revision
    page_entry["reviewedAt"] = args.reviewed_at

    path = WEB / page_name
    text = path.read_text(encoding="utf-8")
    text, revision_count = re.subn(
        r'(<meta name="myosotis-source-revision" content=")[0-9a-f]{40}(" />)',
        rf"\g<1>{args.source_revision}\2",
        text,
    )
    text, review_count = re.subn(
        r'(<meta name="myosotis-reviewed-at" content=")[0-9]{4}-[0-9]{2}-[0-9]{2}(" />)',
        rf"\g<1>{args.reviewed_at}\2",
        text,
    )
    if revision_count != 1 or review_count != 1:
        raise SystemExit(f"{page_name}: expected one provenance meta pair")
    path.write_text(text, encoding="utf-8")

for claim in claims["claims"]:
    surfaces = set(claim["publicSurfaces"])
    if surfaces and surfaces.issubset(reviewed_pages):
        claim["reviewedAt"] = args.reviewed_at

provenance_path.write_text(
    json.dumps(provenance, indent=2, sort_keys=False) + "\n",
    encoding="utf-8",
)
claims_path.write_text(
    json.dumps(claims, indent=2, sort_keys=False) + "\n",
    encoding="utf-8",
)

unreviewed = sorted(set(PAGES) - reviewed_pages)
print(
    "updated approved public provenance metadata; review the diff and run "
    "scripts/validate_site.py and scripts/validate_provenance.py before publication"
)
if unreviewed:
    print(
        "pages intentionally left stale until explicitly reviewed: "
        + ", ".join(unreviewed)
    )
