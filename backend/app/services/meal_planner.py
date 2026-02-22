from dataclasses import dataclass
from app.domain.models import DailyMealPlan, DietaryPreference, Goal, MacroTargets, MealItem, WeeklyMealPlan


@dataclass
class FoodTemplate:
    name: str
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    vegan: bool = False
    vegetarian: bool = False


WHOLE_FOOD_LIBRARY = [
    FoodTemplate("Oats", 150, 5, 27, 3, vegan=True, vegetarian=True),
    FoodTemplate("Greek Yogurt", 140, 20, 6, 2, vegetarian=True),
    FoodTemplate("Eggs", 140, 12, 1, 10, vegetarian=True),
    FoodTemplate("Chicken Breast", 180, 34, 0, 4),
    FoodTemplate("Salmon", 220, 28, 0, 12),
    FoodTemplate("Brown Rice", 180, 4, 38, 1, vegan=True, vegetarian=True),
    FoodTemplate("Quinoa", 170, 6, 30, 3, vegan=True, vegetarian=True),
    FoodTemplate("Lentils", 180, 13, 30, 1, vegan=True, vegetarian=True),
    FoodTemplate("Almonds", 170, 6, 6, 15, vegan=True, vegetarian=True),
    FoodTemplate("Olive Oil", 120, 0, 0, 14, vegan=True, vegetarian=True),
    FoodTemplate("Broccoli", 50, 4, 10, 0, vegan=True, vegetarian=True),
]


def _filter_foods(preference: DietaryPreference) -> list[FoodTemplate]:
    if preference == DietaryPreference.vegan:
        return [f for f in WHOLE_FOOD_LIBRARY if f.vegan]
    if preference == DietaryPreference.vegetarian:
        return [f for f in WHOLE_FOOD_LIBRARY if f.vegetarian or f.vegan]
    return WHOLE_FOOD_LIBRARY


def _build_meal(name: str, foods: list[FoodTemplate], target_calories: int, target_protein: int) -> list[MealItem]:
    meal_items: list[MealItem] = []
    running_calories = 0
    running_protein = 0

    for food in foods:
        if running_calories >= target_calories * 0.95 and running_protein >= target_protein * 0.9:
            break
        meal_items.append(
            MealItem(
                name=food.name,
                quantity="1 serving",
                calories=food.calories,
                protein_g=food.protein_g,
                carbs_g=food.carbs_g,
                fat_g=food.fat_g,
            )
        )
        running_calories += food.calories
        running_protein += food.protein_g
    return meal_items


def _sum(items: list[MealItem]) -> MacroTargets:
    return MacroTargets(
        calories=sum(i.calories for i in items),
        protein_g=sum(i.protein_g for i in items),
        carbs_g=sum(i.carbs_g for i in items),
        fat_g=sum(i.fat_g for i in items),
    )


def generate_daily_plan(daily_target: MacroTargets, preference: DietaryPreference, goal: Goal) -> DailyMealPlan:
    foods = _filter_foods(preference)

    if preference == DietaryPreference.low_carb:
        foods = sorted(foods, key=lambda x: x.carbs_g)
    elif preference == DietaryPreference.high_protein or goal == Goal.muscle_gain:
        foods = sorted(foods, key=lambda x: x.protein_g, reverse=True)

    meals = {
        "breakfast": _build_meal("Breakfast", foods, int(daily_target.calories * 0.25), int(daily_target.protein_g * 0.25)),
        "lunch": _build_meal("Lunch", foods, int(daily_target.calories * 0.30), int(daily_target.protein_g * 0.25)),
        "dinner": _build_meal("Dinner", foods, int(daily_target.calories * 0.30), int(daily_target.protein_g * 0.25)),
        "snacks": _build_meal("Snacks", foods, int(daily_target.calories * 0.15), int(daily_target.protein_g * 0.25)),
    }

    all_items = meals["breakfast"] + meals["lunch"] + meals["dinner"] + meals["snacks"]
    total = _sum(all_items)

    # Rebalance calorie drift to keep plan inside target ±5%
    if total.calories > int(daily_target.calories * 1.05):
        meals["snacks"] = meals["snacks"][0:1]
        all_items = meals["breakfast"] + meals["lunch"] + meals["dinner"] + meals["snacks"]
        total = _sum(all_items)

    return DailyMealPlan(
        breakfast=meals["breakfast"],
        lunch=meals["lunch"],
        dinner=meals["dinner"],
        snacks=meals["snacks"],
        total=total,
    )


def _rotate(items: list[MealItem], shift: int) -> list[MealItem]:
    if not items:
        return items
    s = shift % len(items)
    return items[s:] + items[:s]


def generate_weekly_plan(daily_target: MacroTargets, preference: DietaryPreference, goal: Goal) -> WeeklyMealPlan:
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    base = generate_daily_plan(daily_target, preference, goal)
    days: dict[str, DailyMealPlan] = {}

    for idx, day in enumerate(day_names):
        # Rotate meal item order through the week to avoid identical day presentation.
        days[day] = DailyMealPlan(
            breakfast=_rotate(base.breakfast, idx),
            lunch=_rotate(base.lunch, idx + 1),
            dinner=_rotate(base.dinner, idx + 2),
            snacks=_rotate(base.snacks, idx),
            total=base.total,
        )

    return WeeklyMealPlan(days=days)
