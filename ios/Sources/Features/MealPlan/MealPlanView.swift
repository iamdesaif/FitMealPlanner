import SwiftUI

struct MealPlanView: View {
    @ObservedObject var viewModel: MealPlanViewModel

    var body: some View {
        NavigationStack {
            List(viewModel.days) { day in
                Section("\(day.day.capitalized) (\(day.dayType.capitalized))") {
                    ForEach(day.meals) { meal in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(meal.name).font(.headline)
                            Text("P \(meal.proteinG)g  C \(meal.carbsG)g  F \(meal.fatG)g  Fiber \(meal.fiberG)g")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            ForEach(meal.ingredients) { ing in
                                VStack(alignment: .leading, spacing: 2) {
                                    Text("• \(ing.ingredient): \(ing.grams)g")
                                        .font(.caption)
                                    if let rp = ing.retailProduct {
                                        Text("  \(rp.brand) - \(rp.productName)\(rp.retailer != nil ? " (\(rp.retailer!))" : "")")
                                            .font(.caption2)
                                            .foregroundStyle(.secondary)
                                        let nutri = rp.nutriscoreGrade?.uppercased() ?? "N/A"
                                        Text("  Nutri-Score: \(nutri)\(rp.estimatedPrice != nil ? " | Price: \(rp.estimatedPrice!)" : "")")
                                            .font(.caption2)
                                            .foregroundStyle(.secondary)
                                    } else if let hint = ing.brandHint {
                                        Text("  Brand: \(hint)")
                                            .font(.caption2)
                                            .foregroundStyle(.secondary)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Weekly Meals")
        }
    }
}
