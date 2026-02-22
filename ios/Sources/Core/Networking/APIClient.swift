import Foundation

enum APIError: Error {
    case invalidURL
    case requestFailed
    case badStatus(Int)
    case decodeFailed(Error)
    case transport(Error)
}

extension APIError: LocalizedError {
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid API URL."
        case .requestFailed:
            return "Request failed."
        case .badStatus(let code):
            return "Server returned HTTP \(code)."
        case .decodeFailed(let error):
            return "Failed to decode server response: \(error.localizedDescription)"
        case .transport(let error):
            return "Network error: \(error.localizedDescription)"
        }
    }
}

private struct GenerateMealsRequestPayload: Codable {
    let plan: PlanPayload
}

private struct PlanPayload: Codable {
    let heightCm: Double
    let weightKg: Double
    let age: Int
    let gender: Gender
    let bodyFatPercent: Double
    let targetBodyFatPercent: Double
    let activityLevel: ActivityLevel
    let trainingDaysPerWeek: Int
    let timelineWeeks: Int
    let countryCode: String
    let preferredRetailers: [String]
    let goalMode: String

    enum CodingKeys: String, CodingKey {
        case heightCm = "height_cm"
        case weightKg = "weight_kg"
        case age
        case gender
        case bodyFatPercent = "body_fat_percent"
        case targetBodyFatPercent = "target_body_fat_percent"
        case activityLevel = "activity_level"
        case trainingDaysPerWeek = "training_days_per_week"
        case timelineWeeks = "timeline_weeks"
        case countryCode = "country_code"
        case preferredRetailers = "preferred_retailers"
        case goalMode = "goal_mode"
    }
}

private struct WeeklyCheckinPayload: Codable {
    let previousWeightKg: Double
    let currentWeightKg: Double
    let previousCalorieTarget: Int
    let waistCm: Double?

    enum CodingKeys: String, CodingKey {
        case previousWeightKg = "previous_weight_kg"
        case currentWeightKg = "current_weight_kg"
        case previousCalorieTarget = "previous_calorie_target"
        case waistCm = "waist_cm"
    }
}

final class APIClient {
    var baseURL = "http://127.0.0.1:8000"

    func generatePlan(profile: UserProfile) async throws -> PlanResponse {
        guard let url = URL(string: "\(baseURL)/generate-meals") else { throw APIError.invalidURL }

        let goalMode: String = profile.goal == .fat_loss ? "fat_loss" : "recomposition"
        let payload = GenerateMealsRequestPayload(
            plan: PlanPayload(
                heightCm: profile.heightCm,
                weightKg: profile.weightKg,
                age: profile.age,
                gender: profile.gender,
                bodyFatPercent: profile.bodyFatPercent,
                targetBodyFatPercent: profile.targetBodyFatPercent,
                activityLevel: profile.activityLevel,
                trainingDaysPerWeek: profile.trainingDaysPerWeek,
                timelineWeeks: profile.timelineWeeks,
                countryCode: profile.countryCode,
                preferredRetailers: ["aldi", "lidl", "tesco"],
                goalMode: goalMode
            )
        )

        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try JSONEncoder().encode(payload)

        let data = try await send(req)
        do {
            return try JSONDecoder().decode(PlanResponse.self, from: data)
        } catch {
            throw APIError.decodeFailed(error)
        }
    }

    func weeklyCheckin(previousWeightKg: Double, currentWeightKg: Double, previousCalorieTarget: Int, waistCm: Double?) async throws -> WeeklyCheckinResponse {
        guard let url = URL(string: "\(baseURL)/weekly-checkin") else { throw APIError.invalidURL }

        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try JSONEncoder().encode(
            WeeklyCheckinPayload(
                previousWeightKg: previousWeightKg,
                currentWeightKg: currentWeightKg,
                previousCalorieTarget: previousCalorieTarget,
                waistCm: waistCm
            )
        )

        let data = try await send(req)
        do {
            return try JSONDecoder().decode(WeeklyCheckinResponse.self, from: data)
        } catch {
            throw APIError.decodeFailed(error)
        }
    }

    private func send(_ req: URLRequest) async throws -> Data {
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await URLSession.shared.data(for: req)
        } catch {
            throw APIError.transport(error)
        }
        guard let http = response as? HTTPURLResponse else { throw APIError.requestFailed }
        guard (200...299).contains(http.statusCode) else { throw APIError.badStatus(http.statusCode) }
        return data
    }
}
