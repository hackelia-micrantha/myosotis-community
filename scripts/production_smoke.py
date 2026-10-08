#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]

ROUTES = {
    "": "Field-Operated AI,",
    "whitepaper.html": "Myosotis Design Summary",
    "threat-model.html": "Myosotis Threat Model",
    "assets/styles.css": "--bg: #0d1110",
    "provenance.json": "\"project\": \"Myosotis\"",
    "claims.json": "MYO-WEB-INDEX-STATE",
    "provenance.schema.json": "Myosotis public provenance manifest",
    "claims.schema.json": "Myosotis public claims ledger",
    ".well-known/security.txt": "Contact: mailto:security.myosotis@micrantha.com",
}


def fetch(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "myosotis-community-ci/1"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.geturl(), response.status, response.headers, response.read().decode("utf-8")


def validate(base: str) -> None:
    local_provenance = json.loads(
        (ROOT / "web" / "provenance.json").read_text(encoding="utf-8")
    )
    local_claims = json.loads(
        (ROOT / "web" / "claims.json").read_text(encoding="utf-8")
    )

    for route, marker in ROUTES.items():
        final_url, status, headers, body = fetch(urljoin(base, route))
        if status != 200:
            raise AssertionError(f"{route or '/'} returned {status}")
        if marker not in body:
            raise AssertionError(f"{route or '/'} missing expected marker {marker!r}")
        if not final_url.startswith("https://"):
            raise AssertionError(f"{route or '/'} did not resolve over HTTPS: {final_url}")

        if route.endswith(".html") or route == "":
            csp = headers.get("Content-Security-Policy", "")
            if "default-src 'none'" not in csp or "frame-ancestors 'none'" not in csp:
                raise AssertionError(f"{route or '/'} missing expected CSP: {csp!r}")
            if headers.get("Referrer-Policy") != "no-referrer":
                raise AssertionError(f"{route or '/'} missing Referrer-Policy")
            if headers.get("X-Content-Type-Options") != "nosniff":
                raise AssertionError(f"{route or '/'} missing nosniff")
            if not headers.get("Permissions-Policy"):
                raise AssertionError(f"{route or '/'} missing Permissions-Policy")
            if "max-age=" not in headers.get("Strict-Transport-Security", ""):
                raise AssertionError(f"{route or '/'} missing HSTS")


    remote_provenance = json.loads(fetch(urljoin(base, "provenance.json"))[3])
    remote_claims = json.loads(fetch(urljoin(base, "claims.json"))[3])
    if remote_provenance != local_provenance:
        raise AssertionError("deployed provenance.json does not match checked-out main")
    if remote_claims != local_claims:
        raise AssertionError("deployed claims.json does not match checked-out main")

    revision = local_provenance["sourceRevision"]
    for route in ("", "whitepaper.html", "threat-model.html"):
        body = fetch(urljoin(base, route))[3]
        if revision not in body:
            raise AssertionError(
                f"{route or '/'} does not publish reviewed source revision {revision}"
            )


parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="https://myosotis.micrantha.com/")
parser.add_argument("--attempts", type=int, default=12)
parser.add_argument("--delay", type=float, default=10)
args = parser.parse_args()

last_error = None
for attempt in range(1, args.attempts + 1):
    try:
        validate(args.base_url)
        print(f"production smoke passed on attempt {attempt}")
        raise SystemExit(0)
    except (AssertionError, urllib.error.URLError, TimeoutError) as exc:
        last_error = exc
        print(f"production smoke attempt {attempt}/{args.attempts} failed: {exc}")
        if attempt != args.attempts:
            time.sleep(args.delay)

raise SystemExit(f"production smoke failed: {last_error}")
