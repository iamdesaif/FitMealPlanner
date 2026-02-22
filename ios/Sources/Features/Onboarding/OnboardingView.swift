import SwiftUI

struct OnboardingView: View {
    @ObservedObject var viewModel: OnboardingViewModel

    var body: some View {
        NavigationStack {
            Form {
                Section("Body Metrics") {
                    Picker("Height Unit", selection: $viewModel.heightUnit) {
                        ForEach(HeightUnit.allCases, id: \.self) { Text($0.rawValue.uppercased()).tag($0) }
                    }
                    Stepper(
                        value: Binding(get: { viewModel.displayHeight }, set: { viewModel.displayHeight = $0 }),
                        in: viewModel.heightUnit == .cm ? 90...250 : 36...100,
                        step: 1
                    ) {
                        Text("Height: \(Int(viewModel.displayHeight)) \(viewModel.heightUnit.rawValue)")
                    }
                    Picker("Weight Unit", selection: $viewModel.weightUnit) {
                        ForEach(WeightUnit.allCases, id: \.self) { Text($0.rawValue.uppercased()).tag($0) }
                    }
                    Stepper(
                        value: Binding(get: { viewModel.displayWeight }, set: { viewModel.displayWeight = $0 }),
                        in: viewModel.weightUnit == .kg ? 30...300 : 66...660,
                        step: 1
                    ) {
                        Text("Weight: \(String(format: "%.1f", viewModel.displayWeight)) \(viewModel.weightUnit.rawValue)")
                    }
                    Stepper(value: $viewModel.profile.age, in: 14...90) { Text("Age: \(viewModel.profile.age)") }
                    Picker("Gender", selection: $viewModel.profile.gender) {
                        ForEach(Gender.allCases, id: \.self) { Text($0.rawValue.capitalized).tag($0) }
                    }
                    Stepper(value: $viewModel.profile.bodyFatPercent, in: 3...70, step: 0.5) {
                        Text("Body Fat: \(String(format: "%.1f", viewModel.profile.bodyFatPercent))%")
                    }
                }

                Section("Goals") {
                    Picker("Activity", selection: $viewModel.profile.activityLevel) {
                        ForEach(ActivityLevel.allCases, id: \.self) { Text($0.rawValue.capitalized).tag($0) }
                    }
                    Picker("Goal", selection: $viewModel.profile.goal) {
                        Text("Muscle Gain").tag(Goal.muscle_gain)
                        Text("Fat Loss").tag(Goal.fat_loss)
                        Text("Recomposition").tag(Goal.recomposition)
                    }
                    HStack {
                        Text("Target Body Fat")
                        Spacer()
                        Stepper(
                            value: $viewModel.profile.targetBodyFatPercent,
                            in: 3...70,
                            step: 0.5
                        ) {
                            Text("\(String(format: "%.1f", viewModel.profile.targetBodyFatPercent))%")
                                .monospacedDigit()
                        }
                        .fixedSize()
                    }
                    Stepper(value: $viewModel.profile.trainingDaysPerWeek, in: 0...7) {
                        Text("Training Days / Week: \(viewModel.profile.trainingDaysPerWeek)")
                    }
                    Picker("Timeline", selection: $viewModel.profile.timelineWeeks) {
                        Text("8 weeks").tag(8)
                        Text("16 weeks").tag(16)
                        Text("32 weeks").tag(32)
                    }
                    Picker("Diet", selection: $viewModel.profile.dietaryPreference) {
                        ForEach(DietaryPreference.allCases, id: \.self) { Text($0.rawValue.replacingOccurrences(of: "_", with: " ").capitalized).tag($0) }
                    }
                    TextField("Country Code", text: $viewModel.profile.countryCode)
                        .textInputAutocapitalization(.characters)
                }

                if let err = viewModel.errorMessage {
                    Text(err).foregroundStyle(.red)
                }

            }
            .navigationTitle("Onboarding")
            .navigationBarTitleDisplayMode(.inline)
            .scrollDismissesKeyboard(.interactively)
            .safeAreaInset(edge: .bottom) {
                Color.clear.frame(height: 92)
            }
            .overlay(alignment: .bottom) {
                VStack(spacing: 0) {
                    Divider()
                    Button(viewModel.isLoading ? "Generating..." : "Generate Plan") {
                        Task { await viewModel.submit() }
                    }
                    .buttonStyle(.borderedProminent)
                    .frame(maxWidth: .infinity)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(.ultraThinMaterial)
                }
            }
            .alert(
                "Unable to Generate Plan",
                isPresented: Binding(
                    get: { viewModel.errorMessage != nil },
                    set: { if !$0 { viewModel.errorMessage = nil } }
                )
            ) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage ?? "")
            }
        }
    }
}
