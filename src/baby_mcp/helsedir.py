"""Client for Helsedirektoratet's open content API (NLOD licence).

Structure (verified against the QA gateway 2026-10-07):
  retningslinje -> links[rel=barn,type=kapittel] -> kapittel
  kapittel      -> links[rel=barn,type=anbefaling] -> anbefaling (text, data.styrke, data.praktisk)

The subscription key from the "Alle utviklere" product only works on the QA
gateway. Set HELSEDIR_API_BASE to the production URL once a production
product is granted; every result carries the environment so QA is never
presented as production.
"""
import asyncio
import os
import re
import time

import httpx

from .pages import html_to_text
from .sources import source_name

QA_BASE = "https://api-qa.helsedirektoratet.no/innhold"
KEY_HEADER = "Ocp-Apim-Subscription-Key"
CACHE_TTL = 3600  # dev/test product has call limits; guidelines change rarely
MAX_RECS = 25
ID_RE = re.compile(r"^[0-9a-z][0-9a-z-]{8,80}$")

_cache: dict[str, tuple[float, object]] = {}


class MissingApiKey(RuntimeError):
    pass


def base_url() -> str:
    base = os.environ.get("HELSEDIR_API_BASE", QA_BASE).rstrip("/")
    if source_name(base) != "Helsedirektoratet":
        raise ValueError(f"HELSEDIR_API_BASE må være en helsedirektoratet.no-adresse: {base}")
    return base


def environment() -> str:
    return "qa" if "api-qa." in base_url() else "prod"


def env_note() -> str | None:
    if environment() == "qa":
        return (
            "Data fra Helsedirektoratets QA-miljø (test). Ikke bekreftet identisk med produksjon; "
            "kontroller mot kilde-URL før bruk."
        )
    return None


def _headers() -> dict:
    key = os.environ.get("HELSEDIR_API_KEY")
    if not key:
        raise MissingApiKey(
            "HELSEDIR_API_KEY mangler. Hent gratis nøkkel på https://utvikler.helsedirektoratet.no"
        )
    return {KEY_HEADER: key, "Accept": "application/json"}


def _check_id(content_id: str) -> str:
    if not ID_RE.match(content_id):
        raise ValueError(f"Ugyldig id: {content_id!r}")
    return content_id


async def _get_json(path: str, params: dict | None, client: httpx.AsyncClient):
    cache_key = f"{base_url()}{path}?{sorted((params or {}).items())}"
    hit = _cache.get(cache_key)
    if hit and time.time() - hit[0] < CACHE_TTL:
        return hit[1]
    resp = await client.get(base_url() + path, params=params, headers=_headers())
    resp.raise_for_status()
    data = resp.json()
    _cache[cache_key] = (time.time(), data)
    return data


def _one(data):
    return data[0] if isinstance(data, list) else data


def _safe_url(url: str | None) -> str | None:
    # Some QA records point at non-production hosts; never surface those.
    return url if url and source_name(url) else None


def _link_id(href: str) -> str:
    return href.rstrip("/").rsplit("/", 1)[-1]


def summarize(item: dict) -> dict:
    return {
        "id": item["id"],
        "title": item["tittel"],
        "topics": item.get("tema") or [],
        "updated": (item.get("sistOppdatert") or "")[:10],
        "url": _safe_url(item.get("url")),
    }


async def search(query: str, limit: int = 10, client: httpx.AsyncClient | None = None) -> list[dict]:
    """Rank current guidelines by how many query words hit title/topics/intro."""
    terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]
    own = client is None
    client = client or httpx.AsyncClient(timeout=60)
    try:
        items = await _get_json("/innhold", {"infoTyper": "retningslinje"}, client)
    finally:
        if own:
            await client.aclose()
    scored = []
    for it in items:
        if it.get("status") != "Gjeldende":
            continue
        hay = " ".join([it["tittel"], " ".join(it.get("tema") or []), it.get("intro") or ""]).lower()
        score = sum(t in hay for t in terms)
        if score:
            scored.append((score, summarize(it)))
    scored.sort(key=lambda s: -s[0])
    return [s for _, s in scored[:limit]]


async def outline(guideline_id: str, client: httpx.AsyncClient | None = None) -> dict:
    gid = _check_id(guideline_id)
    own = client is None
    client = client or httpx.AsyncClient(timeout=60)
    try:
        g = _one(await _get_json(f"/retningslinjer/{gid}", None, client))
    finally:
        if own:
            await client.aclose()
    chapters = [
        {"chapter_id": _link_id(l["href"]), "title": l["tittel"]}
        for l in g.get("links", [])
        if l.get("rel") == "barn" and l.get("type") == "kapittel"
    ]
    return {**summarize(g), "chapters": chapters}


async def chapter(chapter_id: str, client: httpx.AsyncClient | None = None) -> dict:
    cid = _check_id(chapter_id)
    own = client is None
    client = client or httpx.AsyncClient(timeout=60)
    try:
        ch = _one(await _get_json(f"/kapitler/{cid}", None, client))
        rec_ids = [
            _link_id(l["href"])
            for l in ch.get("links", [])
            if l.get("rel") == "barn" and l.get("type") == "anbefaling"
        ][:MAX_RECS]
        recs = await asyncio.gather(*[_get_json(f"/anbefalinger/{r}", None, client) for r in rec_ids])
    finally:
        if own:
            await client.aclose()
    out = []
    for r in map(_one, recs):
        if r.get("status") != "Gjeldende":
            continue
        data = r.get("data") or {}
        out.append({
            "recommendation": r["tittel"],
            "strength": data.get("styrke"),
            "text": html_to_text(r.get("tekst") or "")[1],
            "practical": html_to_text(data.get("praktisk") or "")[1],
            "updated": (r.get("sistOppdatert") or "")[:10],
            "url": _safe_url(r.get("url")),
        })
    return {**summarize(ch), "recommendations": out}
