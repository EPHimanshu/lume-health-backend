def validate_cycle_length(cycle_length: int) -> None:
    if cycle_length < 21 or cycle_length > 45:
        raise ValueError("Cycle length must be between 21 and 45 days.")


def validate_embryo_age(embryo_age_days: int) -> None:
    if embryo_age_days not in (3, 5):
        raise ValueError("Embryo age must be either 3 or 5 days.")


def validate_ultrasound_inputs(pregnancy_weeks: int, pregnancy_days: int) -> None:
    if pregnancy_weeks < 0 or pregnancy_weeks > 45:
        raise ValueError("Pregnancy weeks must be between 0 and 45.")
    if pregnancy_days < 0 or pregnancy_days > 6:
        raise ValueError("Pregnancy days must be between 0 and 6.")