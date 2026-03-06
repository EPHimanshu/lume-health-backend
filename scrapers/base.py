from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ScrapedItem:
    test_raw: str
    price: Optional[float]
    tat_text: Optional[str]
    tat_hours: Optional[float]
    home_sample: bool
    nabl: bool
    source_url: str

class BaseScraper:
    name: str = "base"
    website: str = ""

    def scrape(self, city: str) -> List[ScrapedItem]:
        raise NotImplementedError("Implement in child class")