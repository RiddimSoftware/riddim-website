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
import json
import subprocess
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

DEFAULT_SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.environ.get("VALIDATE_SITE_ROOT", DEFAULT_SITE_ROOT)
if not os.path.isabs(SITE_ROOT):
    SITE_ROOT = os.path.join(DEFAULT_SITE_ROOT, SITE_ROOT)
TEMPLATE_PATH = os.path.join(
    DEFAULT_SITE_ROOT,
    "infrastructure",
    "cloudformation",
    "riddim-website-static-site.yml",
)
LIVE_BASE = "https://riddimsoftware.com"

LIVE_PATHS = [
    "/",
    "/default.css",
    "/robots.txt",
    "/sitemap.xml",
    "/.well-known/apple-app-site-association",
]
LIVE_MISSING_PATH = "/__riddim_validate_missing_route__"

CONSOLIDATED_PRODUCT_PATHS = [
    ("Blindfold", "/blindfold/", "Blindfold - Riddim Software"),
    ("epac", "/epac/", "epac - Riddim Software"),
    ("Bubble Bop", "/bubble-bop/", "Bubble Bop — Riddim Software"),
    ("Reach", "/reach/", "Reach - Riddim Software"),
    ("Portal Door", "/portal-door/", "Portal Door - Riddim Software"),
    ("Sonnio", "/sonnio/", "Sonnio - Riddim Software"),
    ("Double Dozen", "/double-dozen/", "Double Dozen - Riddim Software"),
]

