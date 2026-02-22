from typing import Any
import httpx
from app.core.config import settings


async def search_products(
    query: str,
    country_code: str,
    page_size: int = 10,
    store: str | None = None,
) -> list[dict[str, Any]]:
    url = f"{settings.openfoodfacts_base_url}/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
        "tagtype_0": "countries",
        "tag_contains_0": "contains",
        "tag_0": country_code.lower(),
    }
    if store:
        params["tagtype_1"] = "stores"
        params["tag_contains_1"] = "contains"
        params["tag_1"] = store.lower()
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()
    return payload.get("products", [])
