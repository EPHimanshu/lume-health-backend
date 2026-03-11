from datetime import date, timedelta


def add_days(input_date: date, days: int) -> date:
    return input_date + timedelta(days=days)


def days_between(start_date: date, end_date: date) -> int:
    return (end_date - start_date).days


def format_date_range(start_date: date, end_date: date) -> str:
    return f"{start_date.isoformat()} to {end_date.isoformat()}"