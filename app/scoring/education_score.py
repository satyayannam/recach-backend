def university_base_score(tier: int) -> int:
    return {1: 60, 2: 50, 3: 40, 4: 30, 5: 20}.get(tier, 0)


def degree_bonus(degree_type: str, is_completed: bool) -> int:
    d = (degree_type or "").strip().lower()
    if d == "bachelor":
        return 0
    if d == "master":
        return 10
    if d == "phd":
        return 20 if is_completed else 10
    return 0


def gpa_bonus(gpa: float | None) -> int:
    if gpa is None:
        return 0
    if gpa >= 3.9:
        return 10
    if gpa >= 3.7:
        return 8
    if gpa >= 3.5:
        return 6
    if gpa >= 3.3:
        return 4
    if gpa >= 3.0:
        return 2
    return 0


def score_education_entry(university_tier: int, degree_type: str, is_completed: bool, gpa: float | None):
    uni = university_base_score(university_tier)
    deg = degree_bonus(degree_type, is_completed)
    gpa_pts = gpa_bonus(gpa)

    return {
        "total": uni + deg + gpa_pts,
        "breakdown": {
            "university_base": uni,
            "degree_bonus": deg,
            "gpa_bonus": gpa_pts,
        },
    }
