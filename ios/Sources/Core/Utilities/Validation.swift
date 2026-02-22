import Foundation

struct FormValidator {
    static func validate(profile: UserProfile) -> String? {
        guard (90...250).contains(profile.heightCm) else { return "Height must be between 90-250 cm." }
        guard (30...300).contains(profile.weightKg) else { return "Weight must be between 30-300 kg." }
        guard (14...90).contains(profile.age) else { return "Age must be between 14-90." }
        guard (3...70).contains(profile.bodyFatPercent) else { return "Body fat must be between 3-70%." }
        guard (3...70).contains(profile.targetBodyFatPercent) else { return "Target body fat must be between 3-70%." }
        guard profile.targetBodyFatPercent <= profile.bodyFatPercent else { return "Target body fat should be less than or equal to current body fat." }
        guard (0...7).contains(profile.trainingDaysPerWeek) else { return "Training days must be between 0-7." }
        guard profile.countryCode.count == 2 else { return "Country code must be 2 letters." }
        return nil
    }
}
