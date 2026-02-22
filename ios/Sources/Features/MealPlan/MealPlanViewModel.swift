import Foundation

@MainActor
final class MealPlanViewModel: ObservableObject {
    @Published var days: [DayMealPlan] = []

    func apply(_ payload: [DayMealPlan]) {
        days = payload
    }
}
