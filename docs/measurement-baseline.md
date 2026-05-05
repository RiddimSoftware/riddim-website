# Website Measurement Baseline Decision

**Decision date:** 2026-05-05
**Decided by:** Autonomous Developer subagent for `WEB-8`
**Revisit trigger:** See "When to revisit" below.

---

## Options Compared

| Option | Cookie-free? | Cost | Setup effort | What it answers |
|---|---|---|---|---|
| **CloudFront standard logs** | Yes | S3 storage (~cents/mo) | Low — enable in console, query with Athena or download CSV | Total requests, status codes, paths requested, referrer headers, edge location |
| **No-cookie analytics (e.g. Plausible, Fathom)** | Yes (GDPR-friendly) | $9–$14/mo per service | Medium — add script tag, configure domain | Unique visitors, page views, referrers, outbound link clicks, country |
| **No measurement (deliberate deferral)** | N/A | $0 | None | None until decision is revisited |

---

## Recommendation: CloudFront Standard Logs

**Recommended baseline: enable CloudFront standard logging to an S3 bucket.**

### Rationale

- Zero cookies, zero compliance overhead, no banner required.
- Already available on the existing S3/CloudFront stack at negligible cost.
- Answers the baseline questions that matter for the current static site refresh: total visits by request volume, product page visits, referrers when the header is present, and deploy-to-deploy trend.
- No third-party script loaded by visitors.
- Requires one AWS console change and no code changes to the website.
- Fits the current S3/CloudFront hosting model already documented in [./release-process.md](./release-process.md).

### What it does not answer

- Unique visitors (logs are per-request, not per-session).
- Outbound link clicks to App Store or other external destinations (no JavaScript event tracking).
- Product page engagement depth.

For this baseline, "product link clicks" means requests to first-party product pages such as `/products/epac.html` or `/products/reach.html`, which CloudFront logs can capture. It does not mean outbound App Store or external CTA clicks.

If outbound CTA clicks or unique visitors become important, a no-cookie SaaS (Plausible/Fathom) is the natural upgrade and should be handled as a separate follow-up ticket.

---

## Baseline Questions and Where to Find Answers

Once CloudFront standard logs are enabled, the following baseline questions can be answered by downloading logs from S3 and grepping/parsing with standard tools:

| Question | How to answer |
|---|---|
| Total visits (request baseline) | `wc -l` on combined log files, then subtract obvious bot noise and HEAD/OPTIONS as needed |
| Top paths | `awk '{print $8}' *.log \| sort \| uniq -c \| sort -rn \| head -20` |
| Referrers (when sent by the client) | `awk '{print $10}' *.log \| sort \| uniq -c \| sort -rn \| head -20` |
| Product page visits / internal product-link usage | `awk '{print $8}' *.log \| grep '^/products/' \| sort \| uniq -c \| sort -rn` |
| 4xx/5xx errors | `awk '{print $9}' *.log \| grep -E '^[45]' \| sort \| uniq -c` |
| Deploy-to-deploy trend | Compare the same path/referrer counts across release windows using the deploy timestamps in `version.json` or release history |

CloudFront logs arrive in S3 within ~1 hour of requests. Log format reference: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/AccessLogs.html

Treat this as a directional baseline, not audited traffic reporting: request counts are good enough for trend checks, but they are not the same thing as unique visitors.

---

## Setup (follow-up ticket scope)

Enabling CloudFront standard logs requires:
1. Create or designate an S3 bucket for logs (e.g. `riddim-website-logs`).
2. In the CloudFront distribution for `riddimsoftware.com`, enable standard logging → point at the bucket.
3. Set an S3 lifecycle rule to expire logs after 90 days (cost control).
4. Record the chosen bucket name and retention window in [./release-process.md](./release-process.md) if the team wants the operational runbook to stay fully current.

This is a sub-one-day AWS task, so it stays out of `WEB-8` and should be split into a follow-up Linear issue, for example:
`Enable CloudFront standard logging for riddimsoftware.com`

---

## When to Revisit

Revisit this decision if any of the following occur:
- Traffic grows enough that per-request logs become unwieldy (> ~50k requests/day).
- The team needs unique visitor counts or outbound App Store / external CTA click tracking for product prioritization.
- A product marketing initiative requires conversion or referral funnel data.

Until then, CloudFront standard logs are sufficient and require no maintenance.