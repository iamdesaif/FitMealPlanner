import SwiftUI
import Charts

struct DashboardView: View {
    @ObservedObject var viewModel: DashboardViewModel
    @State private var showCheckin = false
    @State private var consumedProtein: Double = 0
    @State private var consumedCarbs: Double = 0
    @State private var consumedFat: Double = 0

    var body: some View {
        NavigationStack {
            if let plan = viewModel.plan, let profile = viewModel.profile {
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        MetricCard(title: "Current BF%", value: "\(String(format: "%.1f", profile.bodyFatPercent))%")
                        MetricCard(title: "Target BF%", value: "\(String(format: "%.1f", profile.targetBodyFatPercent))%")
                        MetricCard(title: "Weeks To Goal", value: String(format: "%.1f", plan.projection.weeksToGoal))
                        MetricCard(title: "Fat Mass Remaining", value: "\(String(format: "%.2f", plan.bodyComposition.fatLossRequiredKg)) kg")

                        ProgressView(value: (profile.bodyFatPercent - profile.targetBodyFatPercent) <= 0 ? 1 : max(0, 1 - (plan.bodyComposition.fatLossRequiredKg / max(plan.bodyComposition.fatMassKg, 0.1))))
                        Text("Recomposition Progress")
                            .font(.caption)
                            .foregroundStyle(.secondary)

                        Picker("Day Type", selection: $viewModel.selectedDayMode) {
                            ForEach(DashboardViewModel.DayMode.allCases, id: \.self) { mode in
                                Text(mode.rawValue).tag(mode)
                            }
                        }
                        .pickerStyle(.segmented)

                        if let target = viewModel.selectedMacroTarget {
                            Text("Target: \(target.calories) kcal")
                            Chart {
                                BarMark(x: .value("Macro", "Protein"), y: .value("g", target.proteinG))
                                BarMark(x: .value("Macro", "Carbs"), y: .value("g", target.carbsG))
                                BarMark(x: .value("Macro", "Fat"), y: .value("g", target.fatG))
                            }
                            .frame(height: 220)

                            GroupBox("Macro Compliance Tracker") {
                                VStack(alignment: .leading, spacing: 10) {
                                    Slider(value: $consumedProtein, in: 0...Double(max(target.proteinG * 2, 1)), step: 1) {
                                        Text("Protein")
                                    }
                                    Text("Protein consumed: \(Int(consumedProtein))g")
                                    ProgressView(value: viewModel.proteinCompliance)

                                    Slider(value: $consumedCarbs, in: 0...Double(max(target.carbsG * 2, 1)), step: 1) {
                                        Text("Carbs")
                                    }
                                    Text("Carbs consumed: \(Int(consumedCarbs))g")
                                    ProgressView(value: viewModel.carbsCompliance)

                                    Slider(value: $consumedFat, in: 0...Double(max(target.fatG * 2, 1)), step: 1) {
                                        Text("Fat")
                                    }
                                    Text("Fat consumed: \(Int(consumedFat))g")
                                    ProgressView(value: viewModel.fatCompliance)
                                }
                                .onChange(of: consumedProtein) { _, _ in
                                    viewModel.updateCompliance(consumedProtein: consumedProtein, consumedCarbs: consumedCarbs, consumedFat: consumedFat)
                                }
                                .onChange(of: consumedCarbs) { _, _ in
                                    viewModel.updateCompliance(consumedProtein: consumedProtein, consumedCarbs: consumedCarbs, consumedFat: consumedFat)
                                }
                                .onChange(of: consumedFat) { _, _ in
                                    viewModel.updateCompliance(consumedProtein: consumedProtein, consumedCarbs: consumedCarbs, consumedFat: consumedFat)
                                }
                            }
                        }

                        Button("Weekly Check-In") {
                            showCheckin = true
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding()
                }
                .navigationTitle("Dashboard")
                .sheet(isPresented: $showCheckin) {
                    WeeklyCheckinSheet(viewModel: viewModel)
                }
            } else {
                ContentUnavailableView("No Plan Yet", systemImage: "chart.pie", description: Text("Complete onboarding to calculate macros."))
            }
        }
    }
}

private struct WeeklyCheckinSheet: View {
    @ObservedObject var viewModel: DashboardViewModel
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Form {
                Stepper(value: $viewModel.checkinPreviousWeight, in: 35...300, step: 0.1) {
                    Text("Previous Weight: \(String(format: "%.1f", viewModel.checkinPreviousWeight)) kg")
                }
                Stepper(value: $viewModel.checkinCurrentWeight, in: 35...300, step: 0.1) {
                    Text("Current Weight: \(String(format: "%.1f", viewModel.checkinCurrentWeight)) kg")
                }
                Stepper(value: $viewModel.checkinWaistCm, in: 40...200, step: 0.5) {
                    Text("Waist (optional): \(String(format: "%.1f", viewModel.checkinWaistCm)) cm")
                }

                Button("Submit Check-In") {
                    Task { await viewModel.submitCheckin() }
                }

                if let result = viewModel.checkinResult {
                    Text("Change: \(String(format: "%.2f", result.weeklyChangePercent))%")
                    Text("Adjustment: \(result.adjustmentKcal) kcal")
                    Text("New target: \(result.newCalorieTarget) kcal")
                    Text(result.note).foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Weekly Check-In")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}
