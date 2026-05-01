#!/usr/bin/env python3
"""
Local HTML validation and live site health checks for riddimsoftware.com.

Usage:
  python3 scripts/validate.py            # local HTML checks only
  python3 scripts/validate.py --live     # local + live site checks

Exit code 0 = all checks passed. Exit code 1 = one or more failures.

Run before deploy (local only) and after deploy (--live) to verify the site.
"""

import sys
import os
import re
import subprocess

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
