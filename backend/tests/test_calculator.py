from app.domain.models import ActivityLevel, Gender, Goal, TimelineWeeks, UserProfile
from app.services.calculator import build_summary


def test_summary_generation() -> None:
    profile = UserProfile(
        height_cm=180,
        weight_kg=80,
        age=30,
        gender=Gender.male,
        body_fat_percent=18,
        activity_level=ActivityLevel.moderate,
        goal=Goal.muscle_gain,
        timeline_weeks=TimelineWeeks.sixteen,
        country_code="US",
    )

    summary = build_summary(profile)
    assert summary.bmr > 0
    assert summary.tdee > summary.bmr
    assert summary.daily_macros.calories == summary.calorie_target
