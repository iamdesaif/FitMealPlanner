import SwiftUI

struct RootView: View {
    @StateObject private var vm = AppViewModel()

    var body: some View {
        TabView {
            OnboardingView(viewModel: vm.onboardingVM)
                .tabItem { Label("Profile", systemImage: "person.text.rectangle") }

            DashboardView(viewModel: vm.dashboardVM)
                .tabItem { Label("Dashboard", systemImage: "chart.pie") }

            MealPlanView(viewModel: vm.mealPlanVM)
                .tabItem { Label("Meals", systemImage: "fork.knife") }

            GroceryView(viewModel: vm.groceryVM)
                .tabItem { Label("Grocery", systemImage: "cart") }
        }
        .task { await vm.bootstrap() }
    }
}
