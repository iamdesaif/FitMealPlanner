import Foundation

enum HeightUnit: String, CaseIterable {
    case cm, `in`
}

enum WeightUnit: String, CaseIterable {
    case kg, lb
}

enum Gender: String, CaseIterable, Codable {
    case male, female
}

enum ActivityLevel: String, CaseIterable, Codable {
    case sedentary, light, moderate, high, athlete
}

enum Goal: String, CaseIterable, Codable {
    case muscle_gain, fat_loss, recomposition
}

enum DietaryPreference: String, CaseIterable, Codable {
    case none, vegetarian, vegan, high_protein, low_carb
}

struct UserProfile: Codable {
    var heightCm: Double
    var weightKg: Double
    var age: Int
    var gender: Gender
    var bodyFatPercent: Double
    var targetBodyFatPercent: Double
    var activityLevel: ActivityLevel
    var goal: Goal
    var timelineWeeks: Int
    var trainingDaysPerWeek: Int
    var countryCode: String
    var dietaryPreference: DietaryPreference

    enum CodingKeys: String, CodingKey {
        case heightCm = "height_cm"
        case weightKg = "weight_kg"
        case age
        case gender
        case bodyFatPercent = "body_fat_percent"
        case targetBodyFatPercent = "target_body_fat_percent"
        case activityLevel = "activity_level"
        case goal
        case timelineWeeks = "timeline_weeks"
        case trainingDaysPerWeek = "training_days_per_week"
        case countryCode = "country_code"
        case dietaryPreference = "dietary_preference"
    }
}

struct MacroTargets: Codable {
    let calories: Int
    let proteinG: Int
    let carbsG: Int
    let fatG: Int
    let fiberG: Int

    enum CodingKeys: String, CodingKey {
        case calories
        case proteinG = "protein_g"
        case carbsG = "carbs_g"
        case fatG = "fat_g"
        case fiberG = "fiber_g"
    }
}

struct BodyComposition: Codable {
    let leanBodyMassKg: Double
    let fatMassKg: Double
    let targetWeightKg: Double
    let fatLossRequiredKg: Double

    enum CodingKeys: String, CodingKey {
        case leanBodyMassKg = "lean_body_mass_kg"
        case fatMassKg = "fat_mass_kg"
        case targetWeightKg = "target_weight_kg"
        case fatLossRequiredKg = "fat_loss_required_kg"
    }
}

struct CaloriesPlan: Codable {
    let bmr: Int
    let tdee: Int
    let dailyDeficit: Int
    let target: Int
    let trainingDay: Int
    let restDay: Int

    enum CodingKeys: String, CodingKey {
        case bmr, tdee, target
        case dailyDeficit = "daily_deficit"
        case trainingDay = "training_day"
        case restDay = "rest_day"
    }
}

struct MacroPlan: Codable {
    let baseline: MacroTargets
    let trainingDay: MacroTargets
    let restDay: MacroTargets

    enum CodingKeys: String, CodingKey {
        case baseline
        case trainingDay = "training_day"
        case restDay = "rest_day"
    }
}

struct WeeklyWeightTarget: Codable, Identifiable {
    var id: Int { week }
    let week: Int
    let expectedWeightKg: Double

    enum CodingKeys: String, CodingKey {
        case week
        case expectedWeightKg = "expected_weight_kg"
    }
}

struct Projection: Codable {
    let weeksToGoal: Double
    let weeklyLossKg: Double
    let weeklyWeightTargets: [WeeklyWeightTarget]

    enum CodingKeys: String, CodingKey {
        case weeksToGoal = "weeks_to_goal"
        case weeklyLossKg = "weekly_loss_kg"
        case weeklyWeightTargets = "weekly_weight_targets"
    }
}

struct IngredientAllocation: Codable, Identifiable {
    var id: String { ingredient + "-\(grams)" }
    let ingredient: String
    let grams: Int
    let brandHint: String?
    let retailProduct: RetailProduct?

    enum CodingKeys: String, CodingKey {
        case ingredient, grams
        case brandHint = "brand_hint"
        case retailProduct = "retail_product"
    }
}

struct MealEntry: Codable, Identifiable {
    var id: String { name }
    let name: String
    let ingredients: [IngredientAllocation]
    let calories: Int
    let proteinG: Int
    let carbsG: Int
    let fatG: Int
    let fiberG: Int

    enum CodingKeys: String, CodingKey {
        case name, ingredients, calories
        case proteinG = "protein_g"
        case carbsG = "carbs_g"
        case fatG = "fat_g"
        case fiberG = "fiber_g"
    }
}

struct DayMealPlan: Codable, Identifiable {
    var id: String { day }
    let day: String
    let dayType: String
    let targetMacros: MacroTargets
    let meals: [MealEntry]
    let totals: MacroTargets

    enum CodingKeys: String, CodingKey {
        case day, meals, totals
        case dayType = "day_type"
        case targetMacros = "target_macros"
    }
}

struct WeeklyMealPlan: Codable {
    let days: [DayMealPlan]
}

struct GroceryItem: Codable, Identifiable {
    var id: String { ingredient }
    let ingredient: String
    let totalNeededG: Int
    let packageSizeG: Int
    let packagesToBuy: Int
    let leftoverG: Int
    let retailProduct: RetailProduct?

    enum CodingKeys: String, CodingKey {
        case ingredient
        case totalNeededG = "total_needed_g"
        case packageSizeG = "package_size_g"
        case packagesToBuy = "packages_to_buy"
        case leftoverG = "leftover_g"
        case retailProduct = "retail_product"
    }
}

struct BrandSuggestion: Codable, Identifiable {
    var id: String { brand + productName }
    let brand: String
    let productName: String
    let macrosPer100g: [String: Double]
    let estimatedPrice: String?

    enum CodingKeys: String, CodingKey {
        case brand
        case productName = "product_name"
        case macrosPer100g = "macros_per_100g"
        case estimatedPrice = "estimated_price"
    }
}

struct RetailProduct: Codable {
    let productName: String
    let brand: String
    let retailer: String?
    let nutrimentsPer100g: [String: Double]
    let nutriscoreGrade: String?
    let estimatedPrice: String?
    let source: String

    enum CodingKeys: String, CodingKey {
        case productName = "product_name"
        case brand
        case retailer
        case nutrimentsPer100g = "nutriments_per_100g"
        case nutriscoreGrade = "nutriscore_grade"
        case estimatedPrice = "estimated_price"
        case source
    }
}

struct PlanResponse: Codable {
    let bodyComposition: BodyComposition
    let calories: CaloriesPlan
    let macros: MacroPlan
    let projection: Projection
    let mealPlan: WeeklyMealPlan
    let groceryList: [GroceryItem]

    enum CodingKeys: String, CodingKey {
        case bodyComposition = "body_composition"
        case calories
        case macros
        case projection
        case mealPlan = "meal_plan"
        case groceryList = "grocery_list"
    }
}

struct WeeklyCheckinResponse: Codable {
    let weeklyChangePercent: Double
    let adjustmentKcal: Int
    let newCalorieTarget: Int
    let note: String

    enum CodingKeys: String, CodingKey {
        case weeklyChangePercent = "weekly_change_percent"
        case adjustmentKcal = "adjustment_kcal"
        case newCalorieTarget = "new_calorie_target"
        case note
    }
}
