import SwiftUI

struct BrandSuggestionsView: View {
    @ObservedObject var viewModel: BrandSuggestionsViewModel

    var body: some View {
        NavigationStack {
            List(viewModel.brands) { brand in
                VStack(alignment: .leading, spacing: 4) {
                    Text(brand.productName).font(.headline)
                    Text(brand.brand)
                    Text("Protein: \(Int(brand.macrosPer100g["protein_g"] ?? 0))g / 100g")
                    Text("Carbs: \(Int(brand.macrosPer100g["carbs_g"] ?? 0))g / 100g")
                    Text("Fat: \(Int(brand.macrosPer100g["fat_g"] ?? 0))g / 100g")
                    if let price = brand.estimatedPrice {
                        Text("Est. Price: \(price)")
                    }
                }
            }
            .navigationTitle("Brand Suggestions")
        }
    }
}
