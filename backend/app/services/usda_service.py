import json
from pathlib import Path
from typing import Any


def load_seed_foods() -> list[dict[str, Any]]:
    # Seed values aligned to USDA-style nutrient fields for deterministic MVP behavior.
    file_path = Path(__file__).resolve().parent.parent / "data" / "usda_seed_foods.json"
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)
