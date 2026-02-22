from enum import Enum
from pydantic import BaseModel, Field, field_validator


class Gender(str, Enum):
    male = "male"
    female = "female"


class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    moderate = "moderate"
    active = "active"


class Goal(str, Enum):
    muscle_gain = "muscle_gain"
    fat_loss = "fat_loss"
    recomposition = "recomposition"


class TimelineWeeks(int, Enum):
    eight = 8
    sixteen = 16
    thirty_two = 32


class DietaryPreference(str, Enum):
    vegetarian = "vegetarian"
    vegan = "vegan"
    high_protein = "high_protein"
    low_carb = "low_carb"
    none = "none"


class UserProfile(BaseModel):
    height_cm: float = Field(gt=90, lt=250)
    weight_kg: float = Field(gt=30, lt=300)
    age: int = Field(ge=14, le=90)
    gender: Gender
    body_fat_percent: float = Field(ge=3, le=70)
    target_body_fat_percent: float | None = Field(default=None, ge=3, le=70)
    activity_level: ActivityLevel
    goal: Goal
    timeline_weeks: TimelineWeeks
    country_code: str = Field(min_length=2, max_length=2)
    dietary_preference: DietaryPreference = DietaryPreference.none

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str) -> str:
        return value.upper()


class MacroTargets(BaseModel):
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int


class NutritionSummary(BaseModel):
    bmi: float
    bmr: int
    tdee: int
    calorie_target: int
    daily_macros: MacroTargets
    weekly_macros: MacroTargets


class BrandedProduct(BaseModel):
    brand: str
    product_name: str
    macros_per_100g: dict[str, float]
    health_rating: str
    estimated_price: str | None


class MealItem(BaseModel):
    name: str
    quantity: str
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    branded_product: BrandedProduct | None = None


class DailyMealPlan(BaseModel):
    breakfast: list[MealItem]
    lunch: list[MealItem]
    dinner: list[MealItem]
    snacks: list[MealItem]
    total: MacroTargets


class WeeklyMealPlan(BaseModel):
    days: dict[str, DailyMealPlan]


class GroceryItem(BaseModel):
    ingredient: str
    weekly_quantity: str
    suggested_packaging: str
    suggested_purchase_qty: int
    branded_product: BrandedProduct | None = None


class BrandSuggestion(BrandedProduct):
    pass
