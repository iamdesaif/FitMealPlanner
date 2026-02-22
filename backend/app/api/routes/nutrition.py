import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.models import GroceryItem, NutritionSummary, UserProfile, WeeklyMealPlan
from app.services.calculator import build_summary
from app.services.grocery_planner import aggregate_grocery_list
from app.services.meal_planner import generate_weekly_plan
from app.services.product_recommender import recommend_brands, recommend_brands_by_ingredient

router = APIRouter(prefix="/api/v1", tags=["nutrition"])


class PlanResponse(BaseModel):
    profile: UserProfile
    summary: NutritionSummary
    weekly_meal_plan: WeeklyMealPlan
    grocery_list: list[GroceryItem]
    brand_suggestions: list[dict]


@router.post("/plan", response_model=PlanResponse)
async def generate_plan(profile: UserProfile) -> PlanResponse:
    try:
        summary = build_summary(profile)
        weekly_plan = generate_weekly_plan(summary.daily_macros, profile.dietary_preference, profile.goal)
        grocery_list = aggregate_grocery_list(weekly_plan)
        ingredient_names = [g.ingredient for g in grocery_list]
        try:
            # External API calls should not block plan generation.
            ingredient_brand_map = await asyncio.wait_for(
                recommend_brands_by_ingredient(profile.country_code, ingredient_names), timeout=6.0
            )
        except Exception:
            ingredient_brand_map = {}

        for day in weekly_plan.days.values():
            for meal_name in ["breakfast", "lunch", "dinner", "snacks"]:
                items = getattr(day, meal_name)
                for item in items:
                    item.branded_product = ingredient_brand_map.get(item.name)

        for grocery in grocery_list:
            grocery.branded_product = ingredient_brand_map.get(grocery.ingredient)

        # Keep top-level suggestions for API compatibility and future use.
        brands = list(ingredient_brand_map.values())
        if not brands:
            try:
                brands = await asyncio.wait_for(
                    recommend_brands(profile.country_code, ["chicken breast", "oats"]), timeout=5.0
                )
            except Exception:
                brands = []

        return PlanResponse(
            profile=profile,
            summary=summary,
            weekly_meal_plan=weekly_plan,
            grocery_list=grocery_list,
            brand_suggestions=[b.model_dump() for b in brands],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to generate plan: {str(exc)}") from exc
