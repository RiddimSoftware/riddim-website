# Quality baseline

Initial baseline captured on 2026-05-06 for the WEB-48 PR.

## Scope

- Homepage: `/`
- Representative product page: `/sonnio/`

Note: the current 11ty site emits canonical product routes like `/sonnio/`, not the older `/products/sonnio.html` path mentioned in the ticket text.

## Lighthouse budgets enforced on every PR

Both mobile and desktop runs must meet:

- Performance: `>= 90`
- Accessibility: `>= 95`
- Best practices: `>= 95`
- SEO: `>= 95`

## Initial Lighthouse baseline

| Page | Form factor | Performance | Accessibility | Best practices | SEO |
| --- | --- | ---: | ---: | ---: | ---: |
| `/` | Mobile | 96 | 100 | 96 | 100 |
| `/sonnio/` | Mobile | 100 | 100 | 100 | 100 |
| `/` | Desktop | 100 | 100 | 96 | 100 |
| `/sonnio/` | Desktop | 100 | 100 | 100 | 100 |

## Initial accessibility baseline

Automated ruleset: `axe-core` tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22a`, `wcag22aa`.

- `/`: no automated WCAG A/AA violations found
- `/sonnio/`: no automated WCAG A/AA violations found

Raw CI artifacts are uploaded from the PR workflow for deeper inspection when scores or violations change.
