#!/usr/bin/env python3
"""
Local HTML validation and live site health checks for riddimsoftware.com.

Usage:
  python3 scripts/validate.py            # local HTML checks only
  VALIDATE_SITE_ROOT=_site python3 scripts/validate.py --live
                                        # generated output + live site checks

Exit code 0 = all checks passed. Exit code 1 = one or more failures.

Run before deploy (local only) and after deploy (--live) to verify the site.
See docs/deploy-checklist.md for the full launch checklist and screenshot
evidence expectations.
"""

import sys
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

DEFAULT_SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.environ.get("VALIDATE_SITE_ROOT", DEFAULT_SITE_ROOT)
if not os.path.isabs(SITE_ROOT):
    SITE_ROOT = os.path.join(DEFAULT_SITE_ROOT, SITE_ROOT)
LIVE_BASE = "https://riddimsoftware.com"

LIVE_PATHS = [
    "/",
    "/default.css",
    "/robots.txt",
    "/sitemap.xml",
    "/.well-known/apple-app-site-association",
]

failures = []


def fail(msg):
    failures.append(msg)
    print(f"  FAIL: {msg}")


def ok(msg):
    print(f"  ok:   {msg}")


# ── Local HTML checks ──────────────────────────────────────────────────────────

def check_html_file(path):
    rel = os.path.relpath(path, SITE_ROOT)
    with open(path) as f:
        content = f.read()

    # Duplicate IDs
    ids = re.findall(r'\bid=["\']([^"\']+)["\']', content)
    seen = set()
    for id_val in ids:
        if id_val in seen:
            fail(f"{rel}: duplicate id=\"{id_val}\"")
        seen.add(id_val)

    # Images missing alt
    for img in re.finditer(r'<img\b([^>]*)>', content, re.IGNORECASE):
        attrs = img.group(1)
        if not re.search(r'\balt=["\']', attrs):
            src = re.search(r'\bsrc=["\']([^"\']*)["\']', attrs)
            src_val = src.group(1) if src else "(unknown)"
            fail(f"{rel}: <img src=\"{src_val}\"> missing alt attribute")


def run_local_checks():
    print("\n── Local HTML checks ──")
    html_files = []
    for root, _, files in os.walk(SITE_ROOT):
        # skip .git, node_modules
        rel_root = os.path.relpath(root, SITE_ROOT)
        parts = rel_root.replace("\\", "/").split("/")
        if any(p in parts for p in [".git", "node_modules"]):
            continue
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))

    if not html_files:
        fail("no .html files found under site root")
        return

    for path in sorted(html_files):
        check_html_file(path)

    if not failures:
        ok(f"checked {len(html_files)} HTML file(s): no duplicate IDs, all images have alt")


def run_local_sitemap_checks():
    print("\n── Local sitemap checks ──")
    sitemap_path = os.path.join(SITE_ROOT, "sitemap.xml")
    robots_path = os.path.join(SITE_ROOT, "robots.txt")
    namespace = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    if not os.path.exists(sitemap_path):
        fail("sitemap.xml missing")
        return

    expected_locs = public_html_locs()

    try:
        tree = ET.parse(sitemap_path)
    except ET.ParseError as error:
        fail(f"sitemap.xml is not valid XML: {error}")
        return

    root = tree.getroot()
    if root.tag != "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset":
        fail("sitemap.xml root must be Sitemaps 0.9 <urlset>")
        return

    urls = root.findall("sitemap:url", namespace)
    if not urls:
        fail("sitemap.xml has no <url> entries")
        return

    seen = set()
    actual_locs = set()
    for url_node in urls:
        loc = url_node.findtext("sitemap:loc", default="", namespaces=namespace).strip()
        lastmod = url_node.findtext("sitemap:lastmod", default="", namespaces=namespace).strip()
        parsed = urlparse(loc)

        if not loc:
            fail("sitemap.xml entry missing <loc>")
        elif parsed.scheme != "https" or parsed.netloc != "riddimsoftware.com":
            fail(f"sitemap.xml loc is not an absolute riddimsoftware.com HTTPS URL: {loc}")
        elif loc in seen:
            fail(f"sitemap.xml duplicate loc: {loc}")
        seen.add(loc)
        if loc:
            actual_locs.add(loc)

        if not lastmod:
            fail(f"sitemap.xml entry missing <lastmod>: {loc or '(unknown loc)'}")

    missing_locs = sorted(expected_locs - actual_locs)
    extra_locs = sorted(actual_locs - expected_locs)
    for loc in missing_locs:
        fail(f"sitemap.xml missing public HTML page: {loc}")
    for loc in extra_locs:
        fail(f"sitemap.xml lists non-generated public HTML page: {loc}")

    if not os.path.exists(robots_path):
        fail("robots.txt missing")
    else:
        with open(robots_path, encoding="utf-8") as handle:
            robots = handle.read()
        if "Sitemap: https://riddimsoftware.com/sitemap.xml" not in robots:
            fail("robots.txt missing Sitemap: https://riddimsoftware.com/sitemap.xml")

    if not failures:
        ok(f"checked {len(urls)} sitemap URL(s): valid Sitemaps 0.9 XML with lastmod")


def public_html_locs():
    locs = set()

    for root, _, files in os.walk(SITE_ROOT):
        rel_root = os.path.relpath(root, SITE_ROOT)
        parts = rel_root.replace("\\", "/").split("/")
        if any(p in parts for p in [".git", "node_modules"]):
            continue

        for filename in files:
            if not filename.endswith(".html"):
                continue

            path = os.path.join(root, filename)
            with open(path, encoding="utf-8") as handle:
                content = handle.read()

            if re.search(
                r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*\bnoindex\b',
                content,
                re.IGNORECASE,
            ):
                continue

            rel_path = os.path.relpath(path, SITE_ROOT).replace("\\", "/")
            if rel_path == "index.html":
                pathname = "/"
            elif rel_path.endswith("/index.html"):
                pathname = "/" + rel_path[:-len("index.html")]
            else:
                pathname = "/" + rel_path

            locs.add(LIVE_BASE + pathname)

    return locs


# ── Live checks ────────────────────────────────────────────────────────────────

def curl_status(url):
    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "10", url],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def curl_content_type(url):
    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{content_type}", "--max-time", "10", url],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def run_live_checks():
    print("\n── Live site checks ──")
    for path in LIVE_PATHS:
        url = LIVE_BASE + path
        status = curl_status(url)
        if not status.startswith("2"):
            fail(f"{url} returned {status} (expected 2xx)")
        else:
            ok(f"{url} → {status}")

    # apple-app-site-association must be JSON (not HTML fallback)
    aasa_url = LIVE_BASE + "/.well-known/apple-app-site-association"
    ct = curl_content_type(aasa_url)
    if "json" not in ct.lower():
        fail(f"{aasa_url} content-type is '{ct}', expected JSON")
    else:
        ok(f"{aasa_url} content-type: {ct}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    live = "--live" in sys.argv
    run_local_checks()
    run_local_sitemap_checks()
    if live:
        run_live_checks()

    print()
    if failures:
        print(f"Result: {len(failures)} failure(s)")
        sys.exit(1)
    else:
        mode = "local + live" if live else "local"
        print(f"Result: all {mode} checks passed")


if __name__ == "__main__":
    main()
