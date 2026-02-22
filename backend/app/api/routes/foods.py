from fastapi import APIRouter, Query
from app.services.usda_service import load_seed_foods

router = APIRouter(prefix="/api/v1/foods", tags=["foods"])


@router.get("/seed")
def get_seed_foods(query: str | None = Query(default=None)) -> list[dict]:
    foods = load_seed_foods()
    if query:
        q = query.lower()
        foods = [f for f in foods if q in f["name"].lower()]
    return foods
