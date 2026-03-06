# backend/scrapers/pw_fetch.py
from playwright.sync_api import sync_playwright

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"

def fetch_rendered_with_json(url: str, wait_ms: int = 4000, scroll: bool = True):
    """
    Returns:
      html: page.content()
      visible_text: page.inner_text("body")
      json_payloads: list[str] of response bodies for application/json responses
      response_urls: list[str] of URLs for captured JSON responses
    """
    json_payloads = []
    response_urls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=DEFAULT_UA,
            viewport={"width": 1366, "height": 800},
            locale="en-US",
        )
        page = context.new_page()

        def on_response(resp):
            try:
                ct = (resp.headers.get("content-type") or "").lower()
                if "application/json" in ct:
                    body = resp.text()
                    if body and len(body) < 2_000_000:  # guard huge responses
                        json_payloads.append(body)
                        response_urls.append(resp.url)
            except:
                pass

        page.on("response", on_response)

        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(wait_ms)

        if scroll:
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)
                page.evaluate("window.scrollTo(0, 0)")
            except:
                pass

        html = page.content()
        try:
            visible_text = page.inner_text("body")
        except:
            visible_text = ""

        context.close()
        browser.close()

    return html, visible_text, json_payloads, response_urls

    # ---- Backward compatible wrapper ----
def fetch_rendered_html(url: str, wait_ms: int = 2500) -> str:
    html, _, _, _ = fetch_rendered_with_json(url, wait_ms=wait_ms, scroll=False)
    return html