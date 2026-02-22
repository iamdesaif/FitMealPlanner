import json
import math
from collections import defaultdict
from pathlib import Path

from app.domain.recomp_models import GroceryItem, WeeklyMealPlan


def _package_sizes() -> dict[str, int]:
    path = Path(__file__).resolve().parent.parent / "data" / "food_catalog.json"
    with path.open("r", encoding="utf-8") as f:
        foods = json.load(f)
    return {f["name"]: int(f.get("package_g", 500)) for f in foods}


def build_grocery_list(weekly_plan: WeeklyMealPlan) -> list[GroceryItem]:
    package_sizes = _package_sizes()
    totals: dict[str, int] = defaultdict(int)

    for day in weekly_plan.days:
        for meal in day.meals:
            for ing in meal.ingredients:
                totals[ing.ingredient] += ing.grams

    out: list[GroceryItem] = []
    for ingredient, needed in sorted(totals.items()):
        package = package_sizes.get(ingredient, 500)
        packs = max(1, int(math.ceil(needed / package)))
        leftover = (packs * package) - needed
        out.append(
            GroceryItem(
                ingredient=ingredient,
                total_needed_g=needed,
                package_size_g=package,
                packages_to_buy=packs,
                leftover_g=leftover,
            )
        )
    return out
