import math
from app.domain.recomp_models import (
    ACTIVITY_MULTIPLIERS,
    ActivityLevel,
    BodyComposition,
    CaloriesPlan,
    GoalMode,
    MacroPlan,
    MacroTargets,
    PlanInput,
)


def body_composition(plan: PlanInput) -> BodyComposition:
    bf = plan.body_fat_percent / 100
    target_bf = plan.target_body_fat_percent / 100

    lbm = plan.weight_kg * (1 - bf)
    fm = plan.weight_kg - lbm
    target_weight = lbm / (1 - target_bf)
    fat_loss_required = max(0.0, plan.weight_kg - target_weight)

    return BodyComposition(
        lean_body_mass_kg=round(lbm, 2),
        fat_mass_kg=round(fm, 2),
        target_weight_kg=round(target_weight, 2),
        fat_loss_required_kg=round(fat_loss_required, 2),
    )


def bmr_mifflin(plan: PlanInput) -> int:
    # Mifflin-St Jeor (1990): widely used resting metabolic rate equation.
    base = (10 * plan.weight_kg) + (6.25 * plan.height_cm) - (5 * plan.age)
    value = base + 5 if plan.gender.value == "male" else base - 161
    return int(round(value))


def tdee_from_activity(bmr: int, activity_level: ActivityLevel) -> int:
    return int(round(bmr * ACTIVITY_MULTIPLIERS[activity_level]))


def loss_rate_percent(body_fat_percent: float) -> float:
    if body_fat_percent > 20:
        return 1.0
    if body_fat_percent < 15:
        return 0.5
    return 0.75


def weekly_loss_kg_for_plan(plan: PlanInput, fat_loss_required_kg: float | None = None) -> float:
    # Timeline is a user pacing preference; enforce evidence-based safe weekly loss bounds.
    base_rate_percent = loss_rate_percent(plan.body_fat_percent)
    # Allow slower pacing for recomposition timelines while keeping fat-loss mode more aggressive.
    min_rate_percent = 0.5 if plan.goal_mode == GoalMode.fat_loss else 0.25
    max_rate_percent = 1.0 if plan.body_fat_percent > 20 else base_rate_percent

    if fat_loss_required_kg is None:
        comp = body_composition(plan)
        fat_loss_required_kg = comp.fat_loss_required_kg

    if plan.timeline_weeks > 0 and fat_loss_required_kg > 0:
        required_weekly_loss = fat_loss_required_kg / plan.timeline_weeks
        required_rate_percent = (required_weekly_loss / plan.weight_kg) * 100
        chosen_rate_percent = max(min_rate_percent, min(required_rate_percent, max_rate_percent))
    else:
        chosen_rate_percent = base_rate_percent

    return plan.weight_kg * (chosen_rate_percent / 100)


def calories_plan(plan: PlanInput) -> CaloriesPlan:
    bmr = bmr_mifflin(plan)
    tdee = tdee_from_activity(bmr, plan.activity_level)

    comp = body_composition(plan)
    weekly_loss_kg = weekly_loss_kg_for_plan(plan, comp.fat_loss_required_kg)

    # Hall et al. (2008) practical energy equivalent: ~7700 kcal per kg fat mass.
    daily_deficit = int(round((weekly_loss_kg * 7700) / 7))
    target = tdee - daily_deficit

    floor_target = int(round(bmr * 1.2))
    target = max(target, floor_target)

    if plan.training_days_per_week >= 4 and plan.training_days_per_week < 7:
        training_day = target + 200
        rest_days = 7 - plan.training_days_per_week
        rest_day = int(round((target * 7 - (training_day * plan.training_days_per_week)) / rest_days))
    else:
        training_day = target
        rest_day = target

    return CaloriesPlan(
        bmr=bmr,
        tdee=tdee,
        daily_deficit=daily_deficit,
        target=target,
        training_day=training_day,
        rest_day=rest_day,
    )


def _macro_targets_for_day(calories: int, weight_kg: float, lbm_kg: float, goal_mode: GoalMode) -> MacroTargets:
    # Helms et al. (2014): higher protein preserves lean mass during dieting.
    protein_per_kg_lbm = 2.2 if goal_mode == GoalMode.fat_loss else 2.0
    protein_g = int(round(lbm_kg * protein_per_kg_lbm))

    fat_per_kg_bw = 0.7
    fat_g = int(round(weight_kg * fat_per_kg_bw))
    fat_g = max(int(math.ceil(weight_kg * 0.6)), min(fat_g, int(math.floor(weight_kg * 0.8))))

    protein_kcal = protein_g * 4
    fat_kcal = fat_g * 9
    carbs_kcal = max(0, calories - protein_kcal - fat_kcal)
    carbs_g = int(round(carbs_kcal / 4))

    return MacroTargets(
        calories=calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        fiber_g=30,
    )


def macro_plan(plan: PlanInput, body_comp: BodyComposition, calories: CaloriesPlan) -> MacroPlan:
    base = _macro_targets_for_day(calories.target, plan.weight_kg, body_comp.lean_body_mass_kg, plan.goal_mode)

    # Training-day carb periodization while keeping protein stable.
    training = _macro_targets_for_day(calories.training_day, plan.weight_kg, body_comp.lean_body_mass_kg, plan.goal_mode)
    rest = _macro_targets_for_day(calories.rest_day, plan.weight_kg, body_comp.lean_body_mass_kg, plan.goal_mode)

    training = training.model_copy(update={"protein_g": base.protein_g, "fat_g": base.fat_g})
    training_carbs = max(0, int(round((training.calories - (training.protein_g * 4) - (training.fat_g * 9)) / 4)))
    training = training.model_copy(update={"carbs_g": training_carbs})

    rest = rest.model_copy(update={"protein_g": base.protein_g, "fat_g": base.fat_g})
    rest_carbs = max(0, int(round((rest.calories - (rest.protein_g * 4) - (rest.fat_g * 9)) / 4)))
    rest = rest.model_copy(update={"carbs_g": rest_carbs})

    return MacroPlan(baseline=base, training_day=training, rest_day=rest)
