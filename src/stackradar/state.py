"""Week-over-week state: remembers what was seen on each domain and works out
what is new (adopted) or gone (dropped) since the last successful scan.

Rules (see docs/detection.md):
- The first successful scan of a domain is a baseline; nothing on it is "new".
- A tool is NEW when it appears on a domain that has a baseline and never had it.
- A tool is DROPPED after DROP_AFTER_MISSES successful scans in a row without it.
- A failed scan (site down / blocked) changes nothing.
"""

import csv
from pathlib import Path

from .signatures import HELPDESK_TECHS, TARGET_TECHS

DROP_AFTER_MISSES = 2

DOMAIN_FIELDS = [
    "domain",
    "source",
    "first_scanned",
    "last_attempt",
    "last_ok",
    "consecutive_failures",
    "is_shopify",
]
TECH_FIELDS = [
    "domain",
    "tech",
    "status",
    "first_seen",
    "last_seen",
    "misses",
    "baseline",
    "evidence",
]
NEW_FIELDS = [
    "domain",
    "tech",
    "detected_on",
    "evidence",
    "source",
    "is_shopify",
    "also_uses",
    "switched_from",
]
DROP_FIELDS = ["domain", "tech", "dropped_on", "first_seen", "last_seen", "source", "now_uses"]
RUN_FIELDS = [
    "date",
    "version",
    "domains_listed",
    "scanned",
    "readable",
    "new_adopters",
    "dropped",
    "minutes",
]


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def last_attempts(data_dir: Path) -> dict[str, str]:
    return {r["domain"]: r["last_attempt"] for r in read_csv(data_dir / "domains.csv")}


def update_state(
    data_dir: Path, today: str, domain_sources: dict[str, str], results: dict[str, dict | None]
) -> tuple[list[dict], list[dict]]:
    """Merge one run's results into the state files. Returns (new_adopters, dropped)."""
    dom_rows = {r["domain"]: r for r in read_csv(data_dir / "domains.csv")}
    by_domain: dict[str, dict[str, dict]] = {}
    for r in read_csv(data_dir / "tech_state.csv"):
        by_domain.setdefault(r["domain"], {})[r["tech"]] = r
    new_adopters: list[dict] = []
    dropped: list[dict] = []

    for domain, found in results.items():
        drow = dom_rows.get(domain) or {
            "domain": domain,
            "source": domain_sources.get(domain, ""),
            "first_scanned": "",
            "last_attempt": "",
            "last_ok": "",
            "consecutive_failures": "0",
            "is_shopify": "",
        }
        dom_rows[domain] = drow
        drow["last_attempt"] = today
        if found is None:
            drow["consecutive_failures"] = str(int(drow["consecutive_failures"] or 0) + 1)
            continue

        had_baseline = bool(drow["last_ok"])
        drow.update(
            consecutive_failures="0",
            last_ok=today,
            first_scanned=drow["first_scanned"] or today,
            is_shopify="yes" if "shopify" in found else "no",
        )
        techs = by_domain.setdefault(domain, {})

        newly_dropped = []
        for tech, row in techs.items():  # tools we already knew about
            if tech in found:
                row.update(status="active", last_seen=today, misses="0", evidence=found[tech])
            elif row["status"] == "active":
                row["misses"] = str(int(row["misses"] or 0) + 1)
                if int(row["misses"]) >= DROP_AFTER_MISSES:
                    row["status"] = "dropped"
                    newly_dropped.append(row)

        fresh = []
        for tech, ev in found.items():  # tools never seen on this domain
            if tech in techs:
                continue
            techs[tech] = {
                "domain": domain,
                "tech": tech,
                "status": "active",
                "first_seen": today,
                "last_seen": today,
                "misses": "0",
                "baseline": "no" if had_baseline else "yes",
                "evidence": ev,
            }
            if had_baseline and tech in TARGET_TECHS:
                fresh.append((tech, ev))

        active = sorted(
            t for t, r in techs.items() if r["status"] == "active" and t in HELPDESK_TECHS
        )
        fading = sorted(
            t
            for t, r in techs.items()
            if t in HELPDESK_TECHS and (r["status"] == "dropped" or int(r["misses"] or 0) > 0)
        )
        for tech, ev in fresh:
            new_adopters.append(
                {
                    "domain": domain,
                    "tech": tech,
                    "detected_on": today,
                    "evidence": ev,
                    "source": drow["source"],
                    "is_shopify": drow["is_shopify"],
                    "also_uses": ";".join(t for t in active if t != tech),
                    "switched_from": ";".join(t for t in fading if t != tech),
                }
            )
        for row in newly_dropped:
            if row["tech"] in HELPDESK_TECHS:
                dropped.append(
                    {
                        "domain": domain,
                        "tech": row["tech"],
                        "dropped_on": today,
                        "first_seen": row["first_seen"],
                        "last_seen": row["last_seen"],
                        "source": drow["source"],
                        "now_uses": ";".join(active),
                    }
                )

    write_csv(
        data_dir / "domains.csv",
        DOMAIN_FIELDS,
        sorted(dom_rows.values(), key=lambda r: r["domain"]),
    )
    write_csv(
        data_dir / "tech_state.csv",
        TECH_FIELDS,
        [r for d in sorted(by_domain) for _, r in sorted(by_domain[d].items())],
    )
    return new_adopters, dropped


def write_reports(
    data_dir: Path, today: str, new_adopters: list[dict], dropped: list[dict], run_info: dict
) -> None:
    write_csv(data_dir / "new_adopters" / f"{today}.csv", NEW_FIELDS, new_adopters)
    write_csv(data_dir / "latest_new_adopters.csv", NEW_FIELDS, new_adopters)
    write_csv(data_dir / "dropped" / f"{today}.csv", DROP_FIELDS, dropped)
    runs = read_csv(data_dir / "runs.csv")
    runs.append(run_info)
    write_csv(data_dir / "runs.csv", RUN_FIELDS, runs)
