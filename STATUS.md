# Status: what's happening now

This is the project's working memory. **Read it at the start of every session.** At the end of every session, update it in the same pull request as your work.

Keep the top section current. Add to the log at the bottom, newest first, and never delete log entries.

## Current state (updated 2026-10-31)

**Version:** 0.1.0, built and passing offline tests, but **not yet pushed to GitHub and not yet run live.**

### Up next (in order)

1. [ ] Push this repo to `main` on https://github.com/hamid7856/Outbound-engine.
2. [ ] In the repo settings, set workflow permissions to **Read and write**.
3. [ ] Run **Actions → Weekly scan** with `limit: 300` and check `scan-results/data/` for sensible `evidence` values.
4. [ ] Run the full baseline with `limit: 0`. New adopters start appearing from the next weekly run.
5. [ ] Decide whether the repo should be public or private. It's **public** right now. Private means GitHub's free plan can't block direct pushes to `main`.
6. [ ] Add the teammate's GitHub username to `.github/CODEOWNERS` and to CONTEXT.md.
7. [ ] Create the `handbook` repo and push the prepared handbook.
8. [ ] After the first real results, tune the detection rules and decide which Apollo/Vibe exports to add to `domains/imports/` (needs the user's OK on credits).

### In progress

**Who's working on what lives in GitHub, not in this file.** Check open issues that have someone assigned, and open (including draft) pull requests. This file is only updated when work is merged.

### Blocked or waiting on

- Nothing is pushed yet. The Cowork session that built this couldn't push, because the repo wasn't attached to that session.

## Session log

### 2026-10-31: Cowork session (initial build)

- Researched tools for finding new tool adopters. Chose a free, self-built scanner over paid technographic data (ADR 0001).
- Built StackRadar 0.1.0:
  - Detects tools from homepage HTML, Google Tag Manager containers and help-centre DNS records.
  - Compares weekly snapshots, with a baseline on the first scan and a drop confirmed after 2 misses.
  - Weekly GitHub Actions run that saves results to the `scan-results` branch (ADR 0002).
  - CI on every pull request, documentation, and the handbook with team standards.
- Named the project "StackRadar". Agreed on one repo per app and shared standards in `handbook`.
- Added CONTEXT.md and STATUS.md so future sessions share memory.
