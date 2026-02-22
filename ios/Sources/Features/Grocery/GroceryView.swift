import SwiftUI

struct GroceryView: View {
    @ObservedObject var viewModel: GroceryViewModel

    var body: some View {
        NavigationStack {
            List(viewModel.items) { item in
                VStack(alignment: .leading, spacing: 4) {
                    Text(item.ingredient).font(.headline)
                    Text("Need: \(item.totalNeededG)g")
                    Text("Pack size: \(item.packageSizeG)g")
                    Text("Buy: \(item.packagesToBuy) packs")
                    Text("Leftover est.: \(item.leftoverG)g")
                        .foregroundStyle(.secondary)
                    if let rp = item.retailProduct {
                        Text("Product: \(rp.brand) - \(rp.productName)\(rp.retailer != nil ? " (\(rp.retailer!))" : "")")
                            .font(.caption)
                        let nutri = rp.nutriscoreGrade?.uppercased() ?? "N/A"
                        Text("Nutri-Score: \(nutri)\(rp.estimatedPrice != nil ? " | Price: \(rp.estimatedPrice!)" : "")")
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Grocery List")
        }
    }
}
