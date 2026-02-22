import Foundation

@MainActor
final class AppViewModel: ObservableObject {
    let onboardingVM = OnboardingViewModel()
    let dashboardVM = DashboardViewModel()
    let mealPlanVM = MealPlanViewModel()
    let groceryVM = GroceryViewModel()

    private let apiClient = APIClient()

    func bootstrap() async {
        onboardingVM.onPlanGenerated = { [weak self] payload in
            guard let self else { return }
            self.dashboardVM.apply(payload, profile: self.onboardingVM.profile)
            self.mealPlanVM.apply(payload.mealPlan.days)
            self.groceryVM.apply(payload.groceryList)
        }
        onboardingVM.apiClient = apiClient
    }
}
