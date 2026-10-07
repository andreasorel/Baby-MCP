import pytest

from baby_mcp import pages
from baby_mcp.sources import source_name


@pytest.mark.parametrize("url,ok", [
    ("https://www.helsenorge.no/barn/sovn-hos-barn/", True),
    ("https://fhi.no/va/x", True),
    ("https://api.helsedirektoratet.no/x", True),
    ("http://www.fhi.no/x", False),
    ("https://fhi.no.evil.com/x", False),
    ("https://evilfhi.no/x", False),
    ("https://babyverden.no/x", False),
])
def test_allowlist(url, ok):
    assert (source_name(url) is not None) == ok


async def test_fetch_refuses_other_domains():
    with pytest.raises(pages.SourceNotAllowed):
        await pages.fetch_page("https://www.babyverden.no/")


def test_html_to_text():
    t, text = pages.html_to_text(
        "<html><title>T</title><body><nav>menu</nav><main><h1>H</h1><p>Hei</p><li>a</li></main></body></html>"
    )
    assert t == "T" and "menu" not in text and "# H" in text and "- a" in text


def test_helsedir_base_must_be_allowlisted(monkeypatch):
    from baby_mcp import helsedir
    monkeypatch.setenv("HELSEDIR_API_BASE", "https://evil.example.com/innhold")
    with pytest.raises(ValueError):
        helsedir.base_url()


def test_helsedir_id_validation():
    from baby_mcp import helsedir
    with pytest.raises(ValueError):
        helsedir._check_id("../../etc/passwd")
    assert helsedir._check_id("0006-0001-ca6b72d1-b7dc-4495-b0ab-c08c43266cf6")


def test_extract_links_keeps_only_allowlisted():
    html = ('<main><a href="/a/b">Intern</a><a href="https://babyverden.no/x">Magasin</a>'
            '<a href="https://www.fhi.no/z#top">FHI</a><a href="/a/b">Dup</a></main>')
    links = pages.extract_links(html, "https://www.helsenorge.no/a/")
    assert [l["text"] for l in links] == ["Intern", "FHI"]


@pytest.mark.parametrize("query,expected_first", [
    ("feber baby", "feber"),
    ("amming og legemidler", "amming-legemidler"),
    ("gulsott nyfødt", "gulsott"),
    ("alkohol gravid", "gravid-alkohol"),
    ("når får barnet vaksine", "vaksiner-tidspunkt"),
])
def test_rank_pages(query, expected_first):
    from baby_mcp.sources import rank_pages
    assert rank_pages(query)[0][0] == expected_first


def test_rank_pages_no_match():
    from baby_mcp.sources import rank_pages
    assert rank_pages("bleier") == []
