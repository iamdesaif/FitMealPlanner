# FitPlanner Recomposition API (v2)

## POST `/calculate-plan`
Computes physiology outputs only.

### Request
```json
{
  "height_cm": 171,
  "weight_kg": 71,
  "age": 31,
  "gender": "male",
  "body_fat_percent": 18,
  "target_body_fat_percent": 12,
  "activity_level": "moderate",
  "training_days_per_week": 4,
  "goal_mode": "recomposition"
}
```

### Response sections
- `body_composition`
- `calories`
- `macros`
- `projection`

## POST `/generate-meals`
Computes plan + algorithmic weekly meals + precise grocery list.

### Request
```json
{
  "plan": {
    "height_cm": 171,
    "weight_kg": 71,
    "age": 31,
    "gender": "male",
    "body_fat_percent": 18,
    "target_body_fat_percent": 12,
    "activity_level": "moderate",
    "training_days_per_week": 4,
    "country_code": "DE",
    "preferred_retailers": ["aldi", "lidl", "tesco"],
    "goal_mode": "recomposition"
  }
}
```

### Response sections
- `body_composition`
- `calories` (`tdee`, `target`, `training_day`, `rest_day`)
- `macros` (`baseline`, `training_day`, `rest_day`)
- `projection` (`weeks_to_goal`, `weekly_weight_targets`)
- `meal_plan` (`days[]` with per-meal ingredient grams)
- `grocery_list` (exact grams, package sizing, leftovers)
- Each ingredient and grocery item can include `retail_product` with:
  - `product_name`, `brand`, `retailer`, `nutriments_per_100g`, `nutriscore_grade`, `estimated_price`

## POST `/weekly-checkin`
Adaptive engine for weekly calorie adjustment.

### Request
```json
{
  "previous_weight_kg": 71,
  "current_weight_kg": 70.7,
  "previous_calorie_target": 2200,
  "waist_cm": 82.0
}
```

### Rules
- loss `<0.3%` -> `-100 kcal`
- loss `>1.2%` -> `+100 kcal`
- otherwise unchanged

## GET `/projection`
Query projection-only data using query params.
