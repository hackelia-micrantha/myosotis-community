#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin

ROUTES = {
    "": "Field-Operated AI,",
    "whitepaper.html": "Myosotis Design Summary",
    "threat-model.html": "Myosotis Threat Model",
    ".well-known/security.txt": "Contact: mailto:security.myosotis@micrantha.com",
}


def fetch(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "myosotis-community-ci/1"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.geturl(), response.status, response.headers, response.read().decode("utf-8")


def validate(base: str) -> None:
    for route, marker in ROUTES.items():
        final_url, status, headers, body = fetch(urljoin(base, route))
        if status != 200:
            raise AssertionError(f"{route or '/'} returned {status}")
        if marker not in body:
            raise AssertionError(f"{route or '/'} missing expected marker {marker!r}")
        if not final_url.startswith("https://"):
            raise AssertionError(f"{route or '/'} did not resolve over HTTPS: {final_url}")

        if route != ".well-known/security.txt":
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
