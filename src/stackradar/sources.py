"""Where the list of domains to scan comes from.

<data>/tranco_top.txt   - frozen slice of the free Tranco top-sites list
                          (lives with the results so the universe stays stable)
domains/custom.txt      - your own list, one domain per line
domains/imports/*.csv   - exports from Apollo, Vibe Prospecting, LinkedIn,
                          Store Leads etc. Any column called domain / website /
                          url / company_domain is picked up automatically.
domains/imports/*.txt   - plain lists, one domain per line
"""

import csv
import io
import re
import zipfile
from pathlib import Path

import httpx

TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"
DOMAIN_COLUMNS = {
    "domain",
    "domains",
    "website",
    "websites",
    "url",
    "company_domain",
    "company domain",
    "company website",
    "website_url",
    "company_website",
    "primary_domain",
    "primary domain",
}


def normalize(raw: str) -> str | None:
    d = (raw or "").strip().lower()
    if not d or d.startswith("#"):
        return None
    d = re.sub(r"^[a-z]+://", "", d)
    d = d.split("/")[0].split("?")[0].split("#")[0].split(":")[0]
    if d.startswith("www."):
        d = d[4:]
    if "." not in d or " " in d or not re.fullmatch(r"[a-z0-9.-]+", d):
        return None
    return d


def fetch_tranco(path: Path, top_n: int) -> None:
    print(f"Downloading Tranco list (top {top_n:,})...")
    r = httpx.get(TRANCO_URL, timeout=120, follow_redirects=True)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        name = z.namelist()[0]
        lines = z.read(name).decode().splitlines()
    out = []
    for line in lines[:top_n]:
        parts = line.split(",")
        if len(parts) == 2:
            out.append(parts[1].strip())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n")
    print(f"Saved {len(out):,} domains to {path}")


def _read_txt(p: Path):
    yield from p.read_text(errors="ignore").splitlines()


def _read_csv(p: Path):
    with p.open(newline="", errors="ignore") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return
        cols = [c for c in reader.fieldnames if c and c.strip().lower() in DOMAIN_COLUMNS]
        if not cols:
            print(f"  ! {p.name}: no domain/website column found, skipped")
            return
        for row in reader:
            for c in cols:
                if row.get(c):
                    yield row[c]
                    break


def load_domains(
    domains_dir: Path, data_dir: Path, tranco_top: int, refresh_tranco: bool
) -> dict[str, str]:
    """Return {domain: source_label}. Earlier sources win on duplicates,
    so your own lists are labelled as such even if the site is also in Tranco."""
    ddir = domains_dir
    result: dict[str, str] = {}

    def add(values, label):
        n = 0
        for v in values:
            d = normalize(v)
            if d and d not in result:
                result[d] = label
                n += 1
        print(f"  {label}: {n:,} domains")

    custom = ddir / "custom.txt"
    if custom.exists():
        add(_read_txt(custom), "custom")

    imports = ddir / "imports"
    if imports.exists():
        for p in sorted(imports.iterdir()):
            if p.suffix.lower() == ".csv":
                add(_read_csv(p), f"import:{p.stem}")
            elif p.suffix.lower() == ".txt":
                add(_read_txt(p), f"import:{p.stem}")

    if tranco_top > 0:
        tpath = data_dir / "tranco_top.txt"
        if refresh_tranco or not tpath.exists():
            fetch_tranco(tpath, tranco_top)
        lines = list(_read_txt(tpath))[:tranco_top]
        add(lines, "tranco")

    return result
