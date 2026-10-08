import asyncio
import re
from pathlib import Path
import logging
from src.helpers.domain_helper import find_domain
import os

import yaml
from playwright.async_api import async_playwright

OUT = "probe_out/html"

logger = logging.getLogger(__name__)

async def probe(browser, url):
    # name, url = company["name"], company["url"]
    # slug = re.sub(r"\W+", "_", name).lower()
    name = find_domain(url)
    context = await browser.new_context()
    page = await context.new_page()
    logger.info(f"\n=== {name} ===")

    # 1) Raw HTML: a plain HTTP request, JavaScript never runs.
    try:
        raw = await context.request.get(url, timeout=30_000)
        raw_text = await raw.text()
        logger.info(f"raw:      HTTP {raw.status}, {len(raw_text)} chars")
    except Exception as e:
        logger.error(f"raw:      ERROR {type(e).__name__}: {str(e).splitlines()[0]}")

    # 2) Rendered HTML: real browser, wait until the network goes quiet.
    try:
        resp = await page.goto(url, wait_until="networkidle", timeout=45_000)
        html = await page.content()
        os.makedirs(OUT, exist_ok=True)
        html_file_path = f"{OUT}/{name}.html"
        Path(html_file_path).write_text(html, encoding="utf-8")
        status = resp.status if resp else "no response"
        logger.info(f"rendered: HTTP {status}, {len(html)} chars, title={await page.title()!r}")
        return html_file_path
    except Exception as e:
        logger.error(f"rendered: ERROR {type(e).__name__}: {str(e).splitlines()[0]}")
    finally:
        await context.close()


async def run(url):
    try:
        # companies = yaml.safe_load(Path("companies.yaml").read_text(encoding="utf-8"))
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            # for company in companies:  # one at a time so the output is easy to read
            # await probe(browser, company)
            html_file_path = await probe(browser, url)
            await browser.close()
        return html_file_path
    except Exception as e:
        logger.error(f"Error while running probe: {e}")
        return None


# asyncio.run(run())