LEGACY_SUBDOMAINS = [
    ("epac legacy subdomain", "https://epac.riddimsoftware.com"),
    ("nether legacy subdomain", "https://nether.riddimsoftware.com"),
    ("sonnio legacy subdomain", "https://sonnio.riddimsoftware.com"),
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


def run_local_product_metadata_checks():
    print("\n── Local product metadata checks ──")
    missing = []

    for name, path, expected_title in CONSOLIDATED_PRODUCT_PATHS:
        rel_file = path.strip("/") + "/index.html"
        html_path = os.path.join(SITE_ROOT, rel_file)
        canonical = LIVE_BASE + path

        if not os.path.exists(html_path):
            fail(f"{name} route {path}: generated file missing at {rel_file}")
            missing.append(name)
            continue

        with open(html_path, encoding="utf-8") as handle:
            content = handle.read()

        expected_tags = [
            (f"<title>{expected_title}</title>", "HTML title"),
            (f'<link rel="canonical" href="{canonical}">', "canonical URL"),
            (f'<meta property="og:url" content="{canonical}">', "Open Graph URL"),
            ('<meta property="og:title"', "Open Graph title"),
            ('<meta property="og:description"', "Open Graph description"),
            ('<meta property="og:image"', "Open Graph image"),
            ('<meta name="twitter:card"', "Twitter card"),
            ('<meta name="twitter:title"', "Twitter title"),
            ('<meta name="twitter:description"', "Twitter description"),
            ('<meta name="twitter:image"', "Twitter image"),
        ]

        for expected, label in expected_tags:
            if expected not in content:
                fail(f"{name} route {path}: missing {label}")

    if not missing and not failures:
        ok(f"checked metadata for {len(CONSOLIDATED_PRODUCT_PATHS)} consolidated product route(s)")

def run_local_theme_checks():
    print("\n── Local theme checks ──")
    css_path = os.path.join(SITE_ROOT, "default.css")
    theme_js_path = os.path.join(SITE_ROOT, "assets", "theme.js")
    manifest_dark_path = os.path.join(SITE_ROOT, "manifest-dark.json")
    theme_head_template_path = os.path.join(DEFAULT_SITE_ROOT, "src", "_includes", "theme-head.njk")
    theme_toggle_template_path = os.path.join(DEFAULT_SITE_ROOT, "src", "_includes", "theme-toggle.njk")

    if not os.path.exists(css_path):
        fail("default.css missing for theme checks")
        return

    if not os.path.exists(theme_js_path):
        fail("assets/theme.js missing")
    if not os.path.exists(manifest_dark_path):
        fail("manifest-dark.json missing")
    if not os.path.exists(theme_head_template_path):
        fail("src/_includes/theme-head.njk missing")
    if not os.path.exists(theme_toggle_template_path):
        fail("src/_includes/theme-toggle.njk missing")

    with open(css_path, encoding="utf-8") as handle:
        css = handle.read()

    required_css_snippets = [
        '@media (prefers-color-scheme: dark)',
        ':root[data-theme="dark"]',
        'html[data-theme-ui="ready"] .theme-toggle',
    ]
    for snippet in required_css_snippets:
        if snippet not in css:
            fail(f"default.css missing theme rule: {snippet}")

    if os.path.exists(manifest_dark_path):
        with open(manifest_dark_path, encoding="utf-8") as handle:
            try:
                manifest_dark = json.load(handle)
            except json.JSONDecodeError as error:
                fail(f"manifest-dark.json is not valid JSON: {error}")
                manifest_dark = None

        if manifest_dark is not None:
            if manifest_dark.get("theme_color") != "#101418":
                fail("manifest-dark.json theme_color must be #101418")
            if manifest_dark.get("background_color") != "#101418":
                fail("manifest-dark.json background_color must be #101418")

    if os.path.exists(theme_head_template_path):
        with open(theme_head_template_path, encoding="utf-8") as handle:
            theme_head_template = handle.read()

        required_theme_head_snippets = [
            'window.matchMedia("(prefers-color-scheme: dark)")',
            'window.localStorage.getItem(storageKey)',
            'root.dataset.themePreference = preference;',
            'root.dataset.theme = theme;',
            'root.style.colorScheme = theme;',
            'manifestLink.setAttribute("href", nextHref);',
        ]
        for snippet in required_theme_head_snippets:
            if snippet not in theme_head_template:
                fail(f"src/_includes/theme-head.njk missing behavior snippet: {snippet}")

    if os.path.exists(theme_js_path):
        with open(theme_js_path, encoding="utf-8") as handle:
            theme_js = handle.read()

        required_theme_js_snippets = [
            "window.localStorage.removeItem(storageKey)",
            "window.localStorage.setItem(storageKey, preference)",
            "media.addEventListener('change', handleSystemChange)",
            "media.addListener(handleSystemChange)",
            "window.dispatchEvent(new CustomEvent('riddim-themechange'",
        ]
        for snippet in required_theme_js_snippets:
            if snippet not in theme_js:
                fail(f"assets/theme.js missing behavior snippet: {snippet}")

    if os.path.exists(theme_toggle_template_path):
        with open(theme_toggle_template_path, encoding="utf-8") as handle:
            theme_toggle_template = handle.read()

        required_theme_toggle_snippets = [
            '<option value="system">System</option>',
            '<option value="light">Light</option>',
            '<option value="dark">Dark</option>',
            'aria-describedby="theme-status"',
            'role="status"',
            'aria-live="polite"',
        ]
        for snippet in required_theme_toggle_snippets:
            if snippet not in theme_toggle_template:
                fail(f"src/_includes/theme-toggle.njk missing control snippet: {snippet}")

def run_local_asset_path_checks():
    print("\n── Local asset path checks ──")
    html_files = []
    for root, _, files in os.walk(SITE_ROOT):
        rel_root = os.path.relpath(root, SITE_ROOT)
        parts = rel_root.replace("\\", "/").split("/")
        if any(p in parts for p in [".git", "node_modules"]):
            continue
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))

    forbidden_refs = [
        ('href="default.css"', 'href="/default.css"'),
        ('src="wordmark.svg"', 'src="/wordmark.svg"'),
        ('src="app-store.svg"', 'src="/app-store.svg"'),
    ]

    checked_files = 0
    found_issues = False
    for path in sorted(html_files):
        rel = os.path.relpath(path, SITE_ROOT)
        with open(path, encoding="utf-8") as handle:
            content = handle.read()
        checked_files += 1

        for forbidden, expected in forbidden_refs:
            if forbidden in content:
                fail(f'{rel}: found {forbidden}; use {expected} so nested routes keep working')
                found_issues = True

    if not found_issues:
        ok(f"checked {checked_files} HTML file(s): shared assets use root-relative paths")


