import Foundation
import SwiftData

@Model
final class UserProfileEntity {
    var createdAt: Date
    var payload: Data

    init(createdAt: Date = Date(), payload: Data) {
        self.createdAt = createdAt
        self.payload = payload
    }
}

@Model
final class ProgressLogEntity {
    var date: Date
    var weightKg: Double

    init(date: Date = Date(), weightKg: Double) {
        self.date = date
        self.weightKg = weightKg
    }
}
