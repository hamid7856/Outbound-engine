# Runbook

## First-time setup

1. Push this repo to the `smart-instinct` GitHub organization. The handbook's `setup/github-org-setup.md` walks through it.
2. In **Settings → Actions → General → Workflow permissions**, choose **Read and write permissions**. The scan needs this to push to `scan-results`.
3. In **Settings → Rules → Rulesets**, protect `main`: require a pull request, require the `CI` checks to pass, and block force pushes. Don't protect `scan-results` this way, because the bot must be able to push to it.
4. Test it: go to **Actions → Weekly scan → Run workflow** and set `limit` to `300`. It should finish in a few minutes and create the `scan-results` branch.
5. Run the baseline: **Run workflow** again with `limit` set to `0`. After that, the scan runs every Monday at 01:17 UTC.

## Everyday tasks

| Task | How |
|---|---|
| See this week's new adopters | `scan-results` branch → `data/latest_new_adopters.csv` |
| Add your own target companies | Open a pull request adding lines to `domains/custom.txt` |
| Add an export (Apollo, Vibe, LinkedIn…) | Open a pull request adding a CSV to `domains/imports/`. It needs a `domain`, `website` or `url` column |
| Scan more or fewer top sites | Run the workflow with `tranco_top`; for a permanent change, edit the default in `weekly-scan.yml` |
| Refresh the Tranco list | Run with `refresh_tranco: true`. New domains get a baseline first, so they won't show as new adopters straight away |
| Run a scan right now | **Actions → Weekly scan → Run workflow** |

## Monitoring

- **Weekly check**: each run's summary page shows the last 20 lines of its log.
- **`runs.csv`**: the `readable` count should stay steady. A sharp drop usually means GitHub's runners are being blocked, or there's a network problem.
- **Failures**: GitHub emails you about failed workflow runs. Make sure notifications are on under GitHub **Settings → Notifications → Actions**.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `Permission denied` / `403` when pushing results | Workflow permissions aren't set to read and write (setup step 2) |
| Tranco download fails | tranco-list.eu is down. Re-run later; the saved list is reused anyway |
| Run hits the 5-hour limit | Lower `tranco_top`. Any domains it didn't reach are scanned first next run |
| Too many `hubspot` adopters | Filter `evidence` for `usemessages` (live chat). See detection.md |
| A known user isn't detected | Check the site's source for the widget host. If it's missing, the widget probably loads after login or after the cookie banner, which StackRadar can't see |
| A false positive | Add a negative test case and tighten the regex in `signatures.py` |

## Costs

Free tier limits change, so check GitHub's current pricing page.

- **Public repos**: GitHub Actions minutes are free.
- **Private repos**: there's a monthly allowance of free minutes.
- **Current usage**: a weekly scan of 50,000 domains takes roughly 30–60 minutes.
