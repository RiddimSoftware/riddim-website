#!/usr/bin/env python3
"""
Health check script for riddimsoftware.com consolidated product routes
and legacy subdomains.

Usage:
    python3 scripts/health_check.py [--timeout SECONDS]

Exit codes:
    0  All checks passed
    1  One or more checks failed

No Node/npm required. Uses Python 3 stdlib + curl (per project constraint).
curl is used for HTTP requests so the system trust store is always respected
(avoids macOS Python SSL cert bundle issues without requiring certifi).

See docs/deploy-checklist.md for when to run this script during launch checks.
"""

import sys
import argparse
import subprocess

PRODUCT_ROUTES = [
    ("Homepage", "https://riddimsoftware.com/"),
    ("Blindfold", "https://riddimsoftware.com/blindfold/"),
    ("epac", "https://riddimsoftware.com/epac/"),
    ("Bubble Bop", "https://riddimsoftware.com/bubble-bop/"),
    ("Reach", "https://riddimsoftware.com/reach/"),
    ("Portal Door", "https://riddimsoftware.com/portal-door/"),
    ("Sonnio", "https://riddimsoftware.com/sonnio/"),
    ("Double Dozen", "https://riddimsoftware.com/double-dozen/"),
]

LEGACY_SUBDOMAINS = [
    ("epac legacy subdomain", "https://epac.riddimsoftware.com"),
    ("nether legacy subdomain", "https://nether.riddimsoftware.com"),
    ("sonnio legacy subdomain", "https://sonnio.riddimsoftware.com"),
]


def check_url(url: str, timeout: int) -> tuple[bool, str]:
    """Return (ok, detail) for a single URL check using curl."""
    try:
        result = subprocess.run(
            [
                "curl",
                "--silent",
                "--output", "/dev/null",
                "--write-out", "%{http_code}",
                "--max-time", str(timeout),
                "--location",  # follow redirects
                "--user-agent", "riddim-health-check/1.0",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 5,
        )
        http_code_str = result.stdout.strip()
        if not http_code_str.isdigit():
            return False, f"curl error (exit {result.returncode}): {result.stderr.strip()}"
        http_code = int(http_code_str)
        if 200 <= http_code < 300:
            return True, f"HTTP {http_code}"
        if http_code == 0:
            return False, f"curl could not connect (exit {result.returncode})"
        return False, f"HTTP {http_code} (non-2xx)"
    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout}s"
    except Exception as e:  # noqa: BLE001
        return False, f"Unexpected error: {e}"


def run_checks(urls: list[tuple[str, str]], label: str, timeout: int) -> list[str]:
    """Run checks for a list of URLs. Returns list of failure messages."""
    failures = []
    print(f"\n{label}")
    print("-" * len(label))
    for name, url in urls:
        ok, detail = check_url(url, timeout)
        status_icon = "OK" if ok else "FAIL"
        print(f"  [{status_icon}] {name}: {url}  ({detail})")
        if not ok:
            failures.append(f"{name} ({url}): {detail}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Riddim Software health checks")
    parser.add_argument("--timeout", type=int, default=15,
                        help="Request timeout in seconds (default: 15)")
    args = parser.parse_args()

    all_failures: list[str] = []

    all_failures += run_checks(
        PRODUCT_ROUTES,
        "Consolidated product routes (riddimsoftware.com)",
        args.timeout,
    )
    all_failures += run_checks(
        LEGACY_SUBDOMAINS,
        "Legacy subdomains (coexistence check)",
        args.timeout,
    )

    print()
    if all_failures:
        print(f"FAILED — {len(all_failures)} check(s) did not pass:")
        for msg in all_failures:
            print(f"  - {msg}")
        return 1

    total = len(PRODUCT_ROUTES) + len(LEGACY_SUBDOMAINS)
    print(f"All {total} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
