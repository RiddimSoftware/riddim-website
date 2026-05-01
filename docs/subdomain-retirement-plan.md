# Post-Launch Subdomain Retirement Plan

**Status:** Active — legacy subdomains remain live until consolidation is deployed and verified.
**Last updated:** 2026-05-01
**Owner:** sunny@riddimsoftware.com

---

## Prerequisite: Consolidation Must Be Live First

**No subdomain retirement action (redirect, archive, or deletion) may begin until:**

1. All consolidated product pages under `riddimsoftware.com` are deployed and accessible.
2. The live health check (`python3 scripts/validate.py --live`) passes for all consolidated routes.
3. At minimum 2 weeks of post-launch observation with no user-reported breakage.

Until these conditions are met, all subdomains listed below remain live and unmodified.

---

## Known Legacy Subdomains

| Subdomain | Hosted on | Consolidation route | Proposed post-launch action |
|---|---|---|---|
| `epac.riddimsoftware.com` | AWS Amplify | `/epac/` | **Redirect** → `riddimsoftware.com/epac/` after verification window |
| `nether.riddimsoftware.com` | AWS Amplify | `/portal-door/` | **Redirect** → `riddimsoftware.com/portal-door/` after verification window |
| `sonnio.riddimsoftware.com` | AWS Amplify | `/sonnio/` | **Redirect** → `riddimsoftware.com/sonnio/` after verification window |

External sites (`blindfold.lol`, App Store listings, `github.com/sunnypurewal`) are not Riddim-hosted subdomains and are **out of scope** for retirement — they remain as CTAs on their product pages indefinitely.

---

## Retirement Sequence (per subdomain)

Work through each subdomain independently. Do not attempt all three simultaneously.

### Phase 1 — Redirect (reversible)
1. Verify the corresponding consolidated route (`/epac/`, `/portal-door/`, `/sonnio/`) returns HTTP 200.
2. In the AWS Amplify console for the subdomain app, add a redirect rule: `/<*>` → `https://riddimsoftware.com/<product>/` with HTTP 301.
3. Test: `curl -I https://<subdomain>.riddimsoftware.com` should return `301` pointing at the main-site route.
4. Monitor for 2 weeks. If no breakage, proceed to Phase 2.

**Rollback:** Remove the Amplify redirect rule. The Amplify app continues serving the original content immediately.

### Phase 2 — Archive Amplify app (reversible)
1. Confirm Phase 1 has been stable for ≥ 2 weeks.
2. Take a snapshot/export of the Amplify app's current build output as a zip archive stored in S3 or locally.
3. Disable the Amplify app (do not delete). This stops serving the content while keeping the configuration restorable.
4. Verify the subdomain DNS now returns NXDOMAIN or a Amplify parking page — confirm the 301 redirect from Phase 1 is no longer needed (the subdomain itself is gone).

**Rollback:** Re-enable the Amplify app. DNS may take minutes to propagate.

### Phase 3 — DNS and Amplify cleanup (destructive, irreversible)
1. Confirm Phase 2 has been stable for ≥ 30 days with no support reports.
2. Delete the Amplify app and remove the DNS CNAME record for the subdomain.
3. Update `scripts/validate.py` to remove the retired subdomain from live health checks.
4. Log the deletion in this document under "Completed Retirements."

**Rollback:** Not possible after Phase 3. Requires re-provisioning an Amplify app and DNS record from scratch.

---

## Separation: Reversible vs. Destructive Work

| Phase | Type | Reversible? | Requires follow-up ticket |
|---|---|---|---|
| Phase 1 — Redirect | Amplify config change | Yes, immediately | No |
| Phase 2 — Disable Amplify | Amplify disable | Yes, within Amplify retention | Recommended |
| Phase 3 — Delete DNS + Amplify | Infrastructure deletion | No | Required |

Create a separate Jira ticket before executing Phase 2 or Phase 3 for each subdomain. Do not combine multiple subdomains in one ticket.

---

## Minimum Verification Before Any Change

Before any Phase 1 action on a subdomain, confirm:

- `curl -s -o /dev/null -w "%{http_code}" https://riddimsoftware.com/<route>/` → `200`
- `python3 scripts/validate.py --live` passes for the consolidated route
- No open support tickets referencing the subdomain in the past 30 days

---

## Completed Retirements

*(None yet — consolidation not yet verified as of 2026-05-01)*

---

## Follow-Up Tickets to Create (Post-Verification)

Once consolidation is live and the 2-week window passes, create one ticket per subdomain per phase:

- `[WEBSITE]: Redirect epac.riddimsoftware.com → riddimsoftware.com/epac/ (Phase 1)`
- `[WEBSITE]: Redirect nether.riddimsoftware.com → riddimsoftware.com/portal-door/ (Phase 1)`
- `[WEBSITE]: Redirect sonnio.riddimsoftware.com → riddimsoftware.com/sonnio/ (Phase 1)`
- Phase 2 and 3 tickets follow after Phase 1 is stable.
