# Website Measurement Baseline Decision

**Decision date:** 2026-05-01
**Decided by:** Autonomous Scope Orchestrator (WEBSITE-8)
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
- Answers the baseline questions for a low-traffic org website: total requests, top paths, referrers, and 4xx/5xx error rate.
- No third-party script loaded by visitors.
- Requires one AWS console change and no code changes to the website.

### What it does not answer

- Unique visitors (logs are per-request, not per-session).
- Outbound link clicks (no JavaScript event tracking).
- Product page engagement depth.

If those questions become important, a no-cookie SaaS (Plausible/Fathom) is the natural upgrade — a separate follow-up ticket.

---

## Baseline Questions and Where to Find Answers

Once CloudFront standard logs are enabled, the following can be answered by downloading logs from S3 and grepping/parsing with standard tools:

| Question | How to answer |
|---|---|
| Total visits (requests) | `wc -l` on combined log files (subtract HEAD/OPTIONS) |
| Top paths | `awk '{print $8}' *.log \| sort \| uniq -c \| sort -rn \| head -20` |
| Referrers | `awk '{print $10}' *.log \| sort \| uniq -c \| sort -rn \| head -20` |
| 4xx/5xx errors | `awk '{print $9}' *.log \| grep -E '^[45]' \| sort \| uniq -c` |
| Deploy-to-deploy trend | Compare log file count/dates before and after a deploy |

CloudFront logs arrive in S3 within ~1 hour of requests. Log format reference: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/AccessLogs.html

---

## Setup (follow-up ticket scope)

Enabling CloudFront standard logs requires:
1. Create or designate an S3 bucket for logs (e.g. `riddim-website-logs`).
2. In the CloudFront distribution for `riddimsoftware.com`, enable standard logging → point at the bucket.
3. Set an S3 lifecycle rule to expire logs after 90 days (cost control).

This is a 30-minute AWS console task. A separate Jira ticket is recommended:
`[WEBSITE]: Enable CloudFront standard logging for riddimsoftware.com`

---

## When to Revisit

Revisit this decision if any of the following occur:
- Traffic grows enough that per-request logs become unwieldy (> ~50k requests/day).
- The team needs unique visitor counts or outbound click tracking for product prioritization.
- A product marketing initiative requires conversion or referral funnel data.

Until then, CloudFront standard logs are sufficient and require no maintenance.
