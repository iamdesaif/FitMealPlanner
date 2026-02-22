import json
from collections import defaultdict
from pathlib import Path

from app.domain.recomp_models import (
    DayMealPlan,
    IngredientAllocation,
    MacroPlan,
    MacroTargets,
    Meal,
    PlanInput,
    WeeklyMealPlan,
)

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _load_catalog() -> list[dict]:
    path = Path(__file__).resolve().parent.parent / "data" / "food_catalog.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _group_by_category(catalog: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in catalog:
        grouped[item["category"]].append(item)
    return grouped


def _find_food(catalog: list[dict], name: str) -> dict | None:
    for item in catalog:
        if item["name"].lower() == name.lower():
            return item
    return None


def _macros_for_grams(food: dict, grams: float) -> dict[str, float]:
    factor = grams / 100.0
    return {
        "kcal": food["kcal"] * factor,
        "protein_g": food["protein_g"] * factor,
        "carbs_g": food["carbs_g"] * factor,
        "fat_g": food["fat_g"] * factor,
        "fiber_g": food["fiber_g"] * factor,
    }


def _build_meal(
    meal_name: str,
    protein_food: dict,
    carb_food: dict,
    micro_food: dict,
    fat_food: dict,
    protein_target: float,
    carbs_target: float,
    fat_target: float,
    extras: list[tuple[dict, float]] | None = None,
) -> Meal:
    protein_grams = max(90.0, (protein_target / max(protein_food["protein_g"], 1.0)) * 100)
    micro_grams = 120.0
    protein_macro = _macros_for_grams(protein_food, protein_grams)
    micro_macro = _macros_for_grams(micro_food, micro_grams)

    remaining_carbs = max(0.0, carbs_target - protein_macro["carbs_g"] - micro_macro["carbs_g"])
    remaining_fat = max(0.0, fat_target - protein_macro["fat_g"] - micro_macro["fat_g"])

    carb_grams = max(40.0, (remaining_carbs / max(carb_food["carbs_g"], 1.0)) * 100)
    fat_grams = max(0.0, (remaining_fat / max(fat_food["fat_g"], 1.0)) * 100)

    allocations = [
        (protein_food, protein_grams),
        (carb_food, carb_grams),
        (micro_food, micro_grams),
        (fat_food, fat_grams),
    ]
    if extras:
        allocations.extend(extras)

    total = {"kcal": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0}
    ingredients: list[IngredientAllocation] = []

    for food, grams in allocations:
        if grams < 1.0:
            continue
        m = _macros_for_grams(food, grams)
        for k in total:
            total[k] += m[k]
        ingredients.append(
            IngredientAllocation(
                ingredient=food["name"],
                grams=int(round(grams)),
                brand_hint=(food.get("brands") or [None])[0],
            )
        )

    return Meal(
        name=meal_name,
        ingredients=ingredients,
        calories=int(round(total["kcal"])),
        protein_g=int(round(total["protein_g"])),
        carbs_g=int(round(total["carbs_g"])),
        fat_g=int(round(total["fat_g"])),
        fiber_g=int(round(total["fiber_g"])),
    )


def _sum_meals(calories_target: int, meals: list[Meal], fiber_target: int) -> MacroTargets:
    return MacroTargets(
        calories=sum(m.calories for m in meals),
        protein_g=sum(m.protein_g for m in meals),
        carbs_g=sum(m.carbs_g for m in meals),
        fat_g=sum(m.fat_g for m in meals),
        fiber_g=max(fiber_target, sum(m.fiber_g for m in meals)),
    )


def _rebalance_to_target(meals: list[Meal], target: MacroTargets) -> list[Meal]:
    # Tune only the snack meal for precise daily matching, keeping structure of core meals stable.
    snack = next((m for m in meals if m.name == "Snack"), None)
    if not snack:
        return meals

    total = _sum_meals(target.calories, meals, target.fiber_g)

    delta_protein = target.protein_g - total.protein_g
    delta_carbs = target.carbs_g - total.carbs_g
    delta_fat = target.fat_g - total.fat_g

    snack_protein = max(0, snack.protein_g + delta_protein)
    snack_carbs = max(0, snack.carbs_g + delta_carbs)
    snack_fat = max(0, snack.fat_g + delta_fat)
    snack_calories = max(0, snack.calories + (target.calories - total.calories))

    snack = snack.model_copy(
        update={
            "protein_g": int(round(snack_protein)),
            "carbs_g": int(round(snack_carbs)),
            "fat_g": int(round(snack_fat)),
            "calories": int(round(snack_calories)),
        }
    )

    return [snack if m.name == "Snack" else m for m in meals]


