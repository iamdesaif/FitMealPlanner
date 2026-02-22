from app.clients.openfoodfacts_client import search_products
from app.domain.models import BrandSuggestion


def _is_whole_food_friendly(product: dict) -> bool:
    name = (product.get("product_name") or "").lower()
    if any(word in name for word in ["breaded", "nugget", "fried", "chips", "cookie", "soda"]):
        return False
    nova = product.get("nutriscore_grade") or ""
    # Keep better-scoring options where available, but do not hard-fail missing grades.
    return nova in {"", "a", "b"}


def _health_rating(product: dict) -> str:
    grade = (product.get("nutriscore_grade") or "").lower()
    if grade in {"a", "b"}:
        return f"Good ({grade.upper()})"
    if grade in {"c"}:
        return "Moderate (C)"
    if grade in {"d", "e"}:
        return f"Lower ({grade.upper()})"
    return "Unknown"


async def recommend_brands(country_code: str, keywords: list[str]) -> list[BrandSuggestion]:
    suggestions: list[BrandSuggestion] = []

    for keyword in keywords:
        products = await search_products(keyword, country_code)
        for p in products:
            if not _is_whole_food_friendly(p):
                continue
            nutriments = p.get("nutriments", {})
            suggestion = BrandSuggestion(
                brand=p.get("brands", "Unknown Brand"),
                product_name=p.get("product_name", keyword.title()),
                macros_per_100g={
                    "protein_g": float(nutriments.get("proteins_100g", 0.0) or 0.0),
                    "carbs_g": float(nutriments.get("carbohydrates_100g", 0.0) or 0.0),
                    "fat_g": float(nutriments.get("fat_100g", 0.0) or 0.0),
                    "kcal": float(nutriments.get("energy-kcal_100g", 0.0) or 0.0),
                },
                health_rating=_health_rating(p),
                estimated_price=p.get("price") or p.get("stores"),
            )
            suggestions.append(suggestion)
            if len(suggestions) >= 8:
                return suggestions
    return suggestions


async def recommend_brands_by_ingredient(country_code: str, ingredients: list[str]) -> dict[str, BrandSuggestion]:
    mapped: dict[str, BrandSuggestion] = {}
    for ingredient in ingredients:
        products = await search_products(ingredient, country_code, page_size=12)
        for p in products:
            if not _is_whole_food_friendly(p):
                continue
            nutriments = p.get("nutriments", {})
            mapped[ingredient] = BrandSuggestion(
                brand=p.get("brands", "Unknown Brand"),
                product_name=p.get("product_name", ingredient.title()),
                macros_per_100g={
                    "protein_g": float(nutriments.get("proteins_100g", 0.0) or 0.0),
                    "carbs_g": float(nutriments.get("carbohydrates_100g", 0.0) or 0.0),
                    "fat_g": float(nutriments.get("fat_100g", 0.0) or 0.0),
                    "kcal": float(nutriments.get("energy-kcal_100g", 0.0) or 0.0),
                },
                health_rating=_health_rating(p),
                estimated_price=p.get("price") or p.get("stores"),
            )
            break
    return mapped
