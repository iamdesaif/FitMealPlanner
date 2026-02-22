from fastapi import APIRouter, Query

from app.domain.recomp_models import (
    ACTIVITY_MULTIPLIERS,
    CalculatePlanResponse,
    GenerateMealsRequest,
    GenerateMealsResponse,
    PlanInput,
    WeeklyCheckinRequest,
    WeeklyCheckinResponse,
)
from app.services.adaptive import apply_weekly_adjustment
from app.services.grocery_engine import build_grocery_list
from app.services.meal_engine import generate_weekly_meal_plan
from app.services.physiology import body_composition, calories_plan, macro_plan
from app.services.projection import projection
from app.services.retail_enricher import enrich_with_retail_products

router = APIRouter(tags=["recomposition"])


@router.post("/calculate-plan", response_model=CalculatePlanResponse)
def calculate_plan(payload: PlanInput) -> CalculatePlanResponse:
    comp = body_composition(payload)
    kcal = calories_plan(payload)
    macros = macro_plan(payload, comp, kcal)
    proj = projection(payload, comp)
    return CalculatePlanResponse(body_composition=comp, calories=kcal, macros=macros, projection=proj)


@router.post("/generate-meals", response_model=GenerateMealsResponse)
async def generate_meals(payload: GenerateMealsRequest) -> GenerateMealsResponse:
    plan = payload.plan
    comp = body_composition(plan)
    kcal = calories_plan(plan)
    macros = macro_plan(plan, comp, kcal)
    proj = projection(plan, comp)

    weekly_meals = generate_weekly_meal_plan(plan, macros)
    grocery = build_grocery_list(weekly_meals)
    weekly_meals, grocery = await enrich_with_retail_products(
        weekly_plan=weekly_meals,
        grocery_list=grocery,
        country_code=plan.country_code,
        preferred_retailers=plan.preferred_retailers,
    )

    return GenerateMealsResponse(
        body_composition=comp,
        calories=kcal,
        macros=macros,
        projection=proj,
        meal_plan=weekly_meals,
        grocery_list=grocery,
    )


@router.post("/weekly-checkin", response_model=WeeklyCheckinResponse)
def weekly_checkin(payload: WeeklyCheckinRequest) -> WeeklyCheckinResponse:
    return apply_weekly_adjustment(payload)


@router.get("/projection")
def get_projection(
    weight_kg: float = Query(gt=35, lt=300),
    body_fat_percent: float = Query(ge=4, le=60),
    target_body_fat_percent: float = Query(ge=4, le=40),
    height_cm: float = Query(gt=120, lt=230),
    age: int = Query(ge=14, le=90),
    gender: str = Query(pattern="^(male|female)$"),
    activity_level: str = Query(pattern="^(sedentary|light|moderate|high|athlete)$"),
    training_days_per_week: int = Query(ge=0, le=7),
    timeline_weeks: int = Query(default=16, ge=4, le=52),
    goal_mode: str = Query(pattern="^(fat_loss|recomposition)$"),
) -> dict:
    plan = PlanInput(
        height_cm=height_cm,
        weight_kg=weight_kg,
        age=age,
        gender=gender,
        body_fat_percent=body_fat_percent,
        target_body_fat_percent=target_body_fat_percent,
        activity_level=activity_level,
        training_days_per_week=training_days_per_week,
        timeline_weeks=timeline_weeks,
        goal_mode=goal_mode,
    )
    comp = body_composition(plan)
    proj = projection(plan, comp)
    return {"projection": proj.model_dump(), "activity_multipliers": {k.value: v for k, v in ACTIVITY_MULTIPLIERS.items()}}
