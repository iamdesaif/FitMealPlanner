import Foundation

@MainActor
final class DashboardViewModel: ObservableObject {
    enum DayMode: String, CaseIterable {
        case training = "Training"
        case rest = "Rest"
    }

    @Published var profile: UserProfile?
    @Published var plan: PlanResponse?
    @Published var selectedDayMode: DayMode = .training
    @Published var proteinCompliance: Double = 0.0
    @Published var carbsCompliance: Double = 0.0
    @Published var fatCompliance: Double = 0.0

    @Published var checkinPreviousWeight: Double = 71
    @Published var checkinCurrentWeight: Double = 70.5
    @Published var checkinWaistCm: Double = 82
    @Published var checkinResult: WeeklyCheckinResponse?

    private let apiClient = APIClient()

    func apply(_ response: PlanResponse, profile: UserProfile) {
        self.plan = response
        self.profile = profile
        self.checkinPreviousWeight = profile.weightKg
        self.checkinCurrentWeight = profile.weightKg
    }

    var selectedMacroTarget: MacroTargets? {
        guard let macros = plan?.macros else { return nil }
        return selectedDayMode == .training ? macros.trainingDay : macros.restDay
    }

    func updateCompliance(consumedProtein: Double, consumedCarbs: Double, consumedFat: Double) {
        guard let target = selectedMacroTarget else { return }
        proteinCompliance = min(1.5, consumedProtein / Double(max(target.proteinG, 1)))
        carbsCompliance = min(1.5, consumedCarbs / Double(max(target.carbsG, 1)))
        fatCompliance = min(1.5, consumedFat / Double(max(target.fatG, 1)))
    }

    func submitCheckin() async {
        guard let calorieTarget = plan?.calories.target else { return }
        do {
            checkinResult = try await apiClient.weeklyCheckin(
                previousWeightKg: checkinPreviousWeight,
                currentWeightKg: checkinCurrentWeight,
                previousCalorieTarget: calorieTarget,
                waistCm: checkinWaistCm
            )
        } catch {
            checkinResult = nil
        }
    }
}