def run_local_routing_infra_checks():
    print("\n── Local routing infrastructure checks ──")

    if not os.path.exists(TEMPLATE_PATH):
        fail("static-site CloudFormation template missing")
        return

    with open(TEMPLATE_PATH, encoding="utf-8") as handle:
        template = handle.read()

    required_snippets = [
        ("DirectoryIndexRewriteFunction:", "CloudFront directory-index rewrite function resource"),
        ('request.uri = uri + "index.html";', "trailing-slash directory rewrite"),
        ('request.uri = uri + "/index.html";', "extensionless route rewrite"),
        ("FunctionAssociations:", "viewer-request function association"),
        ("EventType: viewer-request", "viewer-request function event"),
        (
            "FunctionARN: !GetAtt DirectoryIndexRewriteFunction.FunctionMetadata.FunctionARN",
            "rewrite function ARN attachment",
        ),
    ]

    for snippet, label in required_snippets:
        if snippet not in template:
            fail(f"CloudFormation template missing {label}")

    response_404_count = template.count("ResponsePagePath: /404.html")
    if response_404_count < 4:
        fail("CloudFormation template must map 403/404 errors to /404.html on both distributions")

    status_404_count = template.count("ResponseCode: 404")
    if status_404_count < 4:
        fail("CloudFormation template must preserve HTTP 404 status on both distributions")

    if not failures:
        ok("CloudFront template includes directory-index rewrites and dedicated 404 responses")


def run_local_homepage_tile_css_checks():
    print("\n── Local homepage tile CSS checks ──")
    css_path = os.path.join(SITE_ROOT, "default.css")

    if not os.path.exists(css_path):
        fail("default.css missing")
        return

    with open(css_path, encoding="utf-8") as handle:
        css = handle.read()

    desktop_blocks = re.findall(
        r"@media[^{]*min-width\s*:\s*1280px[^{]*\{(?P<body>.*?)\n\}",
        css,
        flags=re.IGNORECASE | re.DOTALL,
    )
    for block in desktop_blocks:
        if "grayscale(" in block and re.search(r"opacity\s*:\s*0\.5\b", block):
            fail("default.css must not desaturate or dim homepage product tiles at desktop widths")
            return

    ok("default.css has no desktop grayscale/opacity product tile fallback")


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


def curl_body(url):
    result = subprocess.run(
        ["curl", "-s", "--location", "--max-time", "10", url],
        capture_output=True, text=True
    )
    return result.stdout


def run_live_checks():
    print("\n── Live site checks ──")
    for path in LIVE_PATHS:
        url = LIVE_BASE + path
        status = curl_status(url)
        if not status.startswith("2"):
            fail(f"{url} returned {status} (expected 2xx)")
        else:
            ok(f"{url} → {status}")

    for name, path, _expected_title in CONSOLIDATED_PRODUCT_PATHS:
        url = LIVE_BASE + path
        status = curl_status(url)
        if not status.startswith("2"):
            fail(f"{name} route {url} returned {status} (expected 2xx)")
        else:
            ok(f"{name} route {url} → {status}")

    for name, url in LEGACY_SUBDOMAINS:
        status = curl_status(url)
        if not (status.startswith("2") or status.startswith("3")):
            fail(f"{name} {url} returned {status} (expected reachable 2xx/3xx)")
        else:
            ok(f"{name} {url} → {status}")

    # apple-app-site-association must be JSON (not HTML fallback)
    aasa_url = LIVE_BASE + "/.well-known/apple-app-site-association"
    ct = curl_content_type(aasa_url)
    if "json" not in ct.lower():
        fail(f"{aasa_url} content-type is '{ct}', expected JSON")
    else:
        ok(f"{aasa_url} content-type: {ct}")

    missing_url = LIVE_BASE + LIVE_MISSING_PATH
    missing_status = curl_status(missing_url)
    if missing_status != "404":
        fail(f"{missing_url} returned {missing_status} (expected 404)")
    else:
        ok(f"{missing_url} → {missing_status}")

    missing_body = curl_body(missing_url)
    if "That page doesn’t exist." not in missing_body:
        fail(f"{missing_url} did not render the dedicated 404 page copy")
    else:
        ok(f"{missing_url} rendered the dedicated 404 page copy")

    for name, path, expected_title in CONSOLIDATED_PRODUCT_PATHS:
        url = LIVE_BASE + path
        status = curl_status(url)
        if status != "200":
            fail(f"{url} returned {status} (expected 200)")
            continue

        body = curl_body(url)
        if f"<title>{expected_title}</title>" not in body:
            fail(f"{url} did not render the expected product page title")
        else:
            ok(f"{url} rendered the expected product page title")

        canonical = f'<link rel="canonical" href="{url}">'
        if canonical not in body:
            fail(f"{url} did not render the expected canonical URL")
        else:
            ok(f"{url} rendered the expected canonical URL")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    live = "--live" in sys.argv
    run_local_checks()
    run_local_sitemap_checks()
    run_local_product_metadata_checks()
    run_local_theme_checks()
    run_local_asset_path_checks()
    run_local_routing_infra_checks()
    run_local_homepage_tile_css_checks()
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
