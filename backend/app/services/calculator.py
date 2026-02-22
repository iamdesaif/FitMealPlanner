from app.domain.models import ActivityLevel, Goal, MacroTargets, NutritionSummary, UserProfile


ACTIVITY_MULTIPLIER = {
    ActivityLevel.sedentary: 1.2,
    ActivityLevel.moderate: 1.55,
    ActivityLevel.active: 1.725,
}


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    meters = height_cm / 100
    return round(weight_kg / (meters * meters), 2)


def calculate_bmr(profile: UserProfile) -> int:
    # Mifflin-St Jeor equation:
    # male   = 10*weight(kg) + 6.25*height(cm) - 5*age + 5
    # female = 10*weight(kg) + 6.25*height(cm) - 5*age - 161
    base = (10 * profile.weight_kg) + (6.25 * profile.height_cm) - (5 * profile.age)
    bmr = base + 5 if profile.gender.value == "male" else base - 161
    return int(round(bmr))


def calculate_tdee(bmr: int, activity_level: ActivityLevel) -> int:
    return int(round(bmr * ACTIVITY_MULTIPLIER[activity_level]))


def calculate_calorie_target(tdee: int, goal: Goal, timeline_weeks: int) -> int:
    # Timeline-sensitive adjustment. More aggressive timelines get larger deltas.
    timeline_factor = {8: 1.0, 16: 0.8, 32: 0.6}[timeline_weeks]
    if goal == Goal.muscle_gain:
        delta = int(350 * timeline_factor)
    elif goal == Goal.fat_loss:
        delta = -int(450 * timeline_factor)
    else:
        delta = int(100 * timeline_factor)
    return max(1200, tdee + delta)


def calculate_macros(calorie_target: int, goal: Goal) -> MacroTargets:
    if goal == Goal.muscle_gain:
        protein_pct, carbs_pct, fat_pct = 0.30, 0.45, 0.25
    elif goal == Goal.fat_loss:
        protein_pct, carbs_pct, fat_pct = 0.35, 0.30, 0.35
    else:
        protein_pct, carbs_pct, fat_pct = 0.33, 0.37, 0.30

    # 1g protein = 4 kcal, 1g carbs = 4 kcal, 1g fat = 9 kcal
    protein_g = int(round((calorie_target * protein_pct) / 4))
    carbs_g = int(round((calorie_target * carbs_pct) / 4))
    fat_g = int(round((calorie_target * fat_pct) / 9))

    return MacroTargets(
        calories=calorie_target,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
    )


def build_summary(profile: UserProfile) -> NutritionSummary:
    bmi = calculate_bmi(profile.height_cm, profile.weight_kg)
    bmr = calculate_bmr(profile)
    tdee = calculate_tdee(bmr, profile.activity_level)
    calorie_target = calculate_calorie_target(tdee, profile.goal, int(profile.timeline_weeks.value))
    daily = calculate_macros(calorie_target, profile.goal)

    weekly = MacroTargets(
        calories=daily.calories * 7,
        protein_g=daily.protein_g * 7,
        carbs_g=daily.carbs_g * 7,
        fat_g=daily.fat_g * 7,
    )

    return NutritionSummary(
        bmi=bmi,
        bmr=bmr,
        tdee=tdee,
        calorie_target=calorie_target,
        daily_macros=daily,
        weekly_macros=weekly,
    )
