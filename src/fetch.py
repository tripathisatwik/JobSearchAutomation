import asyncio
import logging
from typing import Any, Dict, List
import requests

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)

async def _fetch_with_playwright(url: str, timeout: int = 30000) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            await page.wait_for_timeout(1000)
            return await page.content()
        finally:
            await browser.close()

def _fetch_with_requests(url: str, timeout: int = 15) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text

async def fetch_one(company: Dict[str, Any]) -> Dict[str, Any]:
    url = company.get("url")
    if not url:
        return {"html": "", "error": "Missing URL"}

    use_browser = company.get("render_js", False)

    if use_browser and PLAYWRIGHT_AVAILABLE:
        try:
            html = await _fetch_with_playwright(url)
            return {"html": html, "error": None}
        except Exception:
            # Fall back to requests if playwright browser launch fails
            pass

    try:
        html = await asyncio.to_thread(_fetch_with_requests, url)
        return {"html": html, "error": None}
    except Exception as e:
        if PLAYWRIGHT_AVAILABLE:
            try:
                html = await _fetch_with_playwright(url)
                return {"html": html, "error": None}
            except Exception as pe:
                return {"html": "", "error": f"Requests error: {e}; Playwright error: {pe}"}
        return {"html": "", "error": str(e)}

async def fetch_all(companies: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    tasks = [fetch_one(c) for c in companies]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return {c["name"]: res for c, res in zip(companies, results)}
