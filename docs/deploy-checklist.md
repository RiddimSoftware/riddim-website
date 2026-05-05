# Website Deploy Checklist

Use this checklist for every production launch or material content refresh of
`riddimsoftware.com`. Keep the evidence in the PR or release thread so a future
operator can compare what changed.

## Pre-Deploy

- Run `npm run validate`; it must pass local HTML and sitemap checks.
- Run `python3 scripts/health_check.py`; every route must return a passing HTTP
  status.
- Start the site locally with `npm run dev` and load the homepage in a browser
  without console or render errors.
- Review new homepage and product copy with the user before merge.
- Confirm product card outbound links in `src/_data/products.json` are expected
  and resolve.
- Attach explicit desktop and mobile screenshot evidence to the PR.
- If the homepage or product layout changed materially, refresh the baseline
  screenshots under `docs/screenshots/baseline-YYYY-MM-DD/`.

## Post-Deploy

- Confirm the live homepage returns HTTP 200:
  `curl --fail --location https://riddimsoftware.com/`.
- Confirm the live Apple app site association file returns HTTP 200 JSON:
  `curl --fail --location https://riddimsoftware.com/.well-known/apple-app-site-association`.
- Confirm `robots.txt` returns HTTP 200:
  `curl --fail --location https://riddimsoftware.com/robots.txt`.
- Confirm `sitemap.xml` returns HTTP 200:
  `curl --fail --location https://riddimsoftware.com/sitemap.xml`.
- Run `VALIDATE_SITE_ROOT=_site python3 scripts/validate.py --live` after
  production promotion.
- Re-check every product card outbound link from `src/_data/products.json`.
- Compare the live homepage against the latest desktop and mobile baseline
  screenshots. Replace the baseline after a material content change.

## Baseline Screenshots

Current local baseline screenshots:

- `docs/screenshots/baseline-2026-05-05/homepage-desktop-1440.png`
- `docs/screenshots/baseline-2026-05-05/homepage-mobile-390.png`

These screenshots were captured from the local 11ty dev server before the next
production deploy was available. After the next deploy, refresh this folder from
the live production homepage and update this section if the rendered output
differs from the local baseline.
