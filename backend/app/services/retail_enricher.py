import asyncio
from typing import Iterable

from app.clients.openfoodfacts_client import search_products
from app.domain.recomp_models import GroceryItem, RetailProduct, WeeklyMealPlan


def _as_float(value: object) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _extract_price(product: dict) -> str | None:
    price = product.get("price")
    if price:
        return str(price)
    if product.get("price_currency") and product.get("price"):
        return f"{product.get('price')} {product.get('price_currency')}"
    stores = product.get("stores")
    if isinstance(stores, str) and stores.strip():
        return None
    return None


def _stores_text(product: dict) -> str:
    stores = product.get("stores") or ""
    stores_tags = product.get("stores_tags") or []
    text = f"{stores} {' '.join(stores_tags)}".lower()
    return text


def _build_retail_product(product: dict, preferred_retailers: list[str]) -> RetailProduct:
    nutriments = product.get("nutriments", {})
    retailer = None
    stores_text = _stores_text(product)
    for r in preferred_retailers:
        if r.lower() in stores_text:
            retailer = r
            break

    return RetailProduct(
        product_name=product.get("product_name") or "Unknown Product",
        brand=product.get("brands") or "Unknown Brand",
        retailer=retailer,
        nutriments_per_100g={
            "protein_g": _as_float(nutriments.get("proteins_100g")),
            "carbs_g": _as_float(nutriments.get("carbohydrates_100g")),
            "fat_g": _as_float(nutriments.get("fat_100g")),
            "kcal": _as_float(nutriments.get("energy-kcal_100g")),
        },
        nutriscore_grade=(product.get("nutriscore_grade") or None),
        estimated_price=_extract_price(product),
    )


def _score_product(product: dict, preferred_retailers: list[str]) -> tuple[int, int, int]:
    stores_text = _stores_text(product)
    retailer_hit = 1 if any(r.lower() in stores_text for r in preferred_retailers) else 0

    nutri = (product.get("nutriscore_grade") or "z").lower()
    nutri_rank = {"a": 5, "b": 4, "c": 3, "d": 2, "e": 1}.get(nutri, 0)

    has_price = 1 if product.get("price") else 0
    return (retailer_hit, nutri_rank, has_price)


async def _match_ingredient(
    ingredient: str,
    country_code: str,
    preferred_retailers: list[str],
) -> RetailProduct | None:
    candidates = await search_products(ingredient, country_code=country_code, page_size=25)
    if not candidates:
        return None

    candidates_sorted = sorted(
        candidates,
        key=lambda p: _score_product(p, preferred_retailers),
        reverse=True,
    )
    best = candidates_sorted[0]
    return _build_retail_product(best, preferred_retailers)


def _all_ingredients(weekly_plan: WeeklyMealPlan, grocery_list: list[GroceryItem]) -> list[str]:
    names: set[str] = set()
    for day in weekly_plan.days:
        for meal in day.meals:
            for ing in meal.ingredients:
                names.add(ing.ingredient)
    for g in grocery_list:
        names.add(g.ingredient)
    return sorted(names)


async def enrich_with_retail_products(
    weekly_plan: WeeklyMealPlan,
    grocery_list: list[GroceryItem],
    country_code: str,
    preferred_retailers: Iterable[str],
) -> tuple[WeeklyMealPlan, list[GroceryItem]]:
    retailers = [r.strip().lower() for r in preferred_retailers if r and r.strip()]
    if not retailers:
        retailers = ["aldi", "lidl", "tesco"]

    ingredient_names = _all_ingredients(weekly_plan, grocery_list)

    semaphore = asyncio.Semaphore(5)

    async def bounded(name: str) -> tuple[str, RetailProduct | None]:
        async with semaphore:
            try:
                product = await asyncio.wait_for(
                    _match_ingredient(name, country_code=country_code, preferred_retailers=retailers),
                    timeout=4.0,
                )
                return name, product
            except Exception:
                return name, None

    mapped = dict(await asyncio.gather(*(bounded(n) for n in ingredient_names)))

    for day in weekly_plan.days:
        for meal in day.meals:
            for ing in meal.ingredients:
                ing.retail_product = mapped.get(ing.ingredient)

    for g in grocery_list:
        g.retail_product = mapped.get(g.ingredient)

    return weekly_plan, grocery_list
