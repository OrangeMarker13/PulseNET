import numpy as np
from config import RESPONSE_THRESHOLD_MINUTES


def _value(item, key, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def calculate_distance_km(latitude_1, longitude_1, latitude_2, longitude_2):
    lat1, lat2 = np.radians([latitude_1, latitude_2])
    dlat = np.radians(latitude_2 - latitude_1)
    dlon = np.radians(longitude_2 - longitude_1)
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return float(2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1))))


def calculate_distance(latitude_1, longitude_1, latitude_2, longitude_2):
    return calculate_distance_km(latitude_1, longitude_1, latitude_2, longitude_2)


def build_distance_matrix(demand_zones, candidate_locations):
    if demand_zones is None or candidate_locations is None or len(demand_zones) == 0 or len(candidate_locations) == 0:
        return np.empty((0, 0))
    zones = demand_zones.to_dict("records") if hasattr(demand_zones, "to_dict") else demand_zones
    return np.array([
        [
            calculate_distance_km(
                _value(zone, "latitude"),
                _value(zone, "longitude"),
                _value(location, "latitude"),
                _value(location, "longitude")
            )
            for location in candidate_locations
        ]
        for zone in zones
    ])


def build_travel_cost_matrix(demand_zones, candidate_locations):
    return build_distance_matrix(demand_zones, candidate_locations)


def greedy_optimize(distance_matrix, demand_zones, candidate_locations, ambulance_count):
    if distance_matrix.size == 0 or not candidate_locations or ambulance_count <= 0:
        return []
    zones = demand_zones.to_dict("records") if hasattr(demand_zones, "to_dict") else demand_zones
    weights = np.array([max(float(_value(z, "predicted_demand", _value(z, "historical_demand", 0))), 0) for z in zones])
    selected = []
    remaining = set(range(len(candidate_locations)))
    count = min(ambulance_count, len(candidate_locations))

    for _ in range(count):
        best_index, best_score = None, float("inf")
        for index in remaining:
            choices = selected + [index]
            nearest = np.min(distance_matrix[:, choices], axis=1)
            score = float(np.sum(nearest * weights))
            if score < best_score:
                best_score, best_index = score, index
        if best_index is None:
            break
        selected.append(best_index)
        remaining.remove(best_index)

    return [candidate_locations[i] for i in selected]


def calculate_coverage(demand, travel_time, response_threshold=RESPONSE_THRESHOLD_MINUTES):
    if travel_time is None or travel_time > response_threshold:
        return 0.0
    return float(demand)


def evaluate_deployment(deployment, demand_zones, route_times=None, response_threshold=RESPONSE_THRESHOLD_MINUTES):
    if demand_zones is None or len(demand_zones) == 0:
        return {"total_demand": 0, "covered_demand": 0, "coverage_percentage": 0, "average_response_time": None}

    zones = demand_zones.to_dict("records") if hasattr(demand_zones, "to_dict") else demand_zones
    total_demand = sum(max(float(_value(z, "predicted_demand", 0)), 0) for z in zones)
    weighted_time = 0.0
    covered_demand = 0.0
    route_times = route_times or {}

    for zone in zones:
        demand = max(float(_value(zone, "predicted_demand", 0)), 0)
        best_time = None

        for facility in deployment or []:
            flat_key = (
                _value(facility, "latitude"),
                _value(facility, "longitude"),
                _value(zone, "latitude"),
                _value(zone, "longitude")
            )
            value = route_times.get(flat_key)

            if isinstance(value, dict):
                value = value.get("duration_minutes", value.get("travel_time"))
            if value is not None:
                try:
                    value = float(value)
                    if best_time is None or value < best_time:
                        best_time = value
                except (TypeError, ValueError):
                    pass

        if best_time is not None:
            weighted_time += demand * best_time
            covered_demand += calculate_coverage(demand, best_time, response_threshold)

    average_response_time = weighted_time / total_demand if total_demand > 0 and weighted_time > 0 else None
    coverage_percentage = covered_demand / total_demand * 100 if total_demand > 0 else 0

    return {
        "total_demand": total_demand,
        "covered_demand": covered_demand,
        "coverage_percentage": coverage_percentage,
        "average_response_time": average_response_time
    }


def create_optimization_problem(demand_zones, candidate_locations, ambulance_count, response_threshold=RESPONSE_THRESHOLD_MINUTES):
    if demand_zones is None or len(demand_zones) == 0 or not candidate_locations or ambulance_count <= 0:
        return None
    return {
        "demand_zones": demand_zones,
        "candidate_locations": candidate_locations,
        "ambulance_count": min(ambulance_count, len(candidate_locations)),
        "response_threshold": response_threshold,
        "cost_matrix": build_distance_matrix(demand_zones, candidate_locations)
    }


def calculate_baseline_score(demand_zones, baseline_locations, route_times=None, response_threshold=RESPONSE_THRESHOLD_MINUTES):
    return evaluate_deployment(baseline_locations, demand_zones, route_times, response_threshold)


def calculate_optimized_score(demand_zones, optimized_locations, route_times=None, response_threshold=RESPONSE_THRESHOLD_MINUTES):
    return evaluate_deployment(optimized_locations, demand_zones, route_times, response_threshold)


def compare_deployments(baseline, optimized):
    baseline_time = baseline.get("average_response_time")
    optimized_time = optimized.get("average_response_time")
    improvement = ((baseline_time - optimized_time) / baseline_time * 100) if baseline_time and optimized_time else 0

    return {
        "baseline_coverage": baseline.get("coverage_percentage", 0),
        "optimized_coverage": optimized.get("coverage_percentage", 0),
        "coverage_improvement": optimized.get("coverage_percentage", 0) - baseline.get("coverage_percentage", 0),
        "baseline_response_time": baseline_time,
        "optimized_response_time": optimized_time,
        "response_time_improvement": improvement
    }
