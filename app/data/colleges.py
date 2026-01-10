TOP_COLLEGES = [
    {"id": "ucb", "name": "University of California, Berkeley", "tier": 1},
    {"id": "stanford", "name": "Stanford University", "tier": 1},
    {"id": "mit", "name": "Massachusetts Institute of Technology", "tier": 1},
    {"id": "harvard", "name": "Harvard University", "tier": 1},
    {"id": "fau", "name": "Florida Atlantic University", "tier": 3},
]

# If a college is NOT in TOP_COLLEGES, we auto-assign this tier
DEFAULT_TIER_FOR_OTHER_COLLEGES = 5


def get_college_by_id(college_id: str):
    cid = (college_id or "").strip().lower()
    for c in TOP_COLLEGES:
        if c["id"] == cid:
            return c
    return None
