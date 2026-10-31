# 0002: Store scan results on a separate `scan-results` branch

- **Status:** Accepted
- **Date:** 2026-10-31

## Context

Every week the scanner produces several MB of CSV. If that were committed to `main`:

- Code history would get noisy.
- Pull requests would conflict with bot commits.
- Branch protection on `main` would block the bot.

## Decision

Code stays on `main`, which is protected. The workflow writes results to an orphan branch called `scan-results`, which shares no history with `main`.

## Consequences

- `main` stays clean and protected, and the bot never needs to bypass protection.
- Results keep a full weekly history in git.
- People need to know to switch to the `scan-results` branch to find results. The README says this up front.
- If results ever move to a database or Google Sheets, this branch can be retired.
