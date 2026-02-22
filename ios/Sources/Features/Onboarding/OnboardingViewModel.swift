import Foundation

@MainActor
final class OnboardingViewModel: ObservableObject {
    @Published var profile = UserProfile(
        heightCm: 171,
        weightKg: 71,
        age: 31,
        gender: .male,
        bodyFatPercent: 18,
        targetBodyFatPercent: 15,
        activityLevel: .moderate,
        goal: .recomposition,
        timelineWeeks: 16,
        trainingDaysPerWeek: 4,
        countryCode: "US",
        dietaryPreference: .none
    )
    @Published var errorMessage: String?
    @Published var isLoading = false
    @Published var heightUnit: HeightUnit = .cm
    @Published var weightUnit: WeightUnit = .kg

    var apiClient: APIClient?
    var onPlanGenerated: ((PlanResponse) -> Void)?

    var displayHeight: Double {
        get { heightUnit == .cm ? profile.heightCm : profile.heightCm / 2.54 }
        set { profile.heightCm = heightUnit == .cm ? newValue : (newValue * 2.54) }
    }

    var displayWeight: Double {
        get { weightUnit == .kg ? profile.weightKg : profile.weightKg * 2.20462 }
        set { profile.weightKg = weightUnit == .kg ? newValue : (newValue / 2.20462) }
    }

    func submit() async {
        profile.countryCode = profile.countryCode.uppercased()
        if let validationError = FormValidator.validate(profile: profile) {
            errorMessage = validationError
            return
        }
        guard let apiClient else {
            errorMessage = "API client unavailable."
            return
        }

        isLoading = true
        defer { isLoading = false }

        do {
            let payload = try await apiClient.generatePlan(profile: profile)
            errorMessage = nil
            onPlanGenerated?(payload)
        } catch {
            if let apiError = error as? LocalizedError, let message = apiError.errorDescription {
                errorMessage = message
            } else {
                errorMessage = "Failed to generate plan. Check backend URL and try again."
            }
        }
    }
}
