"""Source allowlist and curated official pages.

Hard rule: only Norwegian health authorities. Anything else is refused,
so magazines, blogs and forums can never reach an answer.
"""
import re
from urllib.parse import urlparse

ALLOWED_HOSTS = {
    "helsedirektoratet.no": "Helsedirektoratet",
    "fhi.no": "Folkehelseinstituttet (FHI)",
    "helsenorge.no": "Helsenorge",
}

DISCLAIMER = (
    "Generell informasjon fra offentlige helsemyndigheter, ikke individuell "
    "medisinsk rådgivning. Ved bekymring: kontakt helsestasjon, fastlege eller "
    "legevakt (116 117). Ved akutt fare: ring 113."
)


def source_name(url: str) -> str | None:
    """Return the authority's name if url is on an allowed host, else None."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return None
    host = parsed.hostname.lower()
    for domain, name in ALLOWED_HOSTS.items():
        if host == domain or host.endswith("." + domain):
            return name
    return None


def rank_pages(query: str, limit: int = 8) -> list[tuple[str, dict]]:
    """Rank curated pages: a title hit counts 3, a keyword hit 2; ties keep catalogue order."""
    terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]
    scored = []
    for order, (key, page) in enumerate(CURATED_PAGES.items()):
        title = page["title"].lower()
        kws = [k.lower() for k in page["keywords"]]
        score = sum(3 * (t in title) + 2 * any(t in k for k in kws) for t in terms)
        if score:
            scored.append((-score, order, key, page))
    scored.sort(key=lambda r: r[:2])
    return [(key, page) for _, _, key, page in scored[:limit]]


# Starting points found via search; verified reachable by tests/verify_urls.py.
# Add topics here rather than letting callers pass arbitrary URLs.
CURATED_PAGES: dict[str, dict] = {
    "sovn-krybbedod": {
        "title": "Krybbedød (SIDS) og trygg søvn",
        "keywords": ["søvn", "krybbedød", "sids", "sove", "samsoving", "rygg"],
        "url": "https://www.helsenorge.no/barn/krybbedod/",
    },
    "sovn-0-2": {
        "title": "Søvn hos barn 0–2 år",
        "keywords": ["søvn", "sove", "natt", "døgnrytme"],
        "url": "https://www.helsenorge.no/barn/sovn-hos-barn/",
    },
    "nyfodt-omsorg": {
        "title": "Omsorgen for det nyfødte barnet og kjennetegn på trivsel",
        "keywords": ["nyfødt", "trivsel", "omsorg", "første uker"],
        "url": "https://www.helsenorge.no/barn/omsorgen-for-det-nyfodte-barnet/",
    },
    "barn-0-2": {
        "title": "Informasjon om barn fra 0 til 2 år",
        "keywords": ["baby", "spedbarn", "0-2 år", "oversikt"],
        "url": "https://www.helsenorge.no/barn/0-2-ar/",
    },
    "vaksiner-oversikt": {
        "title": "Barnevaksinasjonsprogrammet (FHI)",
        "keywords": ["vaksine", "vaksinasjon", "barnevaksinasjonsprogram"],
        "url": "https://www.fhi.no/va/vaksinasjonshandboka/vaksinasjon/barnevaksinasjonsprogrammet/",
    },
    "vaksiner-tidspunkt": {
        "title": "Når får barnet tilbud om de ulike vaksinene? (FHI)",
        "keywords": ["vaksine", "tidspunkt", "6 uker", "3 måneder", "15 måneder", "rotavirus"],
        "url": "https://www.fhi.no/va/barnevaksinasjonsprogrammet/nar-far-barnet-ditt-tilbud-om-de-ulike-vaksinene/",
    },
    "vaksiner-gravide": {
        "title": "Vaksinasjon av gravide og ammende (FHI)",
        "keywords": ["gravid", "ammende", "vaksine", "kikhoste", "influensa"],
        "url": "https://fhi.no/va/vaksinasjonshandboka/vaksinasjon-i-ulike-livsfaser/vaksinasjon-av-gravide-og-ammende/",
    },

    # --- Amming og spedbarnsernæring ---
    "amming": {
        "title": "Amming (Helsenorge)",
        "keywords": ["amming", "amme", "morsmelk", "die"],
        "url": "https://www.helsenorge.no/spedbarn/spedbarnsmat-og-amming/alt-om-spedbarnsmat/amming/",
    },
    "amming-morsmelk": {
        "title": "Amming og morsmelk (Helsenorge)",
        "keywords": ["amming", "morsmelk", "hvor lenge", "anbefaling"],
        "url": "https://www.helsenorge.no/spedbarn/spedbarnsmat-og-amming/amming-og-morsmelk",
    },
    "ammeteknikk": {
        "title": "Ammeteknikk (Helsenorge)",
        "keywords": ["ammeteknikk", "sugetak", "ammestilling", "sår brystknopp"],
        "url": "https://www.helsenorge.no/spedbarn/spedbarnsmat-og-amming/alt-om-spedbarnsmat/amming/ammeteknikk/",
    },
    "melkeproduksjon": {
        "title": "Melkeproduksjon (Helsenorge)",
        "keywords": ["melkeproduksjon", "melk", "lite melk", "melkemengde"],
        "url": "https://www.helsenorge.no/spedbarn/spedbarnsmat-og-amming/alt-om-spedbarnsmat/amming/melkeproduksjon/",
    },
    "amming-legemidler": {
        "title": "Amming og legemidler (Helsenorge)",
        "keywords": ["amming", "legemidler", "medisiner", "paracet", "ibuprofen"],
        "url": "https://www.helsenorge.no/spedbarn/spedbarnsmat-og-amming/amming-og-legemidler/",
    },
    "fast-fode": {
        "title": "Fast føde / tilleggsmat (Helsenorge)",
        "keywords": ["fast føde", "tilleggsmat", "grøt", "smaking", "seks måneder", "introduksjon av mat"],
        "url": "https://helsenorge.no/spedbarn/spedbarnsmat-og-amming/alt-om-spedbarnsmat/fast-fode",
    },
    "spedbarnsernaering-anbefalinger": {
        "title": "Anbefalinger for morsmelk, morsmelkerstatning og introduksjon av mat (Helsedirektoratet)",
        "keywords": ["morsmelkerstatning", "d-vitamin", "introduksjon av mat", "ernæring", "spedbarnsernæring"],
        "url": "https://www.helsedirektoratet.no/retningslinjer/spedbarnsernaering/anbefalinger-for-morsmelk-morsmelkerstatning-og-introduksjon-av-mat",
    },
    # --- Sykdom og symptomer hos barn ---
    "feber": {
        "title": "Feber hos barn (Helsenorge)",
        "keywords": ["feber", "temperatur", "paracetamol", "feberkramper", "syk"],
        "url": "https://www.helsenorge.no/sykdom/barn/feber-hos-barn/",
    },
    "diare": {
        "title": "Diaré hos barn (Helsenorge)",
        "keywords": ["diare", "diaré", "oppkast", "mageinfluensa", "dehydrering"],
        "url": "https://www.helsenorge.no/sykdom/mage-og-tarm/diare-hos-barn/",
    },
    "utslett": {
        "title": "Utslett hos barn (Helsenorge)",
        "keywords": ["utslett", "hud", "blodutredelser", "prikker"],
        "url": "https://helsenorge.no/sykdom/hud-og-har/utslett-hos-barn",
    },
    "barn-medisiner": {
        "title": "Barn og medisiner (Helsenorge)",
        "keywords": ["medisin", "dosering", "paracetamol", "legemidler barn"],
        "url": "https://www.helsenorge.no/medisiner/barn-og-medisiner/",
    },
    "hjernehinnebetennelse": {
        "title": "Råd ved mistanke om smittsom hjernehinnebetennelse (FHI)",
        "keywords": ["hjernehinnebetennelse", "meningitt", "nakkestiv", "alvorlig sykdom"],
        "url": "https://www.fhi.no/ss/hjernehinnebetennelse/informasjon-og-rad/",
    },
    # --- Etter fødsel og nyfødt ---
    "etter-fodsel": {
        "title": "Etter fødsel (Helsenorge)",
        "keywords": ["etter fødsel", "barsel", "barseltid", "oppfølging"],
        "url": "https://www.helsenorge.no/etter-fodsel/",
    },
    "kroppen-etter-fodsel": {
        "title": "Kroppen og den første tiden etter fødsel (Helsenorge)",
        "keywords": ["barsel", "kropp", "blødning", "etter fødsel", "keisersnitt"],
        "url": "https://www.helsenorge.no/etter-fodsel/kroppen-og-den-forste-tiden-etter-fodsel",
    },
    "gulsott": {
        "title": "Gulsott hos nyfødte (Helsenorge)",
        "keywords": ["gulsott", "gul", "nyfødt", "bilirubin"],
        "url": "https://www.helsenorge.no/sykdom/barn/gulsott-hos-nyfodte/",
    },
    "gruppe-b-strep": {
        "title": "Gruppe B streptokokkinfeksjon (Helsenorge)",
        "keywords": ["gruppe b", "streptokokk", "nyfødt infeksjon", "gbs"],
        "url": "https://www.helsenorge.no/sykdom/barn/gruppe-b-streptokokkinfeksjon/",
    },
    # --- Helsestasjon ---
    "helsestasjon-0-5": {
        "title": "Helsestasjon 0–5 år (Helsedirektoratet)",
        "keywords": ["helsestasjon", "konsultasjon", "hjemmebesøk", "helsesykepleier"],
        "url": "https://www.helsedirektoratet.no/retningslinjer/helsestasjons-og-skolehelsetjenesten/helsestasjon-05-ar",
    },
    "veiing-maling": {
        "title": "Veiing og måling på helsestasjonen (Helsedirektoratet)",
        "keywords": ["vekt", "vekst", "veiing", "måling", "vekstkurve", "hodeomkrets"],
        "url": "https://www.helsedirektoratet.no/retningslinjer/helsestasjons-og-skolehelsetjenesten/helsestasjon-05-ar/veiing-og-maling",
    },
    # --- Graviditet ---
    "svangerskapsomsorg-konsultasjoner": {
        "title": "Konsultasjoner i svangerskapsomsorgen (Helsedirektoratet)",
        "keywords": ["svangerskapskontroll", "jordmor", "fastlege", "ultralyd", "nipt", "konsultasjon"],
        "url": "https://www.helsedirektoratet.no/retningslinjer/svangerskapsomsorgen/konsultasjoner-i-svangerskapsomsorgen",
    },
    "gravid-vegetar": {
        "title": "Vegetarkost for gravide (Helsenorge)",
        "keywords": ["gravid", "vegetar", "vegan", "kosthold", "tilskudd"],
        "url": "https://www.helsenorge.no/kosthold-og-ernaring/vegetarisk-kosthold/vegetarkost-for-gravide/",
    },
    "gravid-halsbrann": {
        "title": "Sure oppstøt og halsbrann hos gravide (Helsenorge)",
        "keywords": ["gravid", "halsbrann", "sure oppstøt", "svangerskapsplager"],
        "url": "https://www.helsenorge.no/sykdom/svangerskap/halsbrann-og-sure-oppstot-hos-gravide/",
    },
    "preeklampsi": {
        "title": "Svangerskapsforgiftning (preeklampsi) (Helsenorge)",
        "keywords": ["preeklampsi", "svangerskapsforgiftning", "blodtrykk", "gravid"],
        "url": "https://www.helsenorge.no/sykdom/svangerskap/svangerskapsforgiftning",
    },
    # Only found in English on the authority sites; lang flag is surfaced to the caller.
    "gravid-alkohol": {
        "title": "Graviditet og alkohol (Helsenorge, English)",
        "lang": "en",
        "keywords": ["gravid", "alkohol", "alcohol", "pregnancy", "fosteralkohol"],
        "url": "https://www.helsenorge.no/en/pregnancy-and-maternity-care-in-norway/alcohol-and-pregnancy/",
    },
    "gravid-kosthold": {
        "title": "Kosthold for gravide (Helsenorge, English)",
        "lang": "en",
        "keywords": ["gravid", "kosthold", "diet", "jod", "næringsstoffer", "pregnancy"],
        "url": "https://www.helsenorge.no/en/pregnancy-and-maternity-care-in-norway/dietary-advice-for-pregnant-women/",
    },
    "gravid-unngaa": {
        "title": "Mat og drikke gravide bør unngå (Helsenorge, English)",
        "lang": "en",
        "keywords": ["gravid", "unngå", "listeria", "fisk", "koffein", "food to avoid", "pregnancy"],
        "url": "https://www.helsenorge.no/en/pregnancy-and-maternity-care-in-norway/food-and-drink-to-avoid-during-pregnancy/",
    },
    "gravid-legemidler": {
        "title": "Graviditet og legemidler (Helsenorge, English)",
        "lang": "en",
        "keywords": ["gravid", "legemidler", "medisiner", "ibuprofen", "paracetamol", "pregnancy", "medications"],
        "url": "https://www.helsenorge.no/en/medisiner/pregnancy-and-medications/",
    },
}
