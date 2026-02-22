from enum import Enum
from pydantic import BaseModel, Field, model_validator


class Gender(str, Enum):
    male = "male"
    female = "female"


class GoalMode(str, Enum):
    fat_loss = "fat_loss"
    recomposition = "recomposition"


class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    high = "high"
    athlete = "athlete"


ACTIVITY_MULTIPLIERS = {
    ActivityLevel.sedentary: 1.2,
    ActivityLevel.light: 1.375,
    ActivityLevel.moderate: 1.55,
    ActivityLevel.high: 1.725,
    ActivityLevel.athlete: 1.9,
}


class PlanInput(BaseModel):
    height_cm: float = Field(gt=120, lt=230)
    weight_kg: float = Field(gt=35, lt=300)
    age: int = Field(ge=14, le=90)
    gender: Gender
    body_fat_percent: float = Field(ge=4, le=60)
    target_body_fat_percent: float = Field(ge=4, le=40)
    activity_level: ActivityLevel
    training_days_per_week: int = Field(ge=0, le=7)
    timeline_weeks: int = Field(default=16, ge=4, le=52)
    country_code: str = Field(default="DE", min_length=2, max_length=2)
    preferred_retailers: list[str] = Field(default_factory=lambda: ["aldi", "lidl", "tesco"])
    goal_mode: GoalMode = GoalMode.recomposition

    @model_validator(mode="after")
    def validate_targets(self) -> "PlanInput":
        if self.target_body_fat_percent >= self.body_fat_percent:
            raise ValueError("target_body_fat_percent must be lower than current body_fat_percent")
        return self


class MacroTargets(BaseModel):
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    fiber_g: int


class BodyComposition(BaseModel):
    lean_body_mass_kg: float
    fat_mass_kg: float
    target_weight_kg: float
    fat_loss_required_kg: float


class CaloriesPlan(BaseModel):
    bmr: int
    tdee: int
    daily_deficit: int
    target: int
    training_day: int
    rest_day: int


class MacroPlan(BaseModel):
    baseline: MacroTargets
    training_day: MacroTargets
    rest_day: MacroTargets


class WeeklyWeightTarget(BaseModel):
    week: int
    expected_weight_kg: float


class MonthlyMilestone(BaseModel):
    month: int
    expected_weight_kg: float


class Projection(BaseModel):
    weeks_to_goal: float
    weekly_loss_kg: float
    weekly_weight_targets: list[WeeklyWeightTarget]
    monthly_milestones: list[MonthlyMilestone]


class RetailProduct(BaseModel):
    product_name: str
    brand: str
    retailer: str | None = None
    nutriments_per_100g: dict[str, float]
    nutriscore_grade: str | None = None
    estimated_price: str | None = None
    source: str = "openfoodfacts"


class IngredientAllocation(BaseModel):
    ingredient: str
    grams: int
    brand_hint: str | None = None
    retail_product: RetailProduct | None = None


class Meal(BaseModel):
    name: str
    ingredients: list[IngredientAllocation]
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    fiber_g: int


class DayMealPlan(BaseModel):
    day: str
    day_type: str
    target_macros: MacroTargets
    meals: list[Meal]
    totals: MacroTargets


class WeeklyMealPlan(BaseModel):
    days: list[DayMealPlan]


class GroceryItem(BaseModel):
    ingredient: str
    total_needed_g: int
    package_size_g: int
    packages_to_buy: int
    leftover_g: int
    retail_product: RetailProduct | None = None


class CalculatePlanResponse(BaseModel):
    body_composition: BodyComposition
    calories: CaloriesPlan
    macros: MacroPlan
    projection: Projection


class GenerateMealsRequest(BaseModel):
    plan: PlanInput


class GenerateMealsResponse(BaseModel):
    body_composition: BodyComposition
    calories: CaloriesPlan
    macros: MacroPlan
    projection: Projection
    meal_plan: WeeklyMealPlan
    grocery_list: list[GroceryItem]


class WeeklyCheckinRequest(BaseModel):
    previous_weight_kg: float = Field(gt=35, lt=300)
    current_weight_kg: float = Field(gt=35, lt=300)
    previous_calorie_target: int = Field(ge=1000, le=6000)
    waist_cm: float | None = Field(default=None, ge=40, le=200)


class WeeklyCheckinResponse(BaseModel):
    weekly_change_percent: float
    adjustment_kcal: int
    new_calorie_target: int
    note: str
