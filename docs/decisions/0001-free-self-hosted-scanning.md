# 0001: Detect tools ourselves instead of buying technographic data

- **Status:** Accepted
- **Date:** 2026-10-30

## Context

We want companies that recently adopted Zendesk, Intercom, Gorgias or HubSpot.

Paid providers (BuiltWith, HG Insights, ZoomInfo) offer "first detected" dates. Apollo and Vibe Prospecting, which we already have, only show the tools a company currently uses, not when it adopted them. Budget is limited.

## Decision

We'll build a scanner that detects tools from public signals: homepage scripts, Google Tag Manager containers and help-centre DNS records. We'll find adoption by comparing weekly snapshots, and run it on GitHub Actions.

## Consequences

- **Good:** It costs nothing, we fully control detection rules, and we can track any tool we like.
- **Bad:** Adoption dates are only accurate to about a week, and only from our first scan onwards. Widgets hidden behind a login or cookie banner are missed. Some sites block bots.
- **Mitigation:** Apollo and Vibe can still be used to enrich new adopters (contacts, company size) after detection.
