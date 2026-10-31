"""Detection rules. Add a case here for every new signature (see docs/detection.md)."""

import pytest

from stackradar.signatures import match_cname, match_html

ZENDESK = '<script id="ze-snippet" src="https://static.zdassets.com/ekr/snippet.js?key=a"></script>'
INTERCOM = (
    "<script>window.intercomSettings={app_id:'x'};</script>"
    "<script src='https://widget.intercom.io/widget/x'></script>"
)
GORGIAS = (
    '<script src="https://config.gorgias.chat/bundle-loader/01H"></script>'
    '<script src="https://cdn.shopify.com/s/files/x.js"></script>'
)
HUBSPOT = '<script id="hs-script-loader" src="//js.hs-scripts.com/1234.js"></script>'


@pytest.mark.parametrize(
    "html,tech",
    [
        (ZENDESK, "zendesk"),
        (INTERCOM, "intercom"),
        (GORGIAS, "gorgias"),
        (GORGIAS, "shopify"),
        (HUBSPOT, "hubspot"),
        ('<a href="https://acme.zendesk.com/hc/en-us">Help</a>', "zendesk"),
        ('<script src="https://js.usemessages.com/conversations-embed.js"></script>', "hubspot"),
        ('<script src="https://code.tidio.co/abc.js"></script>', "tidio"),
    ],
)
def test_detects(html, tech):
    assert tech in match_html(html)


def test_plain_mentions_are_ignored():
    text = (
        "<p>We compared Zendesk, Intercom, Gorgias and HubSpot. "
        "See https://support.zendesk.com/hc/en-us</p>"
    )
    assert match_html(text) == {}


def test_gtm_escaped_urls():
    js = r'"vtp_html":"<script src=\"https:\/\/widget.intercom.io\/widget\/x\"'
    assert "intercom" in match_html(js)


@pytest.mark.parametrize(
    "target,tech",
    [
        ("acme.zendesk.com.", "zendesk"),
        ("custom.intercom.help.", "intercom"),
        ("1234.group34.sites.hs-sites.com.", "hubspot"),
        ("acme.freshdesk.com.", "freshdesk"),
    ],
)
def test_cname(target, tech):
    assert tech in match_cname(target)


def test_unrelated_cname():
    assert match_cname("acme.netlify.app.") == {}
