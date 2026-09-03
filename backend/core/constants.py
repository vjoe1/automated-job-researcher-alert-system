

from schemas.schemas import PostedRange, ExperienceLevel

POSTED_RANGE_DAYS = {
    PostedRange.today: 1,
    PostedRange.last_3_days: 3,
    PostedRange.last_week: 7,
    PostedRange.last_month: 30,
}

EXPERIENCE_LEVEL_YEARS = {
    ExperienceLevel.entry: (0, 2),
    ExperienceLevel.mid: (3, 5),
    ExperienceLevel.senior: (6, 9),
    ExperienceLevel.staff: (10, 100),
}