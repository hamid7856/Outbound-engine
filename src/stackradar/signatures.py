"""Detection rules for helpdesk / chat / CRM tools.

Each tech has:
  html  - regexes matched against the homepage HTML and any Google Tag Manager
          container the page loads (widgets are often injected through GTM)
  cname - regexes matched against the CNAME of help-centre subdomains
          (support.example.com -> example.zendesk.com)

Patterns target script hosts and embed code, not plain mentions of the brand,
so a blog post that merely says "Zendesk" does not count as adoption.
"""

import re

# Tools whose NEW adoption we report.
TARGET_TECHS = ["zendesk", "intercom", "gorgias", "hubspot"]

# All helpdesk/chat tools, used for "also_uses" / "switched_from" / dropped reports.
HELPDESK_TECHS = TARGET_TECHS + [
    "freshdesk",
    "helpscout",
    "kustomer",
    "gladly",
    "reamaze",
    "tidio",
    "livechat",
    "drift",
]

SIGNATURES = {
    # ---- the four tools we are tracking ----
    "zendesk": {
        "html": [
            r"static\.zdassets\.com",
            r"ekr\.zdassets\.com",
            r"zendesk\.com/embeddable_framework",
            r"v2\.zopim\.com",  # Zendesk Chat (legacy Zopim)
            r"(?<![a-z0-9-])(?!support\.)[a-z0-9-]+\.zendesk\.com/hc",  # own help centre
        ],
        "cname": [r"\.zendesk\.com\.?$", r"\.zdassets\.com\.?$"],
    },
    "intercom": {
        "html": [
            r"widget\.intercom\.io",
            r"js\.intercomcdn\.com",
            r"intercomSettings",
            r"[a-z0-9-]+\.intercom\.help",
        ],
        "cname": [r"intercom\.help\.?$", r"intercom\.io\.?$"],
    },
    "gorgias": {
        "html": [
            r"config\.gorgias\.chat",
            r"[a-z0-9-]*\.?gorgias\.chat",
            r"gorgias\.io/",
            r"[a-z0-9-]+\.gorgias\.help",
        ],
        "cname": [r"gorgias\.(help|chat|io)\.?$"],
    },
    "hubspot": {
        "html": [
            r"js\.usemessages\.com",  # HubSpot live chat / Conversations
            r"js(-eu1)?\.hs-scripts\.com",
            r"js(-eu1)?\.hsforms\.net",
            r"js(-eu1)?\.hs-analytics\.net",
            r"js(-eu1)?\.hs-banner\.com",
            r"js\.hubspot\.com",
            r"hbspt\.forms\.create",
        ],
        "cname": [r"hs-sites(-eu1)?\.com\.?$", r"hubspot\.(net|com)\.?$"],
    },
    # ---- competitors: tracked so we can tell when someone SWITCHED ----
    "freshdesk": {
        "html": [
            r"widget\.freshworks\.com",
            r"wchat\.freshchat\.com",
            r"[a-z0-9-]+\.freshdesk\.com",
        ],
        "cname": [r"freshdesk\.com\.?$"],
    },
    "helpscout": {
        "html": [r"beacon-v2\.helpscout\.net"],
        "cname": [r"helpscoutdocs\.com\.?$"],
    },
    "kustomer": {"html": [r"cdn\.kustomerapp\.com"], "cname": [r"kustomer"]},
    "gladly": {"html": [r"cdn\.gladly\.com"], "cname": [r"gladly\.(com|qa)\.?$"]},
    "reamaze": {"html": [r"cdn\.reamaze\.com"], "cname": [r"reamaze\.com\.?$"]},
    "tidio": {"html": [r"code\.tidio\.co"], "cname": []},
    "livechat": {"html": [r"cdn\.livechatinc\.com"], "cname": []},
    "drift": {"html": [r"js\.driftt\.com"], "cname": []},
    # ---- context ----
    "shopify": {
        "html": [r"cdn\.shopify\.com", r"Shopify\.theme"],
        "cname": [r"myshopify\.com\.?$", r"shops\.myshopify\.com"],
    },
}

# Vendors' own sites always "use" their product; skip them.
VENDOR_DOMAINS = {
    "zendesk.com",
    "intercom.com",
    "gorgias.com",
    "hubspot.com",
    "freshworks.com",
    "freshdesk.com",
    "helpscout.com",
    "kustomer.com",
    "gladly.com",
    "reamaze.com",
    "tidio.com",
    "livechat.com",
    "drift.com",
    "shopify.com",
}

HELP_SUBDOMAINS = ["support", "help", "helpcenter", "help-center", "kb", "faq", "care"]

GTM_ID_RE = re.compile(r"GTM-[A-Z0-9]{4,10}")

_COMPILED = {
    tech: {
        "html": [re.compile(p, re.I) for p in rules["html"]],
        "cname": [re.compile(p, re.I) for p in rules["cname"]],
    }
    for tech, rules in SIGNATURES.items()
}


def match_html(text: str) -> dict:
    """Return {tech: evidence_pattern} for every tech found in the text."""
    found = {}
    for tech, rules in _COMPILED.items():
        for rx in rules["html"]:
            m = rx.search(text)
            if m:
                found[tech] = m.group(0)[:80]
                break
    return found


def match_cname(target: str) -> dict:
    found = {}
    for tech, rules in _COMPILED.items():
        for rx in rules["cname"]:
            if rx.search(target):
                found[tech] = target.rstrip(".")
                break
    return found
