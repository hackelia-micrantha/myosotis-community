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

provenance["sourceRevision"] = args.source_revision
provenance["reviewedAt"] = args.reviewed_at
for page in provenance["pages"]:
    page["sourceRevision"] = args.source_revision
    page["reviewedAt"] = args.reviewed_at

for claim in claims["claims"]:
    claim["reviewedAt"] = args.reviewed_at

provenance_path.write_text(
    json.dumps(provenance, indent=2, sort_keys=False) + "\n",
    encoding="utf-8",
)
claims_path.write_text(
    json.dumps(claims, indent=2, sort_keys=False) + "\n",
    encoding="utf-8",
)

for page_name in PAGES:
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

print(
    "updated approved public provenance metadata; review the diff and run "
    "scripts/validate_site.py before publication"
)
