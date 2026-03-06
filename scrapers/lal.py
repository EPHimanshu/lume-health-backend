import re
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, ScrapedItem
from scrapers.pw_fetch import fetch_rendered_html
PRICE_RE = re.compile(r"(₹|Rs\.?)\s*([0-9][0-9,]*)", re.IGNORECASE)

def _to_float(x: str):
    return float(x.replace(",", "").strip())

def slug_city(city: str) -> str:
    return city.lower().strip().replace(" ", "-")

class LalScraper(BaseScraper):
    name = "Dr Lal PathLabs"
    website = "https://www.lalpathlabs.com"

    def scrape(self, city: str):
        # Your screenshot proves this URL works for Delhi:
        # https://www.lalpathlabs.com/test/city/delhi
        url = f"https://www.lalpathlabs.com/test/city/{slug_city(city)}"

        html = fetch_rendered_html(url, wait_ms=3000)
        soup = BeautifulSoup(html, "lxml")

        items = []
        seen = set()

        # Strategy:
        # Find all text nodes containing ₹xxx.xx or ₹xxx
        # Then climb to a reasonable parent card container, extract title + price
        for node in soup.find_all(string=re.compile(r"₹\s*[0-9]")):
            text = node.strip()
            m = PRICE_RE.search(text)
            if not m:
                continue
            price = _to_float(m.group(2))

            # climb up to find a card-like container
            card = node.parent
            for _ in range(8):
                if not card:
                    break
                block_text = card.get_text(" ", strip=True)

                # must include Book Now or Know More to indicate it's a card
                if ("Book Now" in block_text) and PRICE_RE.search(block_text):
                    # title is usually at the top of the card in CAPS
                    # choose first strong line before parameters
                    # fallback: first 80 chars before price
                    title_guess = None

                    # try: heading tags inside card
                    h = card.find(["h2", "h3", "h4"])
                    if h:
                        title_guess = h.get_text(" ", strip=True)

                    if not title_guess:
                        # pick text before first icon line / or before price
                        title_guess = block_text.split("₹")[0].strip()
                        # cleanup common suffix noise
                        title_guess = title_guess.split("parameter")[0].strip()

                    test_raw = (title_guess or "").strip()

                    if len(test_raw) < 3:
                        break

                    key = (test_raw, price)
                    if key in seen:
                        break
                    seen.add(key)

                    # Extract simple TAT if visible
                    tat_text = None
                    if "Daily" in block_text:
                        tat_text = "Daily"

                    items.append(
                        ScrapedItem(
                            test_raw=test_raw[:170],
                            price=price,
                            tat_text=tat_text,
                            tat_hours=None,
                            home_sample=True,   # the page says “at Home in Delhi”
                            nabl=False,          # set True only if explicitly available
                            source_url=url,
                        )
                    )
                    break

                card = card.parent

        return items