import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import hashlib
from sqlalchemy.exc import IntegrityError
from app.db import SessionLocal, engine
from app.models import Base, Lab, RawSnapshot, LabTestPrice, TestMaster
from app.normalize import map_test_id
from scrapers.lal import LalScraper
from scrapers.apollo import ApolloScraper
from scrapers.metropolis import MetropolisScraper
from scrapers.redcliffe import RedcliffeScraper

Base.metadata.create_all(bind=engine)

SCRAPERS = [
    LalScraper(),
    ApolloScraper(),
    MetropolisScraper(),
    RedcliffeScraper(),
]

CITIES = ["Jaipur", "Delhi"]  # start with 2

def upsert_lab(db, scraper):
    lab = db.query(Lab).filter(Lab.name == scraper.name).first()
    if not lab:
        lab = Lab(name=scraper.name, website=scraper.website, brand_type="chain")
        db.add(lab)
        db.commit()
        db.refresh(lab)
    return lab

def confidence_from_age_days(days: int) -> float:
    if days <= 7: return 0.9
    if days <= 30: return 0.6
    return 0.3

def main():
    db = SessionLocal()

    tests = db.query(TestMaster.id, TestMaster.canonical_name, TestMaster.synonyms_json).all()

    for scraper in SCRAPERS:
        lab = upsert_lab(db, scraper)

        for city in CITIES:
            items = scraper.scrape(city)
            print(">>", scraper.name, city, "items:", len(items))
            if items:
                print("   sample:", items[0])

            for it in items:
                # raw snapshot placeholder (you'll add html/json later)
                raw = f"{it.test_raw}|{it.price}|{it.source_url}"
                h = hashlib.sha256(raw.encode("utf-8")).hexdigest()

                snap = RawSnapshot(lab_id=lab.id, url=it.source_url, content_hash=h, raw_text=raw)
                db.add(snap)
                db.commit()

                test_id, match_score = map_test_id(it.test_raw, tests)

                row = LabTestPrice(
                    lab_id=lab.id,
                    city=city,
                    test_raw=it.test_raw,
                    test_id=test_id,
                    price=it.price,
                    tat_text=it.tat_text,
                    tat_hours=it.tat_hours,
                    home_sample=it.home_sample,
                    nabl=it.nabl,
                    source_url=it.source_url,
                    confidence=0.9,
                )
                db.add(row)
                try:
                    db.commit()
                except IntegrityError:
                    db.rollback()

    db.close()
    print("Scrape run completed.")

if __name__ == "__main__":
    main()