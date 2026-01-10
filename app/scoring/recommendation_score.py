def base_points(rec_type: str) -> int:
    t = (rec_type or "").strip().lower()
    if t == "work rec":
        return 10
    if t == "academic":
        return 8
    if t == "project":
        return 6
    return 5


def weight_from_achievement(achievement_total: int) -> float:
    if achievement_total < 50:
        return 1.0
    if achievement_total < 100:
        return 1.2
    if achievement_total < 200:
        return 1.5
    return 2.0


def points_for_recommendation(rec_type: str, recommender_achievement_total: int) -> dict:
    b = base_points(rec_type)
    w = weight_from_achievement(recommender_achievement_total)
    pts = int(round(b * w))
    return {
        "points": pts,
        "breakdown": {
            "base": b,
            "weight": w,
        },
    }