def generate_weekly_meal_plan(plan: PlanInput, macro_plan: MacroPlan) -> WeeklyMealPlan:
    catalog = _load_catalog()
    grouped = _group_by_category(catalog)

    protein_foods = grouped["protein"]
    lean_protein_foods = [p for p in protein_foods if p["fat_g"] <= 6]
    if not lean_protein_foods:
        lean_protein_foods = protein_foods
    carb_foods = grouped["carb"]
    lower_protein_carbs = [c for c in carb_foods if c["protein_g"] <= 8]
    if not lower_protein_carbs:
        lower_protein_carbs = carb_foods
    micro_foods = grouped["micronutrient"]
    beverages = grouped.get("beverage", [])
    fat_foods = grouped["fat"]
    oats_food = _find_food(catalog, "Oats")
    coffee_food = _find_food(catalog, "Black Coffee")
    eggs_food = _find_food(catalog, "Eggs")

    training_days = set(DAYS[: plan.training_days_per_week])
    weekly_days: list[DayMealPlan] = []

    protein_usage: dict[str, int] = defaultdict(int)

    for idx, day in enumerate(DAYS):
        day_type = "training" if day in training_days else "rest"
        day_target = macro_plan.training_day if day_type == "training" else macro_plan.rest_day

        meal_count = 4
        protein_per_meal = max(25, int(round(day_target.protein_g / meal_count)))
        carbs_split = [0.22, 0.24, 0.22]
        fat_split = [0.10, 0.10, 0.08]

        day_meals: list[Meal] = []
        meal_names = ["Breakfast", "Lunch", "Dinner"]

        for meal_idx, meal_name in enumerate(meal_names):
            extra_allocations: list[tuple[dict, float]] = []
            if meal_idx == 0:
                # Breakfast preference: eggs + oats + black coffee, avoiding meat proteins in breakfast.
                breakfast_proteins = [
                    p for p in protein_foods if p["name"] in {"Eggs", "Greek Yogurt"}
                ]
                if not breakfast_proteins:
                    breakfast_proteins = lean_protein_foods
                protein_candidates = sorted(
                    breakfast_proteins,
                    key=lambda f: (protein_usage[f["name"]], f["fat_g"]),
                )
                protein_food = protein_candidates[idx % len(protein_candidates)]
                carb_food = oats_food if oats_food is not None else lower_protein_carbs[(idx + meal_idx) % len(lower_protein_carbs)]
                if coffee_food is None and beverages:
                    coffee_food = beverages[0]
                if coffee_food is not None:
                    extra_allocations.append((coffee_food, 240.0))
                breakfast_micros = [
                    m for m in micro_foods if m["name"] in {"Blueberries", "Apple", "Orange", "Pear", "Kiwi"}
                ]
                if breakfast_micros:
                    micro_food = breakfast_micros[idx % len(breakfast_micros)]
                else:
                    micro_food = micro_foods[(idx + meal_idx) % len(micro_foods)]
            else:
                protein_candidates = sorted(
                    lean_protein_foods,
                    key=lambda f: (protein_usage[f["name"]], f["fat_g"]),
                )
                protein_food = protein_candidates[(idx + meal_idx) % len(protein_candidates)]
                carb_food = lower_protein_carbs[(idx + meal_idx) % len(lower_protein_carbs)]
                micro_food = micro_foods[(idx + meal_idx) % len(micro_foods)]

            if protein_usage[protein_food["name"]] >= 3:
                protein_food = protein_candidates[0]
            protein_usage[protein_food["name"]] += 1

            fat_food = fat_foods[(idx + meal_idx) % len(fat_foods)]

            meal = _build_meal(
                meal_name=meal_name,
                protein_food=protein_food,
                carb_food=carb_food,
                micro_food=micro_food,
                fat_food=fat_food,
                protein_target=float(min(28, protein_per_meal)),
                carbs_target=float(day_target.carbs_g * carbs_split[meal_idx]),
                fat_target=float(day_target.fat_g * (0.06 if meal_idx == 0 else fat_split[meal_idx])),
                extras=extra_allocations,
            )
            day_meals.append(meal)

        core = _sum_meals(day_target.calories, day_meals, day_target.fiber_g)
        snack_protein_target = max(25.0, float(day_target.protein_g - core.protein_g))
        snack_carb_target = max(0.0, float(day_target.carbs_g - core.carbs_g))
        snack_fat_target = max(0.0, float(day_target.fat_g - core.fat_g))

        snack_protein_food = sorted(lean_protein_foods, key=lambda f: f["fat_g"])[0]
        snack = _build_meal(
            meal_name="Snack",
            protein_food=snack_protein_food,
            carb_food=lower_protein_carbs[(idx + 3) % len(lower_protein_carbs)],
            micro_food=micro_foods[(idx + 3) % len(micro_foods)],
            fat_food=fat_foods[(idx + 3) % len(fat_foods)],
            protein_target=snack_protein_target,
            carbs_target=snack_carb_target,
            fat_target=snack_fat_target,
        )
        day_meals.append(snack)

        day_meals = _rebalance_to_target(day_meals, day_target)
        totals = _sum_meals(day_target.calories, day_meals, day_target.fiber_g)

        weekly_days.append(
            DayMealPlan(
                day=day,
                day_type=day_type,
                target_macros=day_target,
                meals=day_meals,
                totals=totals,
            )
        )

    return WeeklyMealPlan(days=weekly_days)
