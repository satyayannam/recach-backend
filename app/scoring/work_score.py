from datetime import date


def months_between(start: date, end: date) -> int:
    # full months approximation: good enough for MVP
    return max(0, (end.year - start.year) * 12 + (end.month - start.month))


def base_points(employment_type: str) -> int:
    t = (employment_type or "").strip().lower()
    if t == "internship":
        return 10
    if t == "full_time":
        return 20
    if t == "part_time":
        return 12
    if t == "contract":
        return 14
    return 8  # unknown type fallback


def duration_points(months: int) -> int:
    if months < 6:
        return 0
    if months < 12:
        return 5
    if months < 24:
        return 12
    if months < 36:
        return 20
    return 30


def score_work_entry(employment_type: str, start_date: date, end_date: date):
    b = base_points(employment_type)
    m = months_between(start_date, end_date)
    d = duration_points(m)

    return {
        "total": b + d,
        "breakdown": {
            "base": b,
            "months": m,
            "duration_bonus": d,
        },
    }
