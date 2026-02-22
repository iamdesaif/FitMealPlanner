from app.domain.recomp_models import ActivityLevel, Gender, GoalMode, PlanInput
from app.services.physiology import bmr_mifflin, body_composition, calories_plan, macro_plan, tdee_from_activity
from app.services.projection import projection


def _sample_plan() -> PlanInput:
    return PlanInput(
        height_cm=171,
        weight_kg=71,
        age=31,
        gender=Gender.male,
        body_fat_percent=18,
        target_body_fat_percent=12,
        activity_level=ActivityLevel.moderate,
        training_days_per_week=4,
        goal_mode=GoalMode.recomposition,
    )


def test_bmr_mifflin() -> None:
    plan = _sample_plan()
    # Expected from Mifflin-St Jeor equation.
    assert bmr_mifflin(plan) == 1629


def test_tdee_activity_multiplier() -> None:
    assert tdee_from_activity(1629, ActivityLevel.moderate) == 2525


def test_projection_weeks_positive() -> None:
    plan = _sample_plan()
    comp = body_composition(plan)
    proj = projection(plan, comp)
    assert proj.weeks_to_goal > 0
    assert len(proj.weekly_weight_targets) >= 1


def test_macro_split_non_negative_and_protein_constant() -> None:
    plan = _sample_plan()
    comp = body_composition(plan)
    kcal = calories_plan(plan)
    macros = macro_plan(plan, comp, kcal)

    assert macros.baseline.protein_g > 0
    assert macros.training_day.protein_g == macros.baseline.protein_g
    assert macros.rest_day.protein_g == macros.baseline.protein_g
    assert macros.training_day.carbs_g >= macros.rest_day.carbs_g


def test_timeline_changes_projection() -> None:
    fast = PlanInput(
        height_cm=171,
        weight_kg=71,
        age=31,
        gender=Gender.male,
        body_fat_percent=18,
        target_body_fat_percent=12,
        activity_level=ActivityLevel.moderate,
        training_days_per_week=4,
        timeline_weeks=8,
        goal_mode=GoalMode.recomposition,
    )
    slow = fast.model_copy(update={"timeline_weeks": 32})

    fast_proj = projection(fast, body_composition(fast))
    slow_proj = projection(slow, body_composition(slow))

    assert fast_proj.weeks_to_goal < slow_proj.weeks_to_goal
