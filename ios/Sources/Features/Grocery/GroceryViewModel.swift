import Foundation

@MainActor
final class GroceryViewModel: ObservableObject {
    @Published var items: [GroceryItem] = []

    func apply(_ items: [GroceryItem]) {
        self.items = items
    }
}
