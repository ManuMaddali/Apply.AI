from __future__ import annotations

from typing import Optional


async def render_pdf_from_html(html: str, page_size: str = "A4") -> bytes:
    """
    Async HTML -> PDF rendering using Playwright Chromium.
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_content(html, wait_until="networkidle")
        pdf_bytes = await page.pdf(format=page_size, print_background=True)
        await context.close()
        await browser.close()
        return pdf_bytes


def render_pdf_from_html_sync(html: str, page_size: str = "A4") -> bytes:
    """
    Sync wrapper using Playwright sync API for contexts where awaiting is not possible.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.set_content(html, wait_until="networkidle")
        pdf_bytes = page.pdf(format=page_size, print_background=True)
        context.close()
        browser.close()
        return pdf_bytes




