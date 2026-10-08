#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:4173/"
SCREENSHOTS_DIR = os.environ.get("MYOSOTIS_SCREENSHOTS_DIR")
ROUTES = {
    "index.html": "Field-Operated AI, Bounded at the Device",
    "whitepaper.html": "Myosotis Design Summary",
    "threat-model.html": "Myosotis Threat Model",
}


def driver(width: int, height: int):
    chromium = shutil.which("chromium")
    chromedriver = shutil.which("chromedriver")
    assert chromium, "flake-provided chromium is not on PATH"
    assert chromedriver, "flake-provided chromedriver is not on PATH"

    options = Options()
    options.binary_location = chromium
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--force-prefers-reduced-motion=reduce")
    options.add_argument(f"--window-size={width},{height}")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    return webdriver.Chrome(
        service=Service(executable_path=chromedriver),
        options=options,
    )


def check_route(browser, route: str, expected_heading: str) -> None:
    browser.get(urljoin(BASE, route))
    heading = browser.find_element("css selector", "h1")
    assert expected_heading in heading.text.replace("\n", " "), (route, heading.text)
    assert browser.find_element("css selector", "main#main-content").is_displayed()

    contained = browser.execute_script(
        "return document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )
    assert contained, f"{route} overflows the viewport"

    reduced = browser.execute_script(
        "return window.matchMedia('(prefers-reduced-motion: reduce)').matches"
    )
    assert reduced, f"{route} did not observe reduced-motion browser preference"

    if SCREENSHOTS_DIR:
        target = Path(SCREENSHOTS_DIR)
        target.mkdir(parents=True, exist_ok=True)
        name = route.removesuffix(".html")
        viewport = browser.execute_script("return window.innerWidth")
        assert browser.save_screenshot(str(target / f"{name}-{viewport}px.png"))

    browser.find_element("tag name", "body").send_keys(Keys.TAB)
    active = browser.switch_to.active_element
    assert "skip-link" in (active.get_attribute("class") or "").split(), (
        route,
        active.get_attribute("outerHTML"),
    )
    outline = browser.execute_script(
        "const s=getComputedStyle(arguments[0]); return [s.outlineStyle,s.outlineWidth,s.transform];",
        active,
    )
    assert outline[0] != "none" and float(outline[1].replace("px", "")) >= 2, (route, outline)

    active.send_keys(Keys.ENTER)
    assert browser.current_url.endswith("#main-content"), browser.current_url

    severe = [
        item
        for item in browser.get_log("browser")
        if item.get("level") == "SEVERE"
    ]
    assert not severe, f"{route} browser errors: {severe}"


for width, height in ((1280, 900), (320, 800)):
    with driver(width, height) as browser:
        for route, heading in ROUTES.items():
            check_route(browser, route, heading)

print("browser smoke passed")
