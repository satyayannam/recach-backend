from datetime import date
from collections import defaultdict


def months_between(start: date, end: date) -> int:
    """
    Returns whole-month difference between start and end.
    If end is before start -> 0.
    """
    if not start or not end or end <= start:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)


def streak_bonus_from_months(total_months: int) -> int:
    years = total_months // 12
    if years <= 0:
        return 0
    return years * 3  # 3 points per full year


def compute_company_streaks(work_entries):
    """
    work_entries: list of WorkExperience rows
    Returns:
      - streak_total
      - per_company breakdown
    """
    if not work_entries:
        return 0, []

    by_company = defaultdict(int)

    for w in work_entries:
        # robust end date handling
        end_dt = w.end_date
        if getattr(w, "is_current", False) or end_dt is None:
            end_dt = date.today()

        start_dt = w.start_date
        if start_dt is None:
            continue

        # robust company name handling
        raw_company = getattr(w, "company_name", None)
        company_key = (raw_company or "").strip().lower()
        if not company_key:
            company_key = "unknown"

        by_company[company_key] += months_between(start_dt, end_dt)

    breakdown = []
    total = 0

    for company_key, months in by_company.items():
        bonus = streak_bonus_from_months(months)
        total += bonus
        breakdown.append(
            {
                "company": company_key,
                "total_months": months,
                "streak_bonus": bonus,
            }
        )

    breakdown.sort(key=lambda x: x["streak_bonus"], reverse=True)
    return total, breakdown
