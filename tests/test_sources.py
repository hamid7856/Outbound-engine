from stackradar.sources import load_domains, normalize


def test_normalize():
    assert normalize("https://www.Acme.com/about?x=1") == "acme.com"
    assert normalize("acme.co.uk") == "acme.co.uk"
    assert normalize("not a domain") is None
    assert normalize("# comment") is None


def test_load_custom_and_imports(tmp_path):
    ddir = tmp_path / "domains"
    (ddir / "imports").mkdir(parents=True)
    (ddir / "custom.txt").write_text("# mine\nacme.com\nhttps://www.beta.io/x\n")
    (ddir / "imports" / "apollo.csv").write_text(
        "Company,Website\nAcme,acme.com\nGamma,https://gamma.co\n"
    )
    (ddir / "imports" / "bad.csv").write_text("Name,Notes\nx,y\n")
    got = load_domains(ddir, tmp_path / "data", tranco_top=0, refresh_tranco=False)
    assert got == {"acme.com": "custom", "beta.io": "custom", "gamma.co": "import:apollo"}
