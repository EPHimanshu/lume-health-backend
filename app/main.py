from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import Base, LabTestPrice, Lab, TestMaster
from app.scoring import best_score

Base.metadata.create_all(bind=engine)
app = FastAPI(title="TestNear Meta API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/search")
def search(
    test: str = Query(...),
    city: str = Query(...),
    mode: str = Query("best"),  # best/cheap/fast
    home: int = Query(0),
    nabl: int = Query(0),
    db: Session = Depends(get_db),
):
    # basic lookup by raw test match or canonical match
    q = db.query(LabTestPrice, Lab).join(Lab, Lab.id == LabTestPrice.lab_id).filter(LabTestPrice.city == city)

    # For MVP: match by test_raw contains OR canonical contains
    q = q.outerjoin(TestMaster, TestMaster.id == LabTestPrice.test_id)
    q = q.filter(
        (LabTestPrice.test_raw.ilike(f"%{test}%")) | (TestMaster.canonical_name.ilike(f"%{test}%"))
    )

    if home == 1:
        q = q.filter(LabTestPrice.home_sample == True)
    if nabl == 1:
        q = q.filter(LabTestPrice.nabl == True)

    rows = q.all()

    items = []
    for price_row, lab in rows:
        items.append({
            "lab": lab.name,
            "lab_website": lab.website,
            "test_raw": price_row.test_raw,
            "price": price_row.price,
            "tat_hours": price_row.tat_hours,
            "tat_text": price_row.tat_text,
            "home_sample": price_row.home_sample,
            "nabl": price_row.nabl,
            "source_url": price_row.source_url,
            "last_seen_at": price_row.last_seen_at.isoformat() if price_row.last_seen_at else None,
            "confidence": price_row.confidence,
        })

    if not items:
        return {"count": 0, "items": [], "stats": {"min": None, "avg": None}}

    prices = [x["price"] for x in items if isinstance(x["price"], (int, float))]
    stats = {"min": min(prices) if prices else None, "avg": round(sum(prices)/len(prices), 2) if prices else None}

    if mode == "cheap":
        items.sort(key=lambda x: (x["price"] if x["price"] is not None else 10**9))
    elif mode == "fast":
        items.sort(key=lambda x: (x["tat_hours"] if x["tat_hours"] is not None else 10**9))
    else:
        items.sort(key=lambda x: best_score(x), reverse=True)

    return {"count": len(items), "items": items, "stats": stats}