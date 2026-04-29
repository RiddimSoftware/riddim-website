# Product Route Map

This route map is the implementation input for first-party product pages and homepage routing. It documents the visible inventory from `index.html` as of RIDDIM-78 and defines which destinations should move under `riddimsoftware.com`.

## Consolidation Guardrails

- Keep every existing subdomain, Amplify-hosted product site, App Store listing, and external site live until the consolidated pages launch and are verified.
- Do not delete, disable, repoint, or require redirects from `epac.riddimsoftware.com`, `nether.riddimsoftware.com`, `sonnio.riddimsoftware.com`, or `blindfold.lol` for this consolidation.
- Main-site product routes should be stable, lowercase, trailing-slash paths that can be listed in `sitemap.xml`.
- Homepage product cards should eventually point to these main-site routes, while product pages keep launch, App Store, support/privacy, GitHub, or contact CTAs as appropriate.

## Route Decisions

| Homepage item | Current destination | Route decision | Primary route | Page CTAs | Rationale |
| --- | --- | --- | --- | --- | --- |
| Blindfold | `https://blindfold.lol` | Main-site product page | `/blindfold/` | Launch site: `https://blindfold.lol`; contact: `info@riddimsoftware.com` | Blindfold is a current featured product. The legacy product site remains the live app destination while the Riddim site provides portfolio context. |
| epac | `https://epac.riddimsoftware.com` | Main-site product page | `/epac/` | Launch app: `https://epac.riddimsoftware.com`; contact: `info@riddimsoftware.com` | epac already uses a Riddim subdomain and is marked updated, so it should have a first-party product page without changing the live app host. |
| Bubble Bop | `https://apps.apple.com/us/app/bubble-bop-kids-balloon-game/id1469251847` | Main-site product page | `/bubble-bop/` | App Store: current listing; contact: `info@riddimsoftware.com` | App-store-only products still need a main-site landing page so visitors can compare the portfolio before choosing the App Store CTA. |
| Reach | `https://apps.apple.com/us/app/reach/id1024071726` | Main-site product page | `/reach/` | App Store: current listing; privacy: `/reach-privacy.html`; contact: `info@riddimsoftware.com` | Reach already has a privacy page in this repo and should expose both App Store and privacy/support paths from its product page. |
| Portal Door | `https://nether.riddimsoftware.com` | Main-site product page | `/portal-door/` | Launch app: `https://nether.riddimsoftware.com`; contact: `info@riddimsoftware.com` | The visible product name is Portal Door, so the canonical route should match the product name. The `nether` subdomain remains the current app host. |
| Sonnio | `https://sonnio.riddimsoftware.com` | Main-site product page | `/sonnio/` | Launch app: `https://sonnio.riddimsoftware.com`; contact: `info@riddimsoftware.com` | Sonnio is a visible Riddim product with an existing subdomain-hosted experience that should stay available as the launch CTA. |
| Double Dozen | `https://apps.apple.com/us/app/double-dozen-tap-speed-game/id1614154786` | Main-site product page | `/double-dozen/` | App Store: current listing; contact: `info@riddimsoftware.com` | Double Dozen is an app-store-only product and should follow the same main-site page pattern as Bubble Bop and Reach. |
| GitHub | `https://github.com/sunnypurewal` | External-only | None | GitHub: current profile link | This is not a product page. Keep it as an external portfolio/work link rather than adding it to the product route set. |
| Koneksa | `https://apps.apple.com/app/koneksa-health/id1636936813` | External-only | None | App Store: current listing | Koneksa appears under Other Work rather than the Riddim product sections, so it should remain an external work-history link unless product ownership changes. |

## Implementation Notes For Product Pages

Create product pages for these route paths:

- `/blindfold/`
- `/epac/`
- `/bubble-bop/`
- `/reach/`
- `/portal-door/`
- `/sonnio/`
- `/double-dozen/`

Each page should use the existing local asset for its product image, include exactly one `h1`, provide product-specific metadata, and expose the CTAs listed above. Pages should link back to the homepage or portfolio section so visitors can continue browsing the Riddim catalog.

External-only entries should stay visible as external links if the homepage keeps the Other Work section. They should not be added to sitemap product entries unless a future backlog item changes their route decision.
