# Architecture

## Data flow

```
 domains/custom.txt ─┐
 domains/imports/*  ─┼─► sources.py ─► list of domains ─► fetch.py (async) ─► {domain: {tech: evidence}}
 Tranco top-N       ─┘                                       │  homepage HTML
                                                             │  Google Tag Manager container
                                                             │  CNAMEs of support./help./kb. …
                                                             ▼
                                         signatures.py (match_html / match_cname)
                                                             │
                                                             ▼
                          state.py: compare with previous state ─► new adopters / dropped
                                                             │
                                                             ▼
                                     CSV files in --data-dir (scan-results branch)
```

## Modules

| Module | Responsibility | Depends on |
|---|---|---|
| `signatures.py` | Detection rules for each tool, plus pure matching functions | – |
| `sources.py` | Loads and normalises domain lists; downloads Tranco | httpx |
| `fetch.py` | All network I/O: homepage, GTM, DNS. Concurrency and timeouts | httpx, dnspython, signatures |
| `state.py` | Diff rules, state CSVs, reports. **No network.** | signatures |
| `cli.py` | Parses arguments, orders domains, runs everything | all |

Two modules are kept pure so they can be tested fully offline: `signatures.py` and `state.py`. Network code stays in `fetch.py`.

## Storage

State is stored as plain CSV files, and git provides the history.

- Code is on the `main` branch.
- Data is on the `scan-results` branch, written only by the weekly workflow. See [ADR 0002](decisions/0002-results-on-separate-branch.md).
- `tranco_top.txt` is kept with the data, so the set of domains stays the same from week to week.

CSV works well at the current scale: tens of thousands of domains, read by people and spreadsheets. If the list grows past a few hundred thousand domains, or other apps need to query it, move to SQLite or Postgres. That move would get its own ADR.

## Run lifecycle

1. Load the domain lists and remove the tool vendors' own websites.
2. Order domains with the least recently attempted first, so a run that times out resumes where it stopped next week.
3. Scan with 150 sites at once (the default), giving each site 60 seconds at most and stopping the whole run after `--max-minutes`.
4. Update the state files, then write reports and add a line to `runs.csv`.

## Future integration

Other Smart Instinct apps, such as the planned outbound email app, should read `latest_new_adopters.csv` from the `scan-results` branch. They should not import StackRadar's code. The CSV columns are the interface between apps (see `docs/output-files.md`).
