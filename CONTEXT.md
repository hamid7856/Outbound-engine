# Project context: read this first

This file is the project's long-term memory. Every Claude session (Cowork or Claude Code, on any teammate's machine) reads it before doing anything. It records **what we're building, why, and what has already been decided**, so nobody re-debates settled questions.

Update it, through a pull request, whenever a goal or decision changes. For what's happening right now, see [STATUS.md](STATUS.md).

## The goal

Smart Instinct is building an **outbound engine**: a set of small apps that find good prospects and reach them.

1. **Find:** StackRadar (this repo) detects companies that have just adopted Zendesk, Intercom, Gorgias or HubSpot. They have just bought helpdesk or CRM software, which is our buying signal.
2. **Enrich:** Apollo.io and Vibe Prospecting (both connected in Claude Cowork) add contacts and company data to those companies.
3. **Reach:**
   - **`mailroom`** (planned, long-term): checks sending domains' DNS records (SPF, DKIM, DMARC, MX), warms up inboxes and sends emails.
   - **LinkedIn content app** (teammate's project, separate repo): a LinkedIn content machine and profile-optimisation best practices.

**Current focus: StackRadar only.** The email app is a long-term plan. Don't start building it until it has an ADR.

## Decisions so far (don't re-open without an ADR)

| Decision | Why | Where recorded |
|---|---|---|
| Detect tools ourselves instead of buying data (BuiltWith, ZoomInfo, etc.) | Free. Apollo and Vibe don't record when a company adopted a tool | ADR 0001 |
| Find new adopters by comparing weekly snapshots | Free sources have no "first detected" date | docs/detection.md |
| Detect from homepage scripts, Google Tag Manager containers and help-centre DNS | Covers chat widgets and email-only helpdesks | docs/detection.md |
| Run on GitHub Actions, not the MacBook or an external SSD | The laptop sleeps; Actions is free and nothing is installed locally | docs/runbook.md |
| Save results to the `scan-results` branch, not `main` | Keeps the code history clean and lets `main` stay protected | ADR 0002 |
| Python 3.11+, ruff, pytest, GitHub Flow with squash merges | Simple and standard for both teammates and Claude | handbook |
| One repo per app, with shared standards in a `handbook` repo | Apps can change and deploy independently | handbook README |
| Domain sources: Tranco top 50k (kept fixed), `domains/custom.txt`, Apollo/Vibe exports in `domains/imports/` | Free broad coverage plus our own targets | docs/runbook.md |
| Output CSV columns are a contract | Future apps (enrichment, `mailroom`) will read them | docs/output-files.md |
| No open-source license | Private internal tool. Without a license the code stays all rights reserved | – |

## People and places

| What | Where |
|---|---|
| This repo | https://github.com/hamid7856/Outbound-engine (holds StackRadar) |
| Repo owner | @hamid7856 |
| Teammate | GitHub username not recorded yet. Builds the LinkedIn content app and also works in this repo |
| Team standards | `handbook` repo (repo not created yet; contents prepared) |
| Tools connected in Cowork | Apollo.io, Vibe Prospecting, Anysite GTM plugin (includes Wappalyzer technographics). Slack and Google Drive connections are incomplete |

## Constraints

- **Budget:** prefer free tools. Spending on credits (Apollo, Vibe) needs the user's OK first, every time.
- **Claude's sandbox can't reach live websites.** Detection can only be tested for real through a GitHub Actions run, e.g. with `limit: 300`.
- **Org policy:** don't include personal data about consumers or third parties. Business contact details (name, work email, role) are fine for internal business operations.
- **Compliance:** email and LinkedIn work follows `handbook/standards/security.md`, which covers anti-spam law and LinkedIn's limits on automation.
