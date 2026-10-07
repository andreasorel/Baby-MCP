"""Manual check (network): every curated URL must return 200 and stay on the allowlist."""
import asyncio

from baby_mcp import pages
from baby_mcp.sources import CURATED_PAGES


async def main():
    for key, p in CURATED_PAGES.items():
        try:
            r = await pages.fetch_page(p["url"])
            print("OK  ", key, len(r["text"]), r["title"][:60])
        except Exception as e:
            print("FAIL", key, p["url"], e)


asyncio.run(main())
