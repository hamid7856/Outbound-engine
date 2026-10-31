"""StackRadar command line.

stackradar                         # weekly run with defaults
stackradar --tranco-top 0          # only your own lists
stackradar --limit 300             # quick test
"""

import argparse
import asyncio
import datetime as dt
import random
import time
from pathlib import Path

from . import __version__
from .fetch import run_scans
from .signatures import VENDOR_DOMAINS
from .sources import load_domains
from .state import last_attempts, update_state, write_reports


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="stackradar", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--version", action="version", version=f"stackradar {__version__}")
    ap.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="where state and reports are read/written (default: ./data)",
    )
    ap.add_argument(
        "--domains-dir",
        type=Path,
        default=Path("domains"),
        help="where custom.txt and imports/ live (default: ./domains)",
    )
    ap.add_argument(
        "--tranco-top",
        type=int,
        default=50000,
        help="how many Tranco top sites to include (0 = none)",
    )
    ap.add_argument(
        "--refresh-tranco",
        action="store_true",
        help="re-download the Tranco list instead of reusing the saved slice",
    )
    ap.add_argument("--concurrency", type=int, default=150)
    ap.add_argument(
        "--max-minutes",
        type=float,
        default=300,
        help="stop starting new sites after this long; the rest go first next run",
    )
    ap.add_argument("--limit", type=int, default=0, help="scan only N domains (testing)")
    return ap


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    data_dir: Path = args.data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    today = dt.datetime.now(dt.UTC).date().isoformat()

    print(f"StackRadar {__version__} - loading domain lists:")
    sources = load_domains(args.domains_dir, data_dir, args.tranco_top, args.refresh_tranco)
    for v in VENDOR_DOMAINS:
        sources.pop(v, None)

    # least-recently-attempted first, so a run that is cut short resumes next time
    last = last_attempts(data_dir)
    order = list(sources)
    random.shuffle(order)  # spread load across hosting providers
    order.sort(key=lambda d: last.get(d, ""))
    if args.limit:
        order = order[: args.limit]

    print(f"Scanning {len(order):,} domains (concurrency {args.concurrency})...")
    t0 = time.time()
    results = asyncio.run(run_scans(order, args.concurrency, t0 + args.max_minutes * 60))
    readable = sum(1 for v in results.values() if v is not None)

    new_adopters, dropped = update_state(data_dir, today, sources, results)
    minutes = (time.time() - t0) / 60
    write_reports(
        data_dir,
        today,
        new_adopters,
        dropped,
        {
            "date": today,
            "version": __version__,
            "domains_listed": len(sources),
            "scanned": len(results),
            "readable": readable,
            "new_adopters": len(new_adopters),
            "dropped": len(dropped),
            "minutes": f"{minutes:.1f}",
        },
    )

    print(
        f"\nDone in {minutes:.1f} min: {len(results):,} scanned, {readable:,} readable, "
        f"{len(new_adopters)} new adopters, {len(dropped)} dropped."
    )
    counts: dict[str, int] = {}
    for n in new_adopters:
        counts[n["tech"]] = counts.get(n["tech"], 0) + 1
    for tech, c in sorted(counts.items()):
        print(f"  new {tech}: {c}")
