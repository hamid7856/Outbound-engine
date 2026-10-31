# Detection

## Signals

| Signal | Example | Strength |
|---|---|---|
| Widget/script host in homepage HTML | `widget.intercom.io`, `static.zdassets.com`, `config.gorgias.chat` | Strong |
| Same, inside the site's Google Tag Manager container | `gtm:GTM-ABC123:js.hs-scripts.com` | Strong |
| Help-centre subdomain CNAME | `dns:support.acme.com->acme.zendesk.com` | Strong (catches email-only helpdesks) |
| Link to the company's own hosted help centre | `acme.zendesk.com/hc` | Medium |

Rules match **script hosts and embed code**, never brand names in text. A blog post saying "we compared Zendesk and Intercom" must not match. A test enforces this.

### HubSpot caveat

The HubSpot tracking script (`js.hs-scripts.com`) is used by HubSpot Marketing customers too. `js.usemessages.com` (HubSpot live chat) is the stronger helpdesk signal. The `evidence` column shows which one matched.

## Change rules

Changing these rules requires an ADR. They're implemented in `state.py`.

1. **Baseline**: a domain's first readable scan only records what's there. Nothing is reported as new.
2. **New adopter**: a target tool (Zendesk, Intercom, Gorgias or HubSpot) appears on a domain that already has a baseline and has never shown that tool before.
3. **Dropped**: an active tool is missing for 2 readable scans in a row. One miss isn't enough, because widgets sometimes fail to load.
4. **Unreadable scan**: if the site is down, blocked by a Cloudflare challenge, or returns less than 300 bytes, nothing changes. The domain's failure counter goes up.
5. **Switched from**: helpdesk tools on that domain that are dropped or currently missing.

## Adding a new tool

1. Add an entry to `SIGNATURES` in `src/stackradar/signatures.py`, with `html` and `cname` regexes.
2. If it's a helpdesk or chat tool, add it to `HELPDESK_TECHS`. To report its new adopters, add it to `TARGET_TECHS` as well.
3. Add positive and negative cases to `tests/test_signatures.py`.
4. Add its vendor domain to `VENDOR_DOMAINS`.
5. After merging, run the workflow with `limit: 300` and check the `evidence` values look right.

Existing domains will report a newly added tool as "new" the next time it's seen. To avoid a one-off spike, add a target tool to `HELPDESK_TECHS` first, let it run for one week, and only then add it to `TARGET_TECHS`.
