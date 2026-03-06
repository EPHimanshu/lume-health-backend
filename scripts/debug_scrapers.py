import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scrapers.apollo import ApolloScraper
from scrapers.lal import LalScraper
from scrapers.redcliffe import RedcliffeScraper
from scrapers.metropolis import MetropolisScraper

def run(scraper, city):
    print("\n===", scraper.name, "===", city)
    try:
        items = scraper.scrape(city)
        print("items:", len(items))
        if items:
            print("sample:", items[0])
    except Exception as e:
        print("ERROR:", type(e).__name__, str(e))
        items = []
    return items

if __name__ == "__main__":
    city = "Delhi"
    run(MetropolisScraper(), city)
    run(ApolloScraper(), city)
    run(LalScraper(), city)
    run(RedcliffeScraper(), city)