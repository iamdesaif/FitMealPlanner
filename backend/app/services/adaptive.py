from app.domain.recomp_models import WeeklyCheckinRequest, WeeklyCheckinResponse


def apply_weekly_adjustment(checkin: WeeklyCheckinRequest) -> WeeklyCheckinResponse:
    change_percent = ((checkin.previous_weight_kg - checkin.current_weight_kg) / checkin.previous_weight_kg) * 100

    if change_percent < 0.3:
        adjustment = -100
        note = "Progress below 0.3%/week. Decrease calories by 100 kcal."
    elif change_percent > 1.2:
        adjustment = 100
        note = "Progress above 1.2%/week. Increase calories by 100 kcal to reduce aggressiveness."
    else:
        adjustment = 0
        note = "Progress within target band. Keep calories unchanged."

    return WeeklyCheckinResponse(
        weekly_change_percent=round(change_percent, 2),
        adjustment_kcal=adjustment,
        new_calorie_target=checkin.previous_calorie_target + adjustment,
        note=note,
    )
