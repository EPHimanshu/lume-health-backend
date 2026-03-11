from sqlalchemy import Column, DateTime, Integer, String, func

from app.db import Base


class ClickLog(Base):
    __tablename__ = "click_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    source_page = Column(String, nullable=True)
    cta_name = Column(String, nullable=True)
    target_url = Column(String, nullable=True)
    city = Column(String, nullable=True, index=True)
    test_name = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ToolUsageLog(Base):
    __tablename__ = "tool_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String, nullable=False, index=True)
    method_used = Column(String, nullable=True, index=True)
    source_page = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)