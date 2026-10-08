import asyncio
import re
from pathlib import Path

import yaml
from playwright.async_api import async_playwright

OUT = Path("probe_out")
OUT.mkdir(exist_ok=True)


async def probe(browser, company):
    name, url = company["name"], company["url"]
    slug = re.sub(r"\W+", "_", name).lower()
    context = await browser.new_context()
    page = await context.new_page()
    print(f"\n=== {name} ===")

    # 1) Raw HTML: a plain HTTP request, JavaScript never runs.
    try:
        raw = await context.request.get(url, timeout=30_000)
        raw_text = await raw.text()
        print(f"raw:      HTTP {raw.status}, {len(raw_text)} chars")
    except Exception as e:
        print(f"raw:      ERROR {type(e).__name__}: {str(e).splitlines()[0]}")

    # 2) Rendered HTML: real browser, wait until the network goes quiet.
    try:
        resp = await page.goto(url, wait_until="networkidle", timeout=45_000)
        html = await page.content()
        (OUT / f"{slug}.html").write_text(html, encoding="utf-8")
        status = resp.status if resp else "no response"
        print(f"rendered: HTTP {status}, {len(html)} chars, title={await page.title()!r}")
    except Exception as e:
        print(f"rendered: ERROR {type(e).__name__}: {str(e).splitlines()[0]}")
    finally:
        await context.close()


async def main():
    companies = yaml.safe_load(Path("companies.yaml").read_text(encoding="utf-8"))
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for company in companies:  # one at a time so the output is easy to read
            await probe(browser, company)
        await browser.close()


asyncio.run(main())