from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.pregnancy.services.pregnancy import (
    calculate_from_conception,
    calculate_from_due_date,
    calculate_from_ivf,
    calculate_from_lmp,
    calculate_from_ultrasound,
)

router = APIRouter(prefix="/tools", tags=["Tools"])


class PregnancyCalcRequest(BaseModel):
    method: str = Field(..., description="lmp | conception | ivf | due_date | ultrasound")
    today: Optional[date] = None

    lmp_date: Optional[date] = None
    cycle_length: Optional[int] = 28

    conception_date: Optional[date] = None

    ivf_transfer_date: Optional[date] = None
    embryo_age_days: Optional[int] = 5

    due_date: Optional[date] = None

    ultrasound_date: Optional[date] = None
    pregnancy_weeks: Optional[int] = None
    pregnancy_days: Optional[int] = None


@router.post("/pregnancy/calculate")
def calculate_pregnancy(payload: PregnancyCalcRequest):
    method = payload.method.strip().lower()
    today = payload.today or date.today()

    try:
        if method == "lmp":
            if not payload.lmp_date:
                raise HTTPException(status_code=400, detail="lmp_date is required for method='lmp'")
            return calculate_from_lmp(
                lmp_date=payload.lmp_date,
                cycle_length=payload.cycle_length or 28,
                today=today,
            )

        if method == "conception":
            if not payload.conception_date:
                raise HTTPException(status_code=400, detail="conception_date is required for method='conception'")
            return calculate_from_conception(
                conception_date=payload.conception_date,
                today=today,
            )

        if method == "ivf":
            if not payload.ivf_transfer_date:
                raise HTTPException(status_code=400, detail="ivf_transfer_date is required for method='ivf'")
            return calculate_from_ivf(
                transfer_date=payload.ivf_transfer_date,
                embryo_age_days=payload.embryo_age_days or 5,
                today=today,
            )

        if method == "due_date":
            if not payload.due_date:
                raise HTTPException(status_code=400, detail="due_date is required for method='due_date'")
            return calculate_from_due_date(
                due_date=payload.due_date,
                today=today,
            )

        if method == "ultrasound":
            if not payload.ultrasound_date:
                raise HTTPException(status_code=400, detail="ultrasound_date is required for method='ultrasound'")
            if payload.pregnancy_weeks is None or payload.pregnancy_days is None:
                raise HTTPException(
                    status_code=400,
                    detail="pregnancy_weeks and pregnancy_days are required for method='ultrasound'",
                )
            return calculate_from_ultrasound(
                ultrasound_date=payload.ultrasound_date,
                pregnancy_weeks=payload.pregnancy_weeks,
                pregnancy_days=payload.pregnancy_days,
                today=today,
            )

        raise HTTPException(status_code=400, detail="Invalid method")

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc