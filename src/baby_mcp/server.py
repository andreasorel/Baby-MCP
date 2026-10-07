"""MCP server exposing Norwegian health-authority guidance on pregnancy and infants."""
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from . import helsedir, pages
from .sources import CURATED_PAGES, DISCLAIMER, rank_pages

# Keep the API key out of Claude Code's config: read it from the project's .env.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

mcp = FastMCP(
    "baby-helse",
    instructions=(
        "Svar KUN basert på tekst hentet via disse verktøyene (Helsedirektoratet, FHI, Helsenorge). "
        "Oppgi alltid kilde-URL. Hvis verktøyene ikke dekker spørsmålet, si 'vet ikke' og "
        "henvis til helsestasjon/fastlege. Ikke fyll inn fra egen kunnskap eller andre kilder."
    ),
)


def _with_disclaimer(payload: dict) -> dict:
    payload["disclaimer"] = DISCLAIMER
    return payload


@mcp.tool()
def list_topics() -> dict:
    """List curated official pages (søvn, vaksiner, nyfødt, gravide) with keywords."""
    return _with_disclaimer(
        {k: {"title": v["title"], "lang": v.get("lang", "no"), "keywords": v["keywords"], "url": v["url"]} for k, v in CURATED_PAGES.items()}
    )


@mcp.tool()
def find_official_pages(query: str) -> dict:
    """Find curated official pages whose keywords/title match the query (Norwegian terms work best)."""
    hits = [
        {"topic": key, "title": p["title"], "lang": p.get("lang", "no"), "url": p["url"]}
        for key, p in rank_pages(query)
    ]
    return _with_disclaimer({"matches": hits})


@mcp.tool()
async def read_official_page(url: str) -> dict:
    """Read a page from helsedirektoratet.no, fhi.no or helsenorge.no. Other domains are refused."""
    try:
        return _with_disclaimer(await pages.fetch_page(url))
    except pages.SourceNotAllowed as e:
        return {"error": str(e)}


def _hd(payload: dict) -> dict:
    payload["source"] = "Helsedirektoratet"
    payload["environment"] = helsedir.environment()
    if note := helsedir.env_note():
        payload["environment_warning"] = note
    return _with_disclaimer(payload)


@mcp.tool()
async def search_guidelines(query: str, limit: int = 10) -> dict:
    """Search Helsedirektoratet national guidelines (svangerskap, barsel, spedbarnsernæring, helsestasjon). Norwegian words work best."""
    try:
        return _hd({"results": await helsedir.search(query, limit)})
    except helsedir.MissingApiKey as e:
        return {"error": str(e)}


@mcp.tool()
async def get_guideline(guideline_id: str) -> dict:
    """Get a guideline's chapter list (use id from search_guidelines), then call get_guideline_chapter."""
    try:
        return _hd(await helsedir.outline(guideline_id))
    except (helsedir.MissingApiKey, ValueError) as e:
        return {"error": str(e)}


@mcp.tool()
async def get_guideline_chapter(chapter_id: str) -> dict:
    """Get the recommendations (with strength and practical advice) in one guideline chapter."""
    try:
        return _hd(await helsedir.chapter(chapter_id))
    except (helsedir.MissingApiKey, ValueError) as e:
        return {"error": str(e)}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
