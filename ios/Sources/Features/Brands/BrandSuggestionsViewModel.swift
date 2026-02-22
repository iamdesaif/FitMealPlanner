import Foundation

@MainActor
final class BrandSuggestionsViewModel: ObservableObject {
    @Published var brands: [BrandSuggestion] = []

    func apply(_ suggestions: [BrandSuggestion]) {
        brands = suggestions
    }
}
