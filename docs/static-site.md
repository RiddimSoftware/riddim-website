# Static Site Decision

**Decision date:** 2026-05-05
**Decision:** Use 11ty as the site generator.
**Scope:** `RiddimSoftware/riddim-website`

## Chosen Tool

Riddim Software's marketing site uses [11ty](https://www.11ty.dev/) with a minimal Node setup.

The site is content-first static HTML/CSS, not an application. 11ty gives the repo shared layouts, product data, predictable output, and a built-in local dev server without adopting a client-side framework or bundler.

## Why 11ty

- The site remains plain static HTML/CSS in production.
- Product pages can be generated from `src/_data/products.json` and one template instead of editing repeated HTML files.
- The generated `_site/` directory fits the S3 artifact-promotion pipeline from `WEB-87`.
- `npm run dev` provides a fast local server with live reload.
- 11ty can support future build-time work such as sitemap generation, Open Graph metadata, and generated social images without turning the repo into a React/Astro app.

## Why Not Raw Includes

A tiny include script would work for the first shared header/footer, but the backlog already expects product data, sitemap generation, Open Graph metadata, and deploy artifacts. Extending a custom script for those jobs would create a private static-site generator. 11ty is the smallest standard tool that covers that surface area.

## Why Not Astro

Astro is a strong static-site framework, but it adds more conventions and framework surface than this site currently needs. There is no client-side app behavior, component hydration, TypeScript, or content collection need that justifies Astro for the current roadmap.

## Source Layout

- `src/index.html` is the homepage.
- `src/bubble-bop/index.html` is the Bubble Bop App Clip landing page.
- `src/reach-privacy.html` is the Reach privacy page.
- `src/_data/products.json` is the product-page content source.
- `src/products.njk` paginates over product records and generates consolidated `<slug>/index.html` product pages, except Bubble Bop, which keeps its hand-authored App Clip landing page at `src/bubble-bop/index.html`.
- `src/_includes/product-page.njk` is the shared product-page template.
- Shared static assets remain at the repository root and are copied through by `.eleventy.js`.
- Generated deploy output lives in `_site/`.

## Add a Page

Create the page under `src/` at the path it should have in production. For example, `src/about.html` builds to `_site/about.html`, and `src/support/index.html` builds to `_site/support/index.html`.

Use root-relative asset paths when a page is meant to live at a route directory, and keep canonical URLs explicit when the page is intended for indexing.

## Add a Product

Follow `docs/adding-a-product.md`. In short, add assets at the repository root, add one object to `src/_data/products.json`, then run `npm run build` and confirm `_site/<slug>/index.html` renders as expected. Product pages should use stable, lowercase, trailing-slash routes such as `https://riddimsoftware.com/epac/`.

Product pages are added to `_site/sitemap.xml` automatically from `src/_data/products.json`. No hand edit is needed for the sitemap after adding a product; run `npm run build` or `npm run validate` to regenerate it.

## Sitemap

`src/sitemap.njk` generates `_site/sitemap.xml` during the 11ty build. Its URL list comes from `src/_data/sitemap.js`, which includes the homepage, every consolidated product route in `src/_data/products.json`, `reach-privacy.html`, and `/about` when `src/about.html` or `src/about/index.html` exists.

Each sitemap entry uses an absolute `https://riddimsoftware.com` URL and a `lastmod` value from the latest git commit touching the relevant source file. If git metadata is unavailable in a build environment, the generator falls back to the current build time. `npm run validate` parses the generated sitemap as Sitemaps 0.9 XML and confirms `robots.txt` references `https://riddimsoftware.com/sitemap.xml`.

## Local Workflow

Install dependencies:

```bash
npm install --package-lock=false
```

Run a live-reload dev server:

```bash
npm run dev
```

Build the static site:

```bash
npm run build
```

Validate generated output:

```bash
npm run validate
```

## Validation and Health Checks

Run `npm run validate` before deployment for local HTML, sitemap, and product
metadata checks. Run `python3 scripts/health_check.py` when checking live
product-route and legacy-subdomain health.

Use `docs/deploy-checklist.md` for the complete pre/post-deploy launch checklist
and screenshot baseline requirements.

## Deploy Workflow

Deployment follows `docs/release-process.md`.

`WEB-87` moved the site to immutable S3 artifact promotion. A push to `main` builds a commit-addressed artifact, deploys that artifact to validation, and leaves production unchanged until the manual production promotion workflow is approved.

`scripts/build_artifact.sh` is the build boundary. It runs the 11ty build, copies `_site/` into a temporary artifact staging directory, writes `artifact-manifest.json`, and packages the tarball consumed by the validation and production deployment scripts.

There is no Amplify build step for the main site after `WEB-87`. Amplify references in older docs apply only to legacy subdomain retirement work unless explicitly stated otherwise.