# baby-mcp

MCP-server som kun svarer fra norske helsemyndigheter (Helsedirektoratet, FHI, Helsenorge) om
graviditet, spedbarn og første leveår. Ingen magasiner, blogger eller fora: domene-allowlist
i `src/baby_mcp/sources.py` håndheves også på redirects.

## Verktøy
- `list_topics`, `find_official_pages` – kuraterte offisielle sider (søvn/SIDS, vaksiner, nyfødt)
- `read_official_page(url)` – henter tekst fra godkjente domener, avviser alt annet
- `search_guidelines`, `get_guideline` – Helsedirektoratets åpne API (krever `HELSEDIR_API_KEY`)

Alle svar inneholder kilde-URL og en standard ansvarsfraskrivelse.

## Kjøring
    uv sync --extra dev && uv run pytest
    uv run python tests/verify_urls.py      # sjekker at kuraterte URL-er lever
    claude mcp add baby-helse -e HELSEDIR_API_KEY=... -- uv --directory $PWD run baby-mcp

## Helsedirektoratet-API (verifisert 2026-10-07)
- Struktur: retningslinje -> kapittel -> anbefalinger (tekst, styrke, praktiske råd).
- Verktøy: `search_guidelines` -> `get_guideline` (kapittelliste) -> `get_guideline_chapter`.
- Nøkkelen fra produktet «Alle utviklere» virker KUN mot QA (`api-qa.helsedirektoratet.no`), som er standard.
  Alle svar har `environment: "qa"` og en advarsel. For produksjon: be om et produksjonsprodukt og sett
  `HELSEDIR_API_BASE=https://api.helsedirektoratet.no/innhold`. Produktet har kallbegrensning; svar caches i 1 time.
- Vilkår (NLOD): oppgi Helsedirektoratet som kilde, ikke endre meningsinnhold.
