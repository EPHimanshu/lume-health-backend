from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.pregnancy.models import ClickLog, ToolUsageLog
from app.pregnancy.schemas import (
    ClickLogCreate,
    ClickLogResponse,
    ToolUsageLogCreate,
    ToolUsageLogResponse,
)

router = APIRouter()


@router.post("/click", response_model=ClickLogResponse)
def log_click(payload: ClickLogCreate, db: Session = Depends(get_db)) -> ClickLogResponse:
    click = ClickLog(
        event_type=payload.event_type,
        source_page=payload.source_page,
        cta_name=payload.cta_name,
        target_url=payload.target_url,
        city=payload.city,
        test_name=payload.test_name,
    )
    db.add(click)
    db.commit()
    db.refresh(click)

    return ClickLogResponse(ok=True, id=click.id)


@router.post("/tool-usage", response_model=ToolUsageLogResponse)
def log_tool_usage(
    payload: ToolUsageLogCreate,
    db: Session = Depends(get_db),
) -> ToolUsageLogResponse:
    usage = ToolUsageLog(
        tool_name=payload.tool_name,
        method_used=payload.method_used,
        source_page=payload.source_page,
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)

    return ToolUsageLogResponse(ok=True, id=usage.id)