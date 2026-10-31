# Output files (on the `scan-results` branch, under `data/`)

> These columns are a contract. New columns are only ever added at the end. Renaming or removing a column needs a major version bump.

## `latest_new_adopters.csv`, `new_adopters/YYYY-MM-DD.csv`

| Column | Meaning |
|---|---|
| `domain` | Company website, e.g. `acme.com` |
| `tech` | `zendesk`, `intercom`, `gorgias` or `hubspot` |
| `detected_on` | Date (UTC) of the scan that first saw it |
| `evidence` | What matched: `html:…`, `gtm:<id>:…` or `dns:<host>-><target>` |
| `source` | Which list the domain came from: `custom`, `import:<file>` or `tranco` |
| `is_shopify` | `yes`/`no` |
| `also_uses` | Other helpdesk tools active on the site, separated by `;` |
| `switched_from` | Helpdesk tools that are dropped or disappearing on the site, separated by `;` |

## `dropped/YYYY-MM-DD.csv`

| Column | Meaning |
|---|---|
| `domain`, `tech`, `source` | As above |
| `dropped_on` | Date the drop was confirmed (the 2nd miss) |
| `first_seen`, `last_seen` | When the tool was first and last detected |
| `now_uses` | Helpdesk tools active on the site now |

## State files (used by the scanner; also handy for analysis)

| File | Contents |
|---|---|
| `domains.csv` | One row per domain: `source`, `first_scanned`, `last_attempt`, `last_ok`, `consecutive_failures`, `is_shopify` |
| `tech_state.csv` | One row per domain and tool: `status` (`active`/`dropped`), `first_seen`, `last_seen`, `misses`, `baseline` (`yes` means it was already there at the first scan), `evidence` |
| `runs.csv` | One row per run: `date`, `version`, `domains_listed`, `scanned`, `readable`, `new_adopters`, `dropped`, `minutes` |
| `tranco_top.txt` | The frozen list of Tranco domains |
