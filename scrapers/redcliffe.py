# backend/scrapers/redcliffe.py
import re
from scrapers.base import BaseScraper, ScrapedItem
from scrapers.pw_fetch import fetch_rendered_with_json

PRICE_RE = re.compile(r"(₹|rs\.?)\s*([0-9][0-9,]*(?:\.\d+)?)", re.IGNORECASE)

def _to_float(x: str):
    return float(x.replace(",", "").strip())

class RedcliffeScraper(BaseScraper):
    name = "Redcliffe Labs"
    website = "https://redcliffelabs.com"

    def scrape(self, city: str):
        url = "https://redcliffelabs.com/cbc-test"
        html, text, json_payloads, json_urls = fetch_rendered_with_json(url, wait_ms=6000, scroll=True)

        items = []
        seen = set()

        def extract_from_blob(blob: str, source_url: str):
            for m in PRICE_RE.finditer(blob):
                price = _to_float(m.group(2))
                start = max(0, m.start() - 140)
                chunk = blob[start:m.start()].strip()
                chunk = re.sub(r"[\n\r\t]+", " ", chunk)
                chunk = re.sub(r"\s+", " ", chunk).strip()

                # Keep only CBC-related names for this seed page to reduce noise
                name = chunk[-90:].strip(" ,:-\"'[]{}")
                if "cbc" not in name.lower():
                    continue

                key = (name, price)
                if key in seen:
                    continue
                seen.add(key)

                items.append(ScrapedItem(
                    test_raw=name[:180],
                    price=price,
                    tat_text=None,
                    tat_hours=None,
                    home_sample=False,
                    nabl=False,
                    source_url=source_url
                ))

        # 1) JSON first
        for blob, surl in zip(json_payloads, json_urls):
            extract_from_blob(blob, surl)

        # 2) visible text fallback
        if not items and text:
            extract_from_blob(text, url)

        # 3) html fallback
        if not items and html:
            extract_from_blob(html, url)

        return items