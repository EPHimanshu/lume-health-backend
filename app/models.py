from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.db import Base

class Lab(Base):
    __tablename__ = "labs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    website = Column(String, nullable=True)
    brand_type = Column(String, default="chain")  # chain/regional later

class TestMaster(Base):
    __tablename__ = "tests_master"
    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String, unique=True, index=True)
    category = Column(String, default="blood")
    synonyms_json = Column(Text, default="[]")  # JSON string

class RawSnapshot(Base):
    __tablename__ = "raw_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id"))
    url = Column(String, index=True)
    captured_at = Column(DateTime(timezone=True), server_default=func.now())
    content_hash = Column(String, index=True)
    raw_text = Column(Text)  # keep short; move to blob storage later

class LabTestPrice(Base):
    __tablename__ = "lab_test_prices"
    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id"), index=True)
    city = Column(String, index=True)
    test_raw = Column(String, index=True)
    test_id = Column(Integer, ForeignKey("tests_master.id"), nullable=True, index=True)

    price = Column(Float, nullable=True)
    currency = Column(String, default="INR")
    tat_text = Column(String, nullable=True)
    tat_hours = Column(Float, nullable=True)

    home_sample = Column(Boolean, default=False)
    nabl = Column(Boolean, default=False)

    source_url = Column(String)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    confidence = Column(Float, default=0.9)

    __table_args__ = (
        UniqueConstraint("lab_id", "city", "test_raw", "source_url", name="uq_lab_city_test_source"),
    )