"""Fetch and clean pages from allowlisted authority sites."""
from urllib.parse import urldefrag, urljoin

import httpx
from bs4 import BeautifulSoup

from .sources import source_name

USER_AGENT = "baby-mcp/0.1 (personal research tool; respects robots.txt)"
MAX_CHARS = 20_000
MAX_LINKS = 40


class SourceNotAllowed(ValueError):
    pass


def html_to_text(html: str) -> tuple[str, str]:
    """Return (title, main text). Prefers <main>/<article>, drops chrome."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()
    title = (soup.title.get_text(strip=True) if soup.title else "") or ""
    root = soup.find("main") or soup.find("article") or soup.body or soup
    lines = []
    for el in root.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = el.get_text(" ", strip=True)
        if not text:
            continue
        if el.name in ("h1", "h2", "h3", "h4"):
            lines.append("\n" + "#" * int(el.name[1]) + " " + text)
        elif el.name == "li":
            lines.append("- " + text)
        else:
            lines.append(text)
    return title, "\n".join(lines).strip()


def extract_links(html: str, base_url: str) -> list[dict]:
    """Allowlisted links inside the main content, so hub pages can be followed."""
    soup = BeautifulSoup(html, "html.parser")
    root = soup.find("main") or soup.find("article") or soup.body or soup
    seen, out = set(), []
    for a in root.find_all("a", href=True):
        url = urldefrag(urljoin(base_url, a["href"]))[0]
        text = a.get_text(" ", strip=True)
        if url in seen or not text or source_name(url) is None or url.rstrip("/") == base_url.rstrip("/"):
            continue
        seen.add(url)
        out.append({"text": text, "url": url})
    return out[:MAX_LINKS]


async def fetch_page(url: str, client: httpx.AsyncClient | None = None) -> dict:
    name = source_name(url)
    if name is None:
        raise SourceNotAllowed(
            f"{url} er ikke en godkjent kilde. Kun helsedirektoratet.no, fhi.no og helsenorge.no."
        )
    own = client is None
    client = client or httpx.AsyncClient(timeout=20, follow_redirects=True)
    try:
        resp = await client.get(url, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        # A redirect must not leave the allowlist.
        final = str(resp.url)
        if source_name(final) is None:
            raise SourceNotAllowed(f"Omdirigert til ikke-godkjent kilde: {final}")
        title, text = html_to_text(resp.text)
        links = extract_links(resp.text, final)
    finally:
        if own:
            await client.aclose()
    truncated = len(text) > MAX_CHARS
    return {
        "source": name,
        "url": final,
        "title": title,
        "text": text[:MAX_CHARS],
        "truncated": truncated,
        "links": links,
    }
