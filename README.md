# baby-mcp

[![CI](https://github.com/andreasorel/Baby-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/andreasorel/Baby-MCP/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

MCP-server som lar AI-assistenter (Claude m.fl.) svare på spørsmål om **graviditet, spedbarn og første leveår**
basert utelukkende på **norske helsemyndigheter**: [Helsedirektoratet](https://www.helsedirektoratet.no),
[Folkehelseinstituttet](https://www.fhi.no) og [Helsenorge](https://www.helsenorge.no).
Ingen magasiner, blogger eller fora.

> **Viktig:** Dette er generell informasjon fra offentlige kilder, ikke individuell medisinsk rådgivning.
> Ved bekymring, kontakt helsestasjon, fastlege eller legevakt (116 117). Ved akutt fare, ring 113.
> Prosjektet er uavhengig og er ikke utviklet av eller godkjent av noen helsemyndighet.

## Hva den gjør
- Henter **ferskt innhold direkte fra kilden** hver gang. Ingen lokal kopi som kan bli utdatert.
- Avviser alle andre domener enn de tre over, også ved omdirigering.
- Gir alltid kilde-URL, og instruerer modellen til å svare «vet ikke» når kildene ikke dekker spørsmålet.
- 33 kuraterte sider: søvn og krybbedød, amming, spedbarnsmat, vaksiner, feber og sykdom, nyfødt og barsel, helsestasjon, graviditet.
- Helsedirektoratets nasjonale faglige retningslinjer (svangerskap, barsel, spedbarnsernæring m.fl.) via deres åpne API.

## Installasjon

Du trenger [uv](https://docs.astral.sh/uv/getting-started/installation/) (inkluderer `uvx`).

### Claude Code
```bash
claude mcp add --scope user baby-helse -- uvx --from git+https://github.com/andreasorel/Baby-MCP baby-mcp
```

### Claude Desktop
Legg til i `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "baby-helse": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/andreasorel/Baby-MCP", "baby-mcp"]
    }
  }
}
```

Start Claude på nytt, og spør for eksempel: *«Når bør jeg kontakte lege hvis babyen min har feber?»*

### Valgfritt: Helsedirektoratets retningslinjer (API-nøkkel)
Sidene fra Helsenorge, FHI og Helsedirektoratet virker uten nøkkel. Verktøyene `search_guidelines`,
`get_guideline` og `get_guideline_chapter` krever en gratis nøkkel:

1. Opprett konto og abonner på **Helsedirektoratets Innholdstjenester** på [utvikler.helsedirektoratet.no](https://utvikler.helsedirektoratet.no).
2. Gi serveren nøkkelen som miljøvariabel:
   ```bash
   claude mcp add --scope user baby-helse -e HELSEDIR_API_KEY=din_nøkkel -- uvx --from git+https://github.com/andreasorel/Baby-MCP baby-mcp
   ```
   (Claude Desktop: legg til `"env": { "HELSEDIR_API_KEY": "din_nøkkel" }` i konfigurasjonen over.)

> **Om QA-miljøet:** Standardproduktet «Alle utviklere» gir bare tilgang til Helsedirektoratets **QA-miljø**
> (`api-qa.helsedirektoratet.no`), og er ment for utvikling og test. Serveren bruker det som standard, og alle
> svar fra API-et er merket `environment: "qa"` med en advarsel. Har du fått produksjonstilgang, sett
> `HELSEDIR_API_BASE=https://api.helsedirektoratet.no/innhold`.

## Verktøy
| Verktøy | Beskrivelse |
|---|---|
| `list_topics` | Alle kuraterte temaer og sider |
| `find_official_pages` | Finn relevante offisielle sider for et spørsmål |
| `read_official_page` | Les en side fra godkjent domene (andre avvises). Returnerer også godkjente lenker for å navigere videre |
| `search_guidelines` | Søk i Helsedirektoratets nasjonale retningslinjer *(krever nøkkel)* |
| `get_guideline` | Kapitler i en retningslinje *(krever nøkkel)* |
| `get_guideline_chapter` | Anbefalinger med styrkegrad og praktiske råd *(krever nøkkel)* |

## Begrensninger
- Innholdet er ikke faglig kvalitetssikret av dette prosjektet. Det formidles slik kildene presenterer det.
- Noen graviditetssider (alkohol, kosthold, legemidler) finnes bare på engelsk hos kilden og er merket `lang: "en"`.
- Søket er enkel tekstmatching og forstår ikke synonymer eller bøyninger.
- Sider kan endre adresse hos kilden. Kjør `uv run python tests/verify_urls.py` for å sjekke at alle kuraterte URL-er lever.

## Utvikling
```bash
git clone https://github.com/andreasorel/Baby-MCP && cd Baby-MCP
uv sync --extra dev
uv run pytest
cp .env.example .env   # valgfritt: legg inn HELSEDIR_API_KEY
```
Nye temaer legges til i `src/baby_mcp/sources.py` (`CURATED_PAGES`). Kun URL-er på de tre godkjente domenene.
Bidrag er velkomne som pull requests.

## Kilder og lisens
Koden er lisensiert under [MIT](LICENSE). Innhold fra Helsedirektoratet hentes under
[Norsk lisens for offentlige data (NLOD)](https://data.norge.no/nlod/no/2.0): Helsedirektoratet oppgis som kilde,
og det faglige innholdet endres ikke. Innhold fra FHI og Helsenorge hentes live og lagres ikke i dette repoet.
Ta hensyn til kildenes egne vilkår hvis du bruker verktøyet i stor skala.
