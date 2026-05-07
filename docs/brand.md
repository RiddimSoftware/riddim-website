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

Canonical Riddim pages use Inter for headings and body copy, and JetBrains Mono for code and tokens. Inter is loaded via Google Fonts (`font-display: swap`) with `preconnect` hints so the page renders quickly under font-loading failure. Keep headings confident and compact, with normal letter spacing. Body copy should stay readable before it tries to be expressive. Do not import Sonnio's Outfit, Portal Door's Space Grotesk, or another product's type direction into canonical Riddim pages.

Three font-role variables and a type scale are defined in `default.css`. Use these instead of hard-coded values.

| Variable | Value |
| --- | --- |
| `--font-heading` | `"Inter"`, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif |
| `--font-body` | `"Inter"`, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif |
| `--font-mono` | `"JetBrains Mono"`, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace |

Type scale (modular, ~1.25 ratio):

| Variable | Value |
| --- | --- |
| `--text-xs` | 0.8 rem |
| `--text-sm` | 0.875 rem |
| `--text-base` | 1 rem |
| `--text-lg` | 1.125 rem |
| `--text-xl` | 1.25 rem |
| `--text-2xl` | 1.5625 rem |
| `--text-3xl` | 1.953 rem |
| `--text-4xl` | 2.441 rem |

Line-height tokens (`--leading-tight` through `--leading-relaxed`) are also available; see `:root` in `default.css`.

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

### Dark mode

When `prefers-color-scheme: dark` is active (or `data-theme="dark"` is set on `:root`), `default.css` overrides the tokens below. The light-mode tokens remain the canonical brand values; the dark-mode values are their governed dark-palette equivalents.

| Token | Hex | Paired against | Contrast | Derivation / guarantee |
| --- | --- | --- | --- | --- |
| `--color-bg` | `#101418` | — | — | Near-black with a cool blue-grey cast; replaces warm paper `#fbfaf7`. Provides the dark canvas for all other tokens. |
| `--color-bg-alt` | `#151b22` | `--color-fg` `#f5f1e8` | 16.0:1 (AAA) | Slightly lighter step above `--color-bg`; preserves the alternating-band rhythm of light-mode `#f2efe8`. |
| `--color-fg` | `#f5f1e8` | `--color-bg` `#101418` | 17.0:1 (AAA) | Warm off-white that mirrors the warmth of light-mode `#171717`; avoids harsh pure white. |
| `--color-fg-muted` | `#c4ccd5` | `--color-bg` `#101418` | 10.5:1 (AAA) | Blue-grey mid-tone; parallels light-mode `#5f646b`. Passes AAA against `--color-bg`. |
| `--color-accent` | `#84d6bb` | `--color-bg` `#101418` | 11.3:1 (AAA) | Light mint; see **Accent endorsement** note below. |
| `--color-accent-fg` | `#102019` | `--color-accent` `#84d6bb` | 10.2:1 (AAA) | Deep forest near-black for text rendered on `--color-accent` fills (e.g., `.btn-primary`). Provides AAA contrast on mint. |
| `--color-border` | `#2a333f` | — | — | Dark blue-grey divider; parallels warm `#ddd8cf` in light mode; visible but not harsh on `--color-bg`. |
| `--color-success` | `#86d39c` | `--color-bg` `#101418` | 9.8:1 (AAA) | Lightened green that preserves positive-status legibility in dark mode. |
| `--color-warning` | `#f2c875` | `--color-bg` `#101418` | 10.4:1 (AAA) | Lightened amber; parallels light-mode `#8a6200`. |
| `--color-danger` | `#ff938d` | `--color-bg` `#101418` | 6.8:1 (AA) | Lightened red; parallels light-mode `#b42318`. Passes WCAG AA; use at large size or bold weight for AAA equivalence. |
| `--color-surface` | `#1b222b` | — | — | Elevated panel background, slightly lighter than `--color-bg-alt`. Mirrors `#ffffff` surface role. |
| `--color-surface-alt` | `#222c37` | — | — | Subtle hover fill and media wells; parallels `#e8eee9`. |
| `--color-footer-bg` | `#090d12` | — | — | Deeper than `--color-bg`; footer uses this instead of light-mode `#171717` to keep hierarchy. |
| `--color-footer-fg` | `#f5f1e8` | `--color-footer-bg` `#090d12` | 18.5:1 (AAA) | Mirrors warm off-white; same value as `--color-fg`. |
| `--color-footer-muted` | `#aeb8c5` | `--color-footer-bg` `#090d12` | 8.2:1 (AAA) | Secondary footer copy; parallels light-mode `#cfcac1`. |

**Accent endorsement — `#84d6bb` light mint:** The deep-green light-mode accent `#2f6f5e` cannot be used in dark mode at accessible luminance — it would disappear against dark backgrounds. `#84d6bb` is the governed dark-palette equivalent: it shifts the feel toward "tech-startup pop" compared to the light-mode "calm, founder-led" green, and that shift is a deliberate and accepted tradeoff for dark-palette legibility. Any future re-evaluation of the dark accent should verify AAA contrast (≥ 7:1) against `--color-bg #101418` before adopting a replacement.

**On-mint text:** When rendering text or icons directly on an `--color-accent` fill (e.g., `.btn-primary` in dark mode), use `--color-accent-fg` (`#102019`) — not `--color-fg` (`#f5f1e8`). `--color-fg` has only 1.7:1 contrast against `#84d6bb` and must not be used as foreground on mint fills. `--color-bg` (`#101418`) also provides AAA contrast (11.3:1) on mint and may be used as a text color on mint fills when the accent-fg token is unavailable. This ensures the solid-CTA pattern lands cleanly without a separate token override.

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
