import SwiftUI
import SwiftData

@main
struct FitPlannerApp: App {
    var body: some Scene {
        WindowGroup {
            RootView()
        }
        .modelContainer(for: [UserProfileEntity.self, ProgressLogEntity.self])
    }
}
