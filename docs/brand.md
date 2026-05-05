# Riddim Brand Usage

## Identity in one paragraph

Riddim Software is Sunny Purewal's one-person indie product company: a quiet home for small, useful products that can stand on their own. It is not an agency, a client-services shop, a venture studio, or a contractor portfolio. The company brand should feel calm, direct, and founder-led, with enough structure that each product benefits from the shared trust without losing its own shape.

## Wordmark Usage

Use the wordmark for the site header, footer, press references, and any surface where the company name needs to be read.

![Riddim Software wordmark](../wordmark.svg)

Use the monogram only where space is tight, such as favicons, social avatars, or square previews.

![Riddim monogram](../monogram.svg)

Keep the wordmark at least 140 px wide on screens and the monogram at least 32 px square. Leave clear space around either mark equal to the height of the lowercase letters in the wordmark. Do use the marks on quiet, high-contrast backgrounds. Do not stretch, recolor, outline, rotate, crop, add shadows, or place them on busy product art.

## Type

Canonical Riddim pages use the system stack already in `default.css`: `Arial, Helvetica, sans-serif` for headings and body copy. Keep headings confident and compact, with normal letter spacing. Body copy should stay readable before it tries to be expressive. Use the browser's default monospace stack for code, tokens, paths, and command snippets. Do not import Sonnio's Outfit, Portal Door's Space Grotesk, or another product's type direction into canonical Riddim pages.

## Color

| Token | Hex | Intended use |
| --- | --- | --- |
| `--color-bg` | `#fbfaf7` | Main warm paper background. |
| `--color-bg-alt` | `#f2efe8` | Alternating bands and quiet page sections. |
| `--color-fg` | `#171717` | Primary text and dark footer background. |
| `--color-fg-muted` | `#5f646b` | Supporting copy and secondary labels. |
| `--color-accent` | `#2f6f5e` | Links, primary actions, and compact emphasis. |
| `--color-accent-fg` | `#ffffff` | Text on accent or status fills. |
| `--color-border` | `#ddd8cf` | Dividers, card borders, and framed media. |
| `--color-success` | `#2f7d4f` | Positive status. |
| `--color-warning` | `#8a6200` | Caution or freshness status. |
| `--color-danger` | `#b42318` | Error or destructive status. |
| `--color-surface` | `#ffffff` | Cards and contained panels. |
| `--color-surface-alt` | `#e8eee9` | Subtle media wells and hover fills. |
| `--color-footer-muted` | `#cfcac1` | Secondary text on dark footer. |

Forbidden values: do not use `#004d97` royal blue, neon Minecraft green, or product-specific colors as company-page accents unless the wordmark itself has been deliberately updated to support them.

## Voice

Use plain language. Prefer concrete nouns and short sentences. Avoid superlatives, hype, growth-deck phrasing, and "we" when the sentence is really about the founder's judgment. Let Sunny be visible when authorship matters, but keep the company pages focused on products and trust. A good Riddim sentence should sound like a careful maker explaining what exists, why it exists, and what someone can do next.

## Out of Brand Scope

Per-product experiences keep their own brands. Sonnio, Portal Door, Blindfold, Reach, Bubble Bop, Double Dozen, and future product subsites may use their own type, color, illustration, screenshots, and voice when those choices serve the product. This guide covers canonical Riddim company pages, shared company marks, and repo-level documentation only.

## App Store Badges

Use the shared App Store badge treatment for product CTAs that link to Apple App Store listings:

```json
{
  "label": "Download on the App Store",
  "href": "https://apps.apple.com/us/app/example/id1234567890",
  "external": true,
  "appStoreBadge": true
}
```

The rendered CTA uses Apple's official badge artwork inside a plain link. Do not wrap the badge in `.btn`, add extra text, add borders, recolor it, change its proportions, or shrink it below 40 px tall. Keep at least 10 px of clear space around the 40 px badge.

Badge asset sources:

- App Store badge: `https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg`
- Mac App Store badge: `https://developer.apple.com/app-store/marketing/guidelines/images/badge-download-on-the-mac-app-store.svg`

Apple's current App Store Marketing Guidelines live at `https://developer.apple.com/app-store/marketing/guidelines/`.
