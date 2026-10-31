"""Week-over-week diff rules (see docs/detection.md#change-rules)."""

from stackradar.state import read_csv, update_state

SRC = {"a.com": "custom", "b.com": "tranco", "c.com": "tranco"}


def pairs(rows, *keys):
    return [tuple(r[k] for k in keys) for r in rows]


def test_baseline_new_switch_and_drop(tmp_path):
    # week 1: baseline only
    new, drop = update_state(
        tmp_path,
        "2026-11-02",
        SRC,
        {"a.com": {"freshdesk": "html:x"}, "b.com": {"hubspot": "html:x"}, "c.com": None},
    )
    assert new == [] and drop == []

    # week 2: a.com adds gorgias; c.com is readable for the first time -> baseline only
    new, drop = update_state(
        tmp_path,
        "2026-11-09",
        SRC,
        {
            "a.com": {"gorgias": "html:g"},
            "b.com": {"hubspot": "html:x"},
            "c.com": {"zendesk": "html:z"},
        },
    )
    assert pairs(new, "domain", "tech", "switched_from") == [("a.com", "gorgias", "freshdesk")]
    assert drop == []  # one miss is not a drop

    # week 3: freshdesk still missing -> dropped; b.com unreadable -> untouched
    new, drop = update_state(
        tmp_path,
        "2026-11-16",
        SRC,
        {"a.com": {"gorgias": "html:g"}, "b.com": None, "c.com": {"zendesk": "html:z"}},
    )
    assert new == []
    assert pairs(drop, "domain", "tech", "now_uses") == [("a.com", "freshdesk", "gorgias")]

    # week 4: b.com back and adds intercom
    new, _ = update_state(
        tmp_path, "2026-11-23", SRC, {"b.com": {"hubspot": "html:x", "intercom": "html:i"}}
    )
    assert pairs(new, "domain", "tech", "also_uses") == [("b.com", "intercom", "hubspot")]

    domains = {r["domain"]: r for r in read_csv(tmp_path / "domains.csv")}
    assert domains["b.com"]["consecutive_failures"] == "0"
    assert domains["c.com"]["first_scanned"] == "2026-11-09"


def test_non_target_tech_is_not_reported_as_new(tmp_path):
    update_state(tmp_path, "2026-11-02", SRC, {"a.com": {}})
    new, _ = update_state(tmp_path, "2026-11-09", SRC, {"a.com": {"tidio": "html:t"}})
    assert new == []
