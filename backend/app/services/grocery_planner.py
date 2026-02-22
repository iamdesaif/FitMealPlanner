from collections import defaultdict
from app.domain.models import GroceryItem, MealItem, WeeklyMealPlan


PACKAGING_RULES = {
    "Oats": ("500g bag", 500),
    "Greek Yogurt": ("170g cup", 170),
    "Eggs": ("12-count carton", 12),
    "Chicken Breast": ("1kg pack", 1000),
    "Salmon": ("500g pack", 500),
    "Brown Rice": ("1kg bag", 1000),
    "Quinoa": ("500g bag", 500),
    "Lentils": ("500g bag", 500),
    "Almonds": ("250g bag", 250),
    "Olive Oil": ("500ml bottle", 500),
    "Broccoli": ("1 whole head", 1),
}


def _flatten(plan: WeeklyMealPlan) -> list[MealItem]:
    out: list[MealItem] = []
    for day in plan.days.values():
        out.extend(day.breakfast)
        out.extend(day.lunch)
        out.extend(day.dinner)
        out.extend(day.snacks)
    return out


def aggregate_grocery_list(plan: WeeklyMealPlan) -> list[GroceryItem]:
    counts = defaultdict(int)
    for item in _flatten(plan):
        counts[item.name] += 1

    groceries: list[GroceryItem] = []
    for ingredient, servings in sorted(counts.items()):
        packaging, unit_size = PACKAGING_RULES.get(ingredient, ("1 pack", 1))
        purchase_qty = max(1, round(servings / 7))
        groceries.append(
            GroceryItem(
                ingredient=ingredient,
                weekly_quantity=f"{servings} servings",
                suggested_packaging=packaging,
                suggested_purchase_qty=purchase_qty,
            )
        )
    return groceries
