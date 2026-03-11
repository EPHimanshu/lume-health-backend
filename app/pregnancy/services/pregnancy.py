from datetime import date

from app.pregnancy.utils.dates import add_days, days_between, format_date_range
from app.pregnancy.utils.validators import (
    validate_cycle_length,
    validate_embryo_age,
    validate_ultrasound_inputs,
)


def get_trimester(total_days_elapsed: int) -> str:
    if total_days_elapsed < 0:
        return ""
    if total_days_elapsed < 14 * 7:
        return "First trimester"
    if total_days_elapsed < 28 * 7:
        return "Second trimester"
    return "Third trimester"


def get_week_and_day(total_days_elapsed: int) -> tuple[int, int]:
    safe_days = max(total_days_elapsed, 0)
    weeks = safe_days // 7
    days = safe_days % 7
    return weeks, days


def build_milestone_windows(estimated_lmp_date: date) -> list[dict]:
    milestones = [
        {"label": "First visit window", "start_day": 42, "end_day": 56},
        {"label": "NT scan window", "start_day": 77, "end_day": 98},
        {"label": "Anomaly scan window", "start_day": 126, "end_day": 154},
        {"label": "Glucose screening window", "start_day": 168, "end_day": 196},
    ]

    return [
        {
            "label": item["label"],
            "start": add_days(estimated_lmp_date, item["start_day"]).isoformat(),
            "end": add_days(estimated_lmp_date, item["end_day"]).isoformat(),
            "display": format_date_range(
                add_days(estimated_lmp_date, item["start_day"]),
                add_days(estimated_lmp_date, item["end_day"]),
            ),
        }
        for item in milestones
    ]


def build_result(estimated_lmp_date: date, estimated_due_date: date, today: date) -> dict:
    total_days_elapsed = days_between(estimated_lmp_date, today)
    gestational_weeks, gestational_days = get_week_and_day(total_days_elapsed)
    estimated_conception_date = add_days(estimated_lmp_date, 14)

    return {
        "estimated_lmp_date": estimated_lmp_date.isoformat(),
        "estimated_due_date": estimated_due_date.isoformat(),
        "estimated_conception_date": estimated_conception_date.isoformat(),
        "gestational_weeks": gestational_weeks,
        "gestational_days_remainder": gestational_days,
        "total_pregnancy_days_elapsed": total_days_elapsed,
        "trimester": get_trimester(total_days_elapsed),
        "important_dates": {
            "first_trimester_end": add_days(estimated_lmp_date, 13 * 7 + 6).isoformat(),
            "second_trimester_end": add_days(estimated_lmp_date, 27 * 7 + 6).isoformat(),
            "full_term_start": add_days(estimated_lmp_date, 37 * 7).isoformat(),
            "full_term_end": add_days(estimated_lmp_date, 40 * 7).isoformat(),
        },
        "milestone_windows": build_milestone_windows(estimated_lmp_date),
    }


def calculate_from_lmp(lmp_date: date, cycle_length: int, today: date) -> dict:
    validate_cycle_length(cycle_length)
    cycle_adjustment = cycle_length - 28
    estimated_due_date = add_days(lmp_date, 280 + cycle_adjustment)
    return build_result(lmp_date, estimated_due_date, today)


def calculate_from_conception(conception_date: date, today: date) -> dict:
    estimated_due_date = add_days(conception_date, 266)
    estimated_lmp_date = add_days(conception_date, -14)
    return build_result(estimated_lmp_date, estimated_due_date, today)


def calculate_from_ivf(transfer_date: date, embryo_age_days: int, today: date) -> dict:
    validate_embryo_age(embryo_age_days)
    lmp_offset = 14 - embryo_age_days
    estimated_lmp_date = add_days(transfer_date, -lmp_offset)
    estimated_due_date = add_days(estimated_lmp_date, 280)
    return build_result(estimated_lmp_date, estimated_due_date, today)


def calculate_from_due_date(due_date: date, today: date) -> dict:
    estimated_lmp_date = add_days(due_date, -280)
    return build_result(estimated_lmp_date, due_date, today)


def calculate_from_ultrasound(
    ultrasound_date: date,
    pregnancy_weeks: int,
    pregnancy_days: int,
    today: date,
) -> dict:
    validate_ultrasound_inputs(pregnancy_weeks, pregnancy_days)
    elapsed_days_at_scan = pregnancy_weeks * 7 + pregnancy_days
    estimated_lmp_date = add_days(ultrasound_date, -elapsed_days_at_scan)
    estimated_due_date = add_days(estimated_lmp_date, 280)
    return build_result(estimated_lmp_date, estimated_due_date, today)