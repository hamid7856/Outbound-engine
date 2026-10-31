# StackRadar

StackRadar finds companies that have **just started using Zendesk, Intercom, Gorgias or HubSpot**. It also flags companies that **switched** from a competing helpdesk tool.

It runs free every week on GitHub Actions and needs no paid data providers.

**Repo:** https://github.com/hamid7856/Outbound-engine  ·  **Results:** [`scan-results` branch](https://github.com/hamid7856/Outbound-engine/tree/scan-results/data)  ·  **Runs:** [Actions](https://github.com/hamid7856/Outbound-engine/actions)

> Part of the Smart Instinct GTM toolkit. Team standards live in the [`handbook`](../../../handbook) repo.

## What it does

Every Monday, StackRadar checks each website on its list:

1. **Homepage code**: looks for chat widgets and scripts, such as `widget.intercom.io` or `static.zdassets.com`.
2. **Google Tag Manager**: reads the site's Tag Manager setup too, since many widgets are loaded through it.
3. **Help-centre subdomains**: checks where addresses like `support.acme.com` point. For example, `support.acme.com` pointing to `acme.zendesk.com` means Acme uses Zendesk.

It then compares the results with previous weeks:

- **New adopter**: a tool shows up on a site that never had it.
- **Dropped**: a tool has been missing for 2 scans in a row.

## Where the results are

Results are saved on the **[`scan-results`](https://github.com/hamid7856/Outbound-engine/tree/scan-results/data)** branch, not on `main`. Start with **`data/latest_new_adopters.csv`**. What each file and column means is explained in [docs/output-files.md](docs/output-files.md).

The first scan only records a baseline. New adopters start appearing from the second weekly run.

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q                                   # offline tests
stackradar --tranco-top 0 --limit 50        # scan domains/custom.txt
```

## Documentation

| Doc | For |
|---|---|
| [docs/runbook.md](docs/runbook.md) | First-time setup, running scans, troubleshooting |
| [docs/architecture.md](docs/architecture.md) | How the code is organised and how data flows |
| [docs/detection.md](docs/detection.md) | Detection rules, change rules, how to add a tool |
| [docs/output-files.md](docs/output-files.md) | Every output file and column |
| [docs/decisions/](docs/decisions/) | Why key design decisions were made (ADRs) |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to make a change |
| [CHANGELOG.md](CHANGELOG.md) | What changed in each version |
| [CLAUDE.md](CLAUDE.md) | Instructions for Claude when it works in this repo |
