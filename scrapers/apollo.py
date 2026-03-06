import re
from scrapers.base import BaseScraper, ScrapedItem
from playwright.sync_api import sync_playwright

PRICE_RE = re.compile(r"₹\s*([0-9][0-9,]*(?:\.\d+)?)")

def _to_float(x: str):
    return float(x.replace(",", "").strip())

class ApolloScraper(BaseScraper):
    name = "Apollo Diagnostics"
    website = "https://apollodiagnostics.in"

    def scrape(self, city: str):
        url = "https://apollodiagnostics.in/"
        items, seen = [], set()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)

            # Get all elements that visibly contain ₹
            els = page.locator("text=/₹\\s*[0-9]/").all()

            for el in els:
                try:
                    # Walk up to a “card-like” container
                    card = el.locator("xpath=ancestor::*[self::div or self::section][1]")
                    card_text = card.inner_text(timeout=2000)
                    m = PRICE_RE.search(card_text)
                    if not m:
                        continue

                    price = _to_float(m.group(1))

                    # Title: prefer strong heading text
                    title = None
                    for sel in ["h1", "h2", "h3", "h4"]:
                        h = card.locator(sel)
                        if h.count() > 0:
                            t = h.first.inner_text().strip()
                            if len(t) >= 4:
                                title = t
                                break

                    if not title:
                        # fallback: first line before ₹
                        title = card_text.split("₹")[0].split("\n")[0].strip()

                    # cleanup
                    title = re.sub(r"\s+", " ", title).strip()
                    if len(title) < 4:
                        continue

                    # Keep only likely test/package names (remove support phrases)
                    bad_words = ["customer care", "report delivery", "speak to", "home collection available"]
                    if any(w in title.lower() for w in bad_words):
                        continue

                    key = (title, price)
                    if key in seen:
                        continue
                    seen.add(key)

                    items.append(
                        ScrapedItem(
                            test_raw=title[:180],
                            price=price,
                            tat_text=None,
                            tat_hours=None,
                            home_sample=("home" in card_text.lower() and "collection" in card_text.lower()),
                            nabl=False,
                            source_url=url,
                        )
                    )
                except:
                    continue

            browser.close()

        return items