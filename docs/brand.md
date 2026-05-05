# Riddim Website Brand Tokens

## Light Theme Palette

The website ships a single light theme today. Tokens live in `default.css` under `:root` so a future dark theme can override the same names in a `[data-theme="dark"]` block without changing component CSS.

| Token | Value | Intended use |
| --- | --- | --- |
| `--color-bg` | `#fbfaf7` | Main page background; warm paper white. |
| `--color-bg-alt` | `#f2efe8` | Alternating bands and quiet product page backgrounds. |
| `--color-fg` | `#171717` | Primary text, dark footer background, and high-emphasis UI. |
| `--color-fg-muted` | `#5f646b` | Supporting copy, descriptions, and secondary text. |
| `--color-accent` | `#2f6f5e` | Links, header bars, primary buttons, back-links, and small emphasis labels. |
| `--color-accent-fg` | `#ffffff` | Text placed on accent, success, warning, or danger fills. |
| `--color-border` | `#ddd8cf` | Dividers, quiet card borders, and framed media edges. |
| `--color-success` | `#2f7d4f` | Positive status indicators such as `UPDATED`. |
| `--color-warning` | `#8a6200` | Caution or freshness indicators such as `NEW`. |
| `--color-danger` | `#b42318` | Error or destructive status indicators. |

Supporting surface tokens currently derive from the same palette:

| Token | Value | Intended use |
| --- | --- | --- |
| `--color-surface` | `#ffffff` | Product cards and contained panels. |
| `--color-surface-alt` | `#e8eee9` | Subtle accent-tinted media wells and hover fills. |
| `--color-footer-muted` | `#cfcac1` | Secondary text on the dark footer. |

## Palette Options

Option 1, neutral-led with refined green accent, is the implemented recommendation. It keeps the existing warm paper and near-black foundation, removes the old royal blue, and uses a restrained green only for links, primary buttons, back-links, and compact emphasis. This is conservative because it can survive a future wordmark decision without making the whole site feel green.

Option 2, monochrome with amber accent, was considered for founder review. It would keep `#fbfaf7` and `#171717`, use a stricter paper-and-ink visual system, and set the accent closer to a saturated amber for links/buttons only. That direction is more editorial, but it risks making warning/status UI and brand accent compete unless the status palette is also revisited.

## Contrast Notes

Checked combinations meet WCAG 2.2 AA contrast targets:

| Combination | Ratio | Target |
| --- | ---: | --- |
| `--color-fg` on `--color-bg` | 17.18:1 | Body text, 4.5:1 minimum. |
| `--color-fg-muted` on `--color-bg` | 5.71:1 | Body/supporting text, 4.5:1 minimum. |
| `--color-fg` on `--color-bg-alt` | 15.61:1 | Body text, 4.5:1 minimum. |
| `--color-accent` on `--color-bg` | 5.66:1 | Link text, 4.5:1 minimum. |
| `--color-accent-fg` on `--color-accent` | 5.91:1 | Button text, 4.5:1 minimum. |
| `--color-accent-fg` on `--color-success` | 5.04:1 | Status text, 4.5:1 minimum. |
| `--color-accent-fg` on `--color-warning` | 5.49:1 | Status text, 4.5:1 minimum. |
| `--color-accent-fg` on `--color-danger` | 6.57:1 | Status text, 4.5:1 minimum. |
