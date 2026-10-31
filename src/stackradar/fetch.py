"""Network layer: fetch a site's homepage, its Google Tag Manager container and
help-centre DNS records, and return which tools were detected."""

import asyncio
import time

import dns.asyncresolver
import dns.exception
import httpx

from .signatures import GTM_ID_RE, HELP_SUBDOMAINS, match_cname, match_html

MAX_BYTES = 2_000_000  # stop reading a homepage after 2 MB
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


async def fetch_text(client: httpx.AsyncClient, url: str) -> tuple[int, str]:
    async with client.stream("GET", url) as r:
        chunks, size = [], 0
        async for chunk in r.aiter_bytes():
            chunks.append(chunk)
            size += len(chunk)
            if size >= MAX_BYTES:
                break
        return r.status_code, b"".join(chunks).decode(errors="ignore")


def looks_blocked(status: int, body: str) -> bool:
    if status >= 400 or len(body) < 300:
        return True
    head = body[:5000].lower()
    return ("just a moment..." in head and "cloudflare" in head) or "captcha-delivery" in head


async def fetch_homepage(client, domain):
    for url in (f"https://{domain}/", f"https://www.{domain}/", f"http://{domain}/"):
        try:
            status, body = await fetch_text(client, url)
            if not looks_blocked(status, body):
                return body
        except (httpx.HTTPError, UnicodeError, ValueError):
            continue
    return None


class GTMCache:
    def __init__(self, client):
        self.client = client
        self.tasks: dict[str, asyncio.Task] = {}

    async def get(self, gtm_id: str) -> str:
        if gtm_id not in self.tasks:
            self.tasks[gtm_id] = asyncio.create_task(self._fetch(gtm_id))
        return await self.tasks[gtm_id]

    async def _fetch(self, gtm_id):
        try:
            _, body = await fetch_text(
                self.client, f"https://www.googletagmanager.com/gtm.js?id={gtm_id}"
            )
            return body
        except httpx.HTTPError:
            return ""


async def cname_checks(resolver, domain) -> dict:
    found = {}

    async def one(sub):
        host = f"{sub}.{domain}"
        try:
            ans = await resolver.resolve(host, "CNAME")
        except (dns.exception.DNSException, OSError):
            return
        for rr in ans:
            for tech, ev in match_cname(str(rr.target)).items():
                found.setdefault(tech, f"dns:{host}->{ev}")

    await asyncio.gather(*(one(s) for s in HELP_SUBDOMAINS))
    return found


async def scan_domain(domain, client, gtm, resolver):
    """Return None if the site could not be read, else {tech: evidence}."""
    html = await fetch_homepage(client, domain)
    if html is None:
        return None
    found = {t: f"html:{e}" for t, e in match_html(html).items()}
    for gtm_id in list(dict.fromkeys(GTM_ID_RE.findall(html)))[:2]:
        js = await gtm.get(gtm_id)
        for t, e in match_html(js).items():
            found.setdefault(t, f"gtm:{gtm_id}:{e}")
    for t, e in (await cname_checks(resolver, domain)).items():
        found.setdefault(t, e)
    return found


async def run_scans(domains, concurrency, deadline):
    results: dict[str, dict | None] = {}
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=20)
    timeout = httpx.Timeout(15.0, connect=8.0)
    resolver = dns.asyncresolver.Resolver()
    resolver.lifetime = 4.0
    sem = asyncio.Semaphore(concurrency)
    done = 0
    start = time.time()

    async with httpx.AsyncClient(
        headers={"User-Agent": UA, "Accept-Language": "en"},
        follow_redirects=True,
        timeout=timeout,
        limits=limits,
        verify=False,
    ) as client:
        gtm = GTMCache(client)

        async def worker(d):
            nonlocal done
            async with sem:
                if time.time() > deadline:
                    return
                try:
                    results[d] = await asyncio.wait_for(
                        scan_domain(d, client, gtm, resolver), timeout=60
                    )
                except Exception:  # noqa: BLE001 - one bad site must not stop the run
                    results[d] = None
                done += 1
                if done % 1000 == 0:
                    rate = done / max(time.time() - start, 1)
                    print(f"  scanned {done:,}/{len(domains):,} ({rate:.0f}/s)", flush=True)

        await asyncio.gather(*(worker(d) for d in domains))
    return results
