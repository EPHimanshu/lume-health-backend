import re
import requests
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, ScrapedItem

PRICE_RE = re.compile(r"(Rs\.?|₹)\s*([0-9][0-9,]*)", re.IGNORECASE)

def _to_float(x):
    if not x:
        return None
    return float(x.replace(",", "").strip())

class MetropolisScraper(BaseScraper):
    name = "Metropolis Healthcare"
    website = "https://www.metropolisindia.com"

    def scrape(self, city: str):
        url = "https://www.metropolisindia.com/"
        html = requests.get(url, timeout=25).text
        soup = BeautifulSoup(html, "lxml")

        items = []
        seen = set()

        # Grab chunks near "Add to cart" / "Rs." patterns
        candidates = soup.find_all(string=re.compile(r"Add to cart|Rs\.|₹", re.IGNORECASE))
        for node in candidates:
            block = node.parent
            for _ in range(6):
                if not block or block.name == "body":
                    break

                text = block.get_text(" ", strip=True)
                if ("Add to cart" in text) and PRICE_RE.search(text):
                    m = PRICE_RE.search(text)
                    price = _to_float(m.group(2)) if m else None
                    if not price:
                        break

                    # Try to find test name from nearby heading
                    heading = block.find_previous(["h2", "h3", "h4"])
                    test_raw = heading.get_text(" ", strip=True) if heading else None
                    if not test_raw:
                        # fallback: portion before price token
                        test_raw = text.split(m.group(0))[0].strip()[:140]

                    key = (test_raw, price)
                    if test_raw and key not in seen:
                        seen.add(key)
                        items.append(
                            ScrapedItem(
                                test_raw=test_raw,
                                price=price,
                                tat_text=None,
                                tat_hours=None,
                                home_sample=False,
                                nabl=False,
                                source_url=url,
                            )
                        )
                    break

                block = block.parent

        return items