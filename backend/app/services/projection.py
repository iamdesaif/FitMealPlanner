import math
from app.domain.recomp_models import BodyComposition, MonthlyMilestone, PlanInput, Projection, WeeklyWeightTarget
from app.services.physiology import weekly_loss_kg_for_plan


def projection(plan: PlanInput, body_comp: BodyComposition) -> Projection:
    weekly_loss_kg = weekly_loss_kg_for_plan(plan, body_comp.fat_loss_required_kg)

    if body_comp.fat_loss_required_kg <= 0 or weekly_loss_kg <= 0:
        return Projection(
            weeks_to_goal=0,
            weekly_loss_kg=0,
            weekly_weight_targets=[WeeklyWeightTarget(week=0, expected_weight_kg=round(plan.weight_kg, 2))],
            monthly_milestones=[],
        )

    weeks = body_comp.fat_loss_required_kg / weekly_loss_kg
    max_weeks = min(int(math.ceil(weeks)), 104)

    weekly_targets: list[WeeklyWeightTarget] = []
    for week in range(1, max_weeks + 1):
        expected_weight = max(body_comp.target_weight_kg, plan.weight_kg - (weekly_loss_kg * week))
        weekly_targets.append(WeeklyWeightTarget(week=week, expected_weight_kg=round(expected_weight, 2)))

    monthly: list[MonthlyMilestone] = []
    month_idx = 1
    for week in range(4, max_weeks + 1, 4):
        expected_weight = max(body_comp.target_weight_kg, plan.weight_kg - (weekly_loss_kg * week))
        monthly.append(MonthlyMilestone(month=month_idx, expected_weight_kg=round(expected_weight, 2)))
        month_idx += 1

    return Projection(
        weeks_to_goal=round(weeks, 1),
        weekly_loss_kg=round(weekly_loss_kg, 3),
        weekly_weight_targets=weekly_targets,
        monthly_milestones=monthly,
    )
