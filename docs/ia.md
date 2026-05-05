# Product Information Architecture Proposal

Status: proposed for user review before WEBSITE-7 implementation proceeds.

This proposal groups the visible Riddim homepage inventory into three sections:
Consumer Apps, Developer Tools, and Selected Work. It documents the IA decision
only; product copy, HTML/CSS implementation, and destination-link changes stay
out of scope.

## Categories

### Consumer Apps

First-party apps and games built for end users. This is the primary catalog
section and should carry the most visual weight after any featured product.

| Item | Placement rationale |
| --- | --- |
| Blindfold | First-party product with a dedicated external product site and current Riddim product-page route. Although it serves retailers, the product experience is customer-facing enough to sit with the main app catalog. |
| epac | First-party civic research product and current featured homepage product. Keep it in the main catalog even when visually featured separately. |
| Bubble Bop | First-party App Store game for kids; belongs with consumer apps rather than selected work. |
| Reach | First-party App Store app with an existing Riddim privacy page; belongs in the main app catalog. |
| Portal Door | First-party generative web experience; the visible product name should be Portal Door. |
| Sonnio | First-party music experience on a Riddim subdomain; belongs in the main app catalog. |
| Double Dozen | First-party App Store game; belongs with the other consumer games and apps. |
| nether | Do not present as a separate product. Treat `nether` as the current host/alias for Portal Door (`nether.riddimsoftware.com`). |

### Developer Tools

Engineering-facing work, open-source projects, prototypes, and public technical
artifacts. This section should be lower-volume than Consumer Apps and should not
compete with the product catalog.

| Item | Placement rationale |
| --- | --- |
| GitHub / open-source | GitHub is not itself a product route. Present it as an external developer-work link to public projects and prototypes. |

### Selected Work

Portfolio or contract work that is relevant to Riddim's capability story but is
not clearly a current first-party Riddim product. This section should be lower
emphasis than Consumer Apps and should avoid implying ownership of products that
belong to clients or partners.

| Item | Placement rationale |
| --- | --- |
| Koneksa | Recommend lower-emphasis Selected Work. Repo evidence identifies Koneksa as external-only App Store work and prior docs note it appears under Other Work, not the Riddim product route set. Keep it out of the main product catalog unless ownership or brand strategy changes. |

## Sort Order

Use a deliberate, stable order rather than pure alphabetic sorting.

Consumer Apps order:

1. epac
2. Blindfold
3. Reach
4. Bubble Bop
5. Double Dozen
6. Sonnio
7. Portal Door

Rationale: lead with the most strategically legible/current products, then keep
people-oriented utility apps ahead of games and experiments. This avoids a flat
"everything is equal" grid while still keeping the full catalog scannable.
Within the games/experiments tail, keep the simpler App Store games before the
less self-explanatory web experiences.

Developer Tools order:

1. GitHub / open-source

Rationale: there is only one current developer-work item. If more are added,
sort by relevance to current hiring/partnership goals, then by recency.

Selected Work order:

1. Koneksa

Rationale: there is only one current selected-work item. If more are added,
sort by relevance to the capability story the homepage is trying to tell, not
by client name.

## Koneksa Placement Decision

Recommend placing Koneksa in lower-emphasis Selected Work, not the main product
catalog.

Reasoning:

- The Linear brief calls Koneksa contract work and asks for an explicit brand
  decision.
- `docs/product-route-map.md` marks Koneksa external-only with no main-site
  product route.
- `docs/homepage-copy.md` treats Koneksa as work-history context, not product
  grid copy.
- Main catalog placement would imply current first-party product ownership; the
  available repo evidence supports a portfolio/work-history treatment instead.

Pending approval: user review should confirm this placement before WEBSITE-7
homepage implementation stories use the IA.
