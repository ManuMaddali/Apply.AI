from __future__ import annotations

from typing import Optional


PDF_MARGIN = {"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"}


async def render_pdf_from_html(html: str, page_size: str = "Letter") -> bytes:
    """
    Async HTML -> PDF rendering using Playwright Chromium.
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_content(html, wait_until="networkidle")
        # Force single page by limiting height to one page and scale to fit
        # Ensure Letter size and compact margins; avoid page breaks
        pdf_bytes = await page.pdf(
            format=page_size,
            print_background=True,
            margin=PDF_MARGIN,
            prefer_css_page_size=True,
            page_ranges="1"
        )
        await context.close()
        await browser.close()
        return pdf_bytes


def render_pdf_from_html_sync(html: str, page_size: str = "Letter") -> Optional[bytes]:
    """
    Sync wrapper using Playwright with more robust defaults for server environments.
    Returns None if rendering fails so callers can fallback.
    """
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Hardened launch options (CI/containers/macOS permissions)
            browser = p.chromium.launch(headless=True, args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-setuid-sandbox"
            ])
            context = browser.new_context()
            page = context.new_page()
            # Allow up to 60s for complex HTML/CSS to layout
            page.set_content(html, wait_until="load", timeout=60000)
            pdf_bytes = page.pdf(
                format=page_size,
                print_background=True,
                margin=PDF_MARGIN,
                prefer_css_page_size=True,
                page_ranges="1"
            )
            context.close()
            browser.close()
            return pdf_bytes
    except Exception as e:
        # Surface a minimal hint to application logs; callers decide fallback
        print(f"❌ Playwright render failed: {e}")
        return None




