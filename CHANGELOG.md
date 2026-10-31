# Changelog

All notable changes to this project are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Added CONTEXT.md and STATUS.md as shared memory for every Claude session, plus start/end-of-session rules in CLAUDE.md.

### Changed

- Added links to the GitHub repo (hamid7856/Outbound-engine) in the README, runbook, `pyproject.toml` and CODEOWNERS.

## [0.1.0] - 2026-10-31

### Added

- Detection of Zendesk, Intercom, Gorgias and HubSpot. It reads homepage HTML, Google Tag Manager containers and help-centre CNAMEs.
- Competitor tracking for switch detection: Freshdesk, Help Scout, Kustomer, Gladly, Re:amaze, Tidio, LiveChat and Drift. Shopify is flagged too.
- Weekly diff: a baseline on the first scan, new adopters, drops after 2 misses, and `also_uses` / `switched_from` columns.
- Domain sources: Tranco top-N (kept fixed between runs), `domains/custom.txt` and CSV/TXT files in `domains/imports/`.
- A weekly GitHub Actions scan that writes results to the `scan-results` branch.
- CI on every pull request (ruff and pytest), Dependabot, and project documentation.

[Unreleased]: https://github.com/hamid7856/Outbound-engine/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hamid7856/Outbound-engine/releases/tag/v0.1.0